"""
ASGI config for story_generator project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'story_generator.settings')

application = get_asgi_application()
