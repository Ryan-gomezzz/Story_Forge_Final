"""
Enhanced Django admin for the story generator.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import StoryGeneration, GenerationStep, UserPreferences

@admin.register(StoryGeneration)
class StoryGenerationAdmin(admin.ModelAdmin):
    list_display = (
        'prompt_preview', 
        'input_method_display',
        'status_display', 
        'word_count_display',
        'generation_time_display',
        'created_at',
        'view_result'
    )
    list_filter = ('status', 'input_method', 'created_at', 'ai_model_used')
    search_fields = ('prompt', 'transcribed_text', 'story_text')
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'generation_time',
        'story_word_count', 'ai_model_used', 'image_model_used'
    )
    fieldsets = (
        ('Input', {
            'fields': ('user', 'input_method', 'prompt', 'audio_file', 'transcribed_text')
        }),
        ('Generated Content', {
            'fields': ('story_text', 'character_description', 'background_description')
        }),
        ('Generated Images', {
            'fields': ('character_image', 'background_image', 'composed_image')
        }),
        ('Generation Metadata', {
            'fields': (
                'ai_model_used', 'image_model_used', 'story_word_count',
                'generation_time', 'status', 'error_message'
            )
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def prompt_preview(self, obj):
        text = obj.get_input_text()
        return text[:50] + "..." if len(text) > 50 else text
    prompt_preview.short_description = "Input Text"

    def input_method_display(self, obj):
        colors = {
            'text': 'primary',
            'audio': 'success', 
            'both': 'info'
        }
        color = colors.get(obj.input_method, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_input_method_display()
        )
    input_method_display.short_description = "Input Method"

    def status_display(self, obj):
        colors = {
            'pending': 'warning',
            'transcribing': 'info',
            'processing': 'primary',
            'completed': 'success',
            'error': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"

    def word_count_display(self, obj):
        if obj.story_word_count:
            return f"{obj.story_word_count:,} words"
        return "-"
    word_count_display.short_description = "Word Count"

    def generation_time_display(self, obj):
        if obj.generation_time:
            return f"{obj.generation_time:.1f}s"
        return "-"
    generation_time_display.short_description = "Generation Time"

    def view_result(self, obj):
        if obj.status == 'completed':
            url = reverse('generator:result', kwargs={'story_id': obj.id})
            return format_html('<a href="{}" target="_blank">View</a>', url)
        return "-"
    view_result.short_description = "Result"

class GenerationStepInline(admin.TabularInline):
    model = GenerationStep
    extra = 0
    readonly_fields = ('step_name', 'started_at', 'completed_at', 'success', 'error_message')
    can_delete = False

@admin.register(GenerationStep)
class GenerationStepAdmin(admin.ModelAdmin):
    list_display = ('story_link', 'step_name', 'success_display', 'duration', 'started_at')
    list_filter = ('success', 'step_name', 'started_at')
    readonly_fields = ('story', 'step_name', 'started_at', 'completed_at', 'success', 'metadata')

    def story_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:generator_storygeneration_change', args=[obj.story.id]),
            str(obj.story)[:50] + "..."
        )
    story_link.short_description = "Story"

    def success_display(self, obj):
        if obj.success:
            return format_html('<span class="badge bg-success">✓</span>')
        else:
            return format_html('<span class="badge bg-danger">✗</span>')
    success_display.short_description = "Success"

    def duration(self, obj):
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            return f"{delta.total_seconds():.1f}s"
        return "-"

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'preferred_story_length', 'preferred_genre',
        'enable_audio_input', 'auto_generate_images', 'updated_at'
    )
    list_filter = ('preferred_story_length', 'preferred_genre', 'enable_audio_input')
    search_fields = ('user__username', 'user__email')

# Customize admin site
admin.site.site_header = "StoryForge AI Enhanced Admin"
admin.site.site_title = "StoryForge AI"
admin.site.index_title = "Story Generation Management"
