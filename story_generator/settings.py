"""
Django settings for enhanced story_generator project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-enhanced-story-generator-2025')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'generator',  # Our enhanced app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'story_generator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'story_generator.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# AI Model Settings
AI_MODELS = {
    # API Keys
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    'HUGGINGFACE_API_KEY': os.getenv('HUGGINGFACE_API_KEY'),

    # Text Generation Models
    'TEXT_MODEL_PROVIDER': os.getenv('TEXT_MODEL_PROVIDER', 'huggingface'),  # openai, anthropic, huggingface
    'TEXT_MODEL_NAME': os.getenv('TEXT_MODEL_NAME', 'microsoft/DialoGPT-large'),
    'BACKUP_TEXT_MODEL': 'facebook/blenderbot-400M-distill',

    # Image Generation Models
    'IMAGE_MODEL_PROVIDER': os.getenv('IMAGE_MODEL_PROVIDER', 'huggingface'),  # openai, huggingface, local
    'CHARACTER_MODEL': os.getenv('CHARACTER_MODEL', 'runwayml/stable-diffusion-v1-5'),
    'BACKGROUND_MODEL': os.getenv('BACKGROUND_MODEL', 'runwayml/stable-diffusion-v1-5'),

    # Audio Processing
    'WHISPER_MODEL': os.getenv('WHISPER_MODEL', 'base'),  # tiny, base, small, medium, large
    'ENABLE_AUDIO_INPUT': os.getenv('ENABLE_AUDIO_INPUT', 'True').lower() == 'true',

    # Generation Settings
    'STORY_MIN_LENGTH': int(os.getenv('STORY_MIN_LENGTH', '500')),  # minimum words
    'STORY_MAX_LENGTH': int(os.getenv('STORY_MAX_LENGTH', '1500')), # maximum words
    'IMAGE_WIDTH': int(os.getenv('IMAGE_WIDTH', '512')),
    'IMAGE_HEIGHT': int(os.getenv('IMAGE_HEIGHT', '512')),
    'USE_GPU': os.getenv('USE_GPU', 'False').lower() == 'true',
}

# Create media directories
MEDIA_ROOT.mkdir(exist_ok=True)
(MEDIA_ROOT / 'generated').mkdir(exist_ok=True)
(MEDIA_ROOT / 'audio').mkdir(exist_ok=True)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'generator': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
