# Generated for Enhanced StoryForge AI

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import generator.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StoryGeneration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('prompt', models.TextField(blank=True, help_text='Original user prompt')),
                ('audio_file', models.FileField(blank=True, help_text='Audio input file', null=True, upload_to=generator.models.audio_upload_path)),
                ('transcribed_text', models.TextField(blank=True, help_text='Transcribed audio text')),
                ('input_method', models.CharField(choices=[('text', 'Text Input'), ('audio', 'Audio Input'), ('both', 'Text and Audio')], default='text', max_length=20)),
                ('story_text', models.TextField(blank=True, help_text='Generated story content')),
                ('character_description', models.TextField(blank=True, help_text='Extracted character details')),
                ('background_description', models.TextField(blank=True, help_text='Extracted background details')),
                ('character_image', models.ImageField(blank=True, null=True, upload_to=generator.models.story_image_path)),
                ('background_image', models.ImageField(blank=True, null=True, upload_to=generator.models.story_image_path)),
                ('composed_image', models.ImageField(blank=True, null=True, upload_to=generator.models.story_image_path)),
                ('story_word_count', models.IntegerField(default=0, help_text='Number of words in story')),
                ('ai_model_used', models.CharField(blank=True, help_text='AI model used for generation', max_length=100)),
                ('image_model_used', models.CharField(blank=True, help_text='Image model used', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('generation_time', models.FloatField(blank=True, help_text='Time taken in seconds', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('transcribing', 'Transcribing Audio'), ('processing', 'Processing'), ('completed', 'Completed'), ('error', 'Error')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('is_favorite', models.BooleanField(default=False)),
                ('shared_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Story Generation',
                'verbose_name_plural': 'Story Generations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_story_length', models.CharField(choices=[('short', 'Short (300-500 words)'), ('medium', 'Medium (500-1000 words)'), ('long', 'Long (1000-1500 words)')], default='medium', max_length=20)),
                ('preferred_genre', models.CharField(choices=[('fantasy', 'Fantasy'), ('sci-fi', 'Science Fiction'), ('adventure', 'Adventure'), ('mystery', 'Mystery'), ('romance', 'Romance'), ('horror', 'Horror'), ('any', 'Any Genre')], default='any', max_length=50)),
                ('enable_audio_input', models.BooleanField(default=True)),
                ('auto_generate_images', models.BooleanField(default=True)),
                ('email_on_completion', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GenerationStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_name', models.CharField(max_length=100)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='generator.storygeneration')),
            ],
            options={
                'ordering': ['started_at'],
            },
        ),
    ]
