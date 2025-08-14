"""
Enhanced database models with audio support.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def story_image_path(instance, filename):
    """Generate upload path for story images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('generated', 'stories', str(instance.id), filename)

def audio_upload_path(instance, filename):
    """Generate upload path for audio files."""
    ext = filename.split('.')[-1]
    filename = f"audio_{uuid.uuid4()}.{ext}"
    return os.path.join('audio', 'uploads', filename)

class StoryGeneration(models.Model):
    """Enhanced model for story generation with audio support."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Input methods
    prompt = models.TextField(help_text="Original user prompt", blank=True)
    audio_file = models.FileField(upload_to=audio_upload_path, blank=True, null=True, 
                                 help_text="Audio input file")
    transcribed_text = models.TextField(blank=True, help_text="Transcribed audio text")
    input_method = models.CharField(max_length=20, choices=[
        ('text', 'Text Input'),
        ('audio', 'Audio Input'),
        ('both', 'Text and Audio')
    ], default='text')

    # Generated content
    story_text = models.TextField(blank=True, help_text="Generated story content")
    character_description = models.TextField(blank=True, help_text="Extracted character details")
    background_description = models.TextField(blank=True, help_text="Extracted background details")

    # Generated images
    character_image = models.ImageField(upload_to=story_image_path, blank=True, null=True)
    background_image = models.ImageField(upload_to=story_image_path, blank=True, null=True)
    composed_image = models.ImageField(upload_to=story_image_path, blank=True, null=True)

    # Generation metadata
    story_word_count = models.IntegerField(default=0, help_text="Number of words in story")
    ai_model_used = models.CharField(max_length=100, blank=True, help_text="AI model used for generation")
    image_model_used = models.CharField(max_length=100, blank=True, help_text="Image model used")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generation_time = models.FloatField(null=True, blank=True, help_text="Time taken in seconds")

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('transcribing', 'Transcribing Audio'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    # User engagement
    is_favorite = models.BooleanField(default=False)
    shared_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Story Generation'
        verbose_name_plural = 'Story Generations'

    def __str__(self):
        if self.prompt:
            return f"Story: {self.prompt[:50]}..." if len(self.prompt) > 50 else f"Story: {self.prompt}"
        elif self.transcribed_text:
            return f"Audio Story: {self.transcribed_text[:50]}..."
        else:
            return f"Story {self.id}"

    def get_input_text(self):
        """Get the input text (prompt or transcribed audio)."""
        if self.input_method == 'audio':
            return self.transcribed_text
        elif self.input_method == 'both':
            return f"{self.prompt} {self.transcribed_text}".strip()
        else:
            return self.prompt

    def save(self, *args, **kwargs):
        # Update word count
        if self.story_text:
            self.story_word_count = len(self.story_text.split())
        super().save(*args, **kwargs)

class GenerationStep(models.Model):
    """Track individual processing steps."""
    story = models.ForeignKey(StoryGeneration, on_delete=models.CASCADE, related_name='steps')
    step_name = models.CharField(max_length=100)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store additional step data

    class Meta:
        ordering = ['started_at']

    def __str__(self):
        return f"{self.story.id} - {self.step_name}"

class UserPreferences(models.Model):
    """Store user preferences for story generation."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Preferred settings
    preferred_story_length = models.CharField(max_length=20, choices=[
        ('short', 'Short (300-500 words)'),
        ('medium', 'Medium (500-1000 words)'),
        ('long', 'Long (1000-1500 words)')
    ], default='medium')

    preferred_genre = models.CharField(max_length=50, choices=[
        ('fantasy', 'Fantasy'),
        ('sci-fi', 'Science Fiction'),
        ('adventure', 'Adventure'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('any', 'Any Genre')
    ], default='any')

    enable_audio_input = models.BooleanField(default=True)
    auto_generate_images = models.BooleanField(default=True)

    # Notification preferences
    email_on_completion = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
