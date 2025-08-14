import time
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import connection

from .models import StoryGeneration, GenerationStep, UserPreferences

logger = logging.getLogger(__name__)

def table_exists():
    """Check if database tables exist."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generator_storygeneration';")
            return cursor.fetchone() is not None
    except:
        return False

def check_audio_support():
    """Safely check if audio processing is available."""
    try:
        import whisper
        import speech_recognition as sr
        from pydub import AudioSegment
        return True
    except ImportError:
        return False

def check_ollama_status():
    """Check if Ollama is running and ready."""
    try:
        from .ollama_story_generator import check_and_suggest_ollama_setup
        available, models = check_and_suggest_ollama_setup()
        return {
            'available': available,
            'models': models,
            'recommended_models': ['llama3.1:8b', 'llama3.1:70b', 'mistral:7b']
        }
    except Exception as e:
        logger.warning(f"Ollama check failed: {e}")
        return {'available': False, 'models': [], 'recommended_models': []}

def check_gpu_status():
    """Check GPU availability for image generation."""
    try:
        from .gpu_image_generator import check_gpu_requirements
        return check_gpu_requirements()
    except Exception as e:
        logger.warning(f"GPU check failed: {e}")
        return {'cuda_available': False, 'diffusers_available': False}

class IndexView(TemplateView):
    """Enhanced main page with Ollama and GPU status."""
    template_name = 'generator/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check all system capabilities
        context['audio_supported'] = check_audio_support()
        context['ollama_status'] = check_ollama_status()
        context['gpu_status'] = check_gpu_status()
        
        # Get recent stories if database is ready
        if table_exists():
            try:
                context['recent_stories'] = StoryGeneration.objects.filter(status='completed')[:6]
            except:
                context['recent_stories'] = []
        else:
            context['recent_stories'] = []
            context['database_not_ready'] = True
        
        # Available image styles
        try:
            from .gpu_image_generator import GPUImageGenerator
            generator = GPUImageGenerator()
            context['available_image_styles'] = generator.get_available_styles()
        except:
            context['available_image_styles'] = ['realistic', 'artistic', 'fantasy']
        
        return context

class GenerateStoryView(View):
    """Enhanced story generation with Ollama and GPU."""
    
    def get(self, request):
        return redirect('generator:index')
    
    def post(self, request):
        if not table_exists():
            messages.error(request, '🚨 Database not ready! Please run: python manage.py migrate')
            return redirect('generator:index')
        
        try:
            # Get input parameters
            prompt = request.POST.get('prompt', '').strip()
            audio_file = request.FILES.get('audio_file')
            story_length = request.POST.get('story_length', 'medium')
            image_style = request.POST.get('image_style', 'realistic')
            
            if not prompt and not audio_file:
                messages.error(request, 'Please provide either text input or audio file.')
                return redirect('generator:index')
            
            # Create story record
            story = StoryGeneration.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=prompt,
                input_method='text' if prompt and not audio_file else 'audio' if audio_file and not prompt else 'both',
                status='pending'
            )
            
            # Handle audio input
            if audio_file:
                success = self._handle_audio_input(story, audio_file)
                if not success:
                    return redirect('generator:index')
            
            # Generate content with Ollama + GPU
            story.status = 'processing'
            story.save()
            self._generate_enhanced_story_content(story, story_length, image_style)
            
            if story.status == 'error':
                messages.error(request, f'Generation error: {story.error_message}')
                return redirect('generator:index')
            else:
                messages.success(request, '🎉 Enhanced story generated with Ollama + GPU!')
                return redirect('generator:result', story_id=story.id)
        
        except Exception as e:
            logger.error(f"Enhanced generation error: {e}")
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return redirect('generator:index')
    
    def _handle_audio_input(self, story, audio_file):
        """Handle audio input safely."""
        try:
            if audio_file.size > 10 * 1024 * 1024:
                story.status = 'error'
                story.error_message = 'Audio file too large (max 10MB)'
                story.save()
                messages.error(self.request, 'Audio file too large')
                return False
            
            story.audio_file = audio_file
            story.status = 'transcribing'
            story.save()
            
            if not check_audio_support():
                raise Exception("Audio processing not available")
            
            transcribed_text = self._safe_transcribe_audio(audio_file)
            story.transcribed_text = transcribed_text
            story.save()
            messages.success(self.request, '✅ Audio transcribed!')
            return True
            
        except Exception as e:
            story.status = 'error'
            story.error_message = f"Audio transcription failed: {str(e)}"
            story.save()
            messages.error(self.request, 'Audio transcription failed')
            return False
    
    def _safe_transcribe_audio(self, audio_file):
        """Safely transcribe audio."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(temp_path)
            return result["text"]
        except:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio_data = r.record(source)
                return r.recognize_google(audio_data)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _generate_enhanced_story_content(self, story, length, image_style):
        """Generate content using Ollama + GPU pipeline."""
        start_time = time.time()
        
        try:
            # Import enhanced generators
            from .ollama_story_generator import OllamaStoryGenerator
            from .gpu_image_generator import GPUImageGenerator
            
            input_text = story.get_input_text()
            if not input_text:
                raise Exception("No input text available")
            
            # Generate story with Ollama
            story_generator = OllamaStoryGenerator()
            story.story_text = story_generator.generate_story(input_text, length)
            story.ai_model_used = f"Ollama ({story_generator.story_model})"
            
            # Generate descriptions with Ollama
            story.character_description = story_generator.generate_character_description(story.story_text)
            story.background_description = story_generator.generate_scene_description(story.story_text)
            
            # Generate images with GPU
            image_generator = GPUImageGenerator()
            
            # Character image
            char_image_data = image_generator.generate_character_image(story.character_description, image_style)
            story.character_image.save(f'character_{story.id}.png', ContentFile(char_image_data), save=False)
            
            # Background image
            bg_image_data = image_generator.generate_background_image(story.background_description, image_style)
            story.background_image.save(f'background_{story.id}.png', ContentFile(bg_image_data), save=False)
            
            # Compose final scene
            if story.character_image and story.background_image:
                composed_data = image_generator.compose_images(
                    story.character_image.path,
                    story.background_image.path
                )
                story.composed_image.save(f'composed_{story.id}.png', ContentFile(composed_data), save=False)
            
            story.image_model_used = f"Stable Diffusion ({image_style})"
            
            # Clean up GPU memory
            image_generator.cleanup()
            
            # Mark completed
            story.status = 'completed'
            story.generation_time = time.time() - start_time
            story.save()
            
        except Exception as e:
            logger.error(f"Enhanced generation failed: {e}")
            story.status = 'error'
            story.error_message = str(e)
            story.save()

class StoryResultView(TemplateView):
    """Enhanced result view."""
    template_name = 'generator/result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story_id = kwargs.get('story_id')
        
        if not table_exists():
            context['story'] = None
            return context
        
        try:
            story = get_object_or_404(StoryGeneration, id=story_id)
            context['story'] = story
            context['story_stats'] = {
                'word_count': story.story_word_count,
                'generation_time': story.generation_time,
                'input_method': story.get_input_method_display(),
                'ai_model': story.ai_model_used,
                'image_model': story.image_model_used,
            }
        except:
            context['story'] = None
            
        return context

class DownloadImageView(View):
    """Download images."""
    
    def get(self, request, story_id, image_type):
        try:
            story = get_object_or_404(StoryGeneration, id=story_id)
            
            if image_type == 'character' and story.character_image:
                image_file = story.character_image
            elif image_type == 'background' and story.background_image:
                image_file = story.background_image
            elif image_type == 'composed' and story.composed_image:
                image_file = story.composed_image
            else:
                raise Http404("Image not found")
            
            response = HttpResponse(image_file.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{image_type}_{story_id}.png"'
            return response
            
        except Exception as e:
            raise Http404("Download failed")

class GenerationStatusView(View):
    """Status API."""
    
    def get(self, request, story_id):
        try:
            story = get_object_or_404(StoryGeneration, id=story_id)
            return JsonResponse({
                'status': story.status,
                'completed': story.status == 'completed',
                'generation_time': story.generation_time,
                'word_count': story.story_word_count,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AudioTranscribeView(View):
    """Audio transcription API."""
    
    def post(self, request):
        try:
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return JsonResponse({'error': 'No audio file'}, status=400)
            
            view = GenerateStoryView()
            text = view._safe_transcribe_audio(audio_file)
            
            return JsonResponse({'success': True, 'text': text})
        except Exception as e:
            return JsonResponse({'error': 'Transcription failed'}, status=500)

class UserPreferencesView(View):
    """User preferences API."""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            prefs = UserPreferences.objects.get(user=request.user)
            return JsonResponse({
                'preferred_story_length': prefs.preferred_story_length,
                'preferred_genre': prefs.preferred_genre,
            })
        except UserPreferences.DoesNotExist:
            return JsonResponse({'error': 'Preferences not found'}, status=404)