"""
Enhanced URL patterns for the generator app.
"""
from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('generate/', views.GenerateStoryView.as_view(), name='generate'),
    path('status/<uuid:story_id>/', views.GenerationStatusView.as_view(), name='status'),
    path('result/<uuid:story_id>/', views.StoryResultView.as_view(), name='result'),
    path('download/<uuid:story_id>/<str:image_type>/', views.DownloadImageView.as_view(), name='download'),

    # Enhanced endpoints
    path('api/transcribe/', views.AudioTranscribeView.as_view(), name='api_transcribe'),
    path('api/preferences/', views.UserPreferencesView.as_view(), name='api_preferences'),
]
