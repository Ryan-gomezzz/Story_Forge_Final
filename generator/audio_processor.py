"""
Audio processing for voice input using Whisper and other speech recognition tools.
"""
import os
import logging
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage

# Try to import audio processing libraries
try:
    import whisper
    import speech_recognition as sr
    from pydub import AudioSegment
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Process audio input and convert to text using Whisper."""

    def __init__(self):
        self.ai_settings = getattr(settings, 'AI_MODELS', {})
        self.whisper_model = None
        self.speech_recognizer = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize audio processing models."""
        if not AUDIO_LIBS_AVAILABLE:
            logger.warning("Audio libraries not available")
            return

        # Initialize Whisper if enabled
        if self.ai_settings.get('ENABLE_AUDIO_INPUT', True):
            try:
                model_name = self.ai_settings.get('WHISPER_MODEL', 'base')
                self.whisper_model = whisper.load_model(model_name)
                logger.info(f"Whisper model '{model_name}' loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")

        # Initialize speech recognition as fallback
        try:
            self.speech_recognizer = sr.Recognizer()
            logger.info("Speech recognition initialized")
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {e}")

    def transcribe_audio(self, audio_file) -> str:
        """Transcribe audio file to text."""
        if not AUDIO_LIBS_AVAILABLE:
            raise Exception("Audio processing libraries not installed")

        try:
            # Save uploaded file temporarily
            temp_path = self._save_temp_audio(audio_file)

            # Convert to WAV if needed
            wav_path = self._convert_to_wav(temp_path)

            # Transcribe using Whisper (preferred) or fallback
            if self.whisper_model:
                text = self._transcribe_with_whisper(wav_path)
            elif self.speech_recognizer:
                text = self._transcribe_with_speech_recognition(wav_path)
            else:
                raise Exception("No transcription method available")

            # Cleanup temporary files
            self._cleanup_temp_files([temp_path, wav_path])

            return text.strip()

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def _save_temp_audio(self, audio_file) -> str:
        """Save uploaded audio file temporarily."""
        # Create temp directory
        temp_dir = Path(settings.MEDIA_ROOT) / 'temp_audio'
        temp_dir.mkdir(exist_ok=True)

        # Save file
        file_name = f"temp_audio_{audio_file.name}"
        temp_path = temp_dir / file_name

        with open(temp_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        return str(temp_path)

    def _convert_to_wav(self, input_path: str) -> str:
        """Convert audio file to WAV format."""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)

            # Convert to WAV
            wav_path = input_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format='wav')

            return wav_path

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            # If conversion fails, try to use original file
            return input_path

    def _transcribe_with_whisper(self, audio_path: str) -> str:
        """Transcribe audio using Whisper."""
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result["text"]

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise

    def _transcribe_with_speech_recognition(self, audio_path: str) -> str:
        """Transcribe audio using SpeechRecognition library."""
        try:
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Record audio
                audio_data = self.speech_recognizer.record(source)

                # Transcribe using Google Speech Recognition (free)
                text = self.speech_recognizer.recognize_google(audio_data)
                return text

        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {e}")
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            raise

    def _cleanup_temp_files(self, file_paths: list):
        """Clean up temporary files."""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

    def is_audio_supported(self) -> bool:
        """Check if audio processing is supported."""
        return AUDIO_LIBS_AVAILABLE and (self.whisper_model or self.speech_recognizer)

    def get_supported_formats(self) -> list:
        """Get list of supported audio formats."""
        if not AUDIO_LIBS_AVAILABLE:
            return []

        return [
            'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg', 'webm',
            'audio/wav', 'audio/mp3', 'audio/mp4', 'audio/mpeg',
            'audio/flac', 'audio/ogg', 'audio/webm'
        ]

class AudioValidator:
    """Validate audio files before processing."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DURATION = 300  # 5 minutes

    @classmethod
    def validate_audio_file(cls, audio_file) -> tuple[bool, str]:
        """Validate uploaded audio file."""
        try:
            # Check file size
            if audio_file.size > cls.MAX_FILE_SIZE:
                return False, f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"

            # Check file extension
            if hasattr(audio_file, 'name') and audio_file.name:
                ext = audio_file.name.lower().split('.')[-1]
                supported_extensions = ['wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg', 'webm']
                if ext not in supported_extensions:
                    return False, f"Unsupported file format. Supported: {', '.join(supported_extensions)}"

            # Additional checks can be added here (duration, sample rate, etc.)

            return True, "Valid audio file"

        except Exception as e:
            return False, f"File validation error: {str(e)}"
