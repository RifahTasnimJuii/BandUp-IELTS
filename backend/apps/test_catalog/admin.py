from django import forms
from django.contrib import admin
from django.db import models

from .models import AudioAsset, Passage, Section, Test


class PassageInline(admin.StackedInline):
    model = Passage
    extra = 0
    fields = (
        'title',
        'body_text',
        'source_note',
        'license_note',
        'word_count',
        'is_original_sample',
        'is_copyable_default',
        'order',
    )
    readonly_fields = ('word_count',)


class AudioAssetInline(admin.StackedInline):
    model = AudioAsset
    extra = 0
    fields = (
        'title',
        'audio_file',
        'duration_seconds',
        'transcript',
        'mime_type',
        'is_active',
        'playback_policy',
    )


class SectionInline(admin.StackedInline):
    model = Section
    extra = 0
    fields = (
        'title',
        'section_type',
        'duration_seconds',
        'extra_transfer_time_seconds',
        'instruction_text',
        'order',
        'is_locked_by_default',
        'is_published',
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'module_type', 'is_published', 'strict_exam_mode')
    list_filter = ('module_type', 'is_published', 'strict_exam_mode')
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    fieldsets = (
        ('Test details', {
            'fields': ('title', 'slug', 'module_type', 'description', 'instructions')
        }),
        ('Publishing & rules', {
            'fields': ('attempt_limit', 'strict_exam_mode', 'allow_practice_replay', 'copy_protection_enabled', 'is_published', 'is_featured', 'published_at')
        }),
        ('Scoring', {
            'fields': ('scoring_config', 'default_section_order'),
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'test', 'section_type', 'duration_seconds')
    list_filter = ('section_type', 'is_published', 'test__module_type')
    search_fields = ('title', 'instruction_text', 'test__title')
    inlines = [PassageInline, AudioAssetInline]
    fieldsets = (
        ('Section setup', {
            'fields': ('test', 'title', 'section_type', 'order', 'duration_seconds', 'extra_transfer_time_seconds', 'instruction_text')
        }),
        ('Behavior', {
            'fields': ('is_locked_by_default', 'is_published')
        }),
    )


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'word_count', 'is_original_sample')
    list_filter = ('section__section_type', 'is_original_sample')
    search_fields = ('title', 'body_text', 'section__title')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 18, 'class': 'vLargeTextField'})}
    }
    fieldsets = (
        ('Passage content', {
            'fields': ('section', 'title', 'body_text', 'order')
        }),
        ('Attribution', {
            'fields': ('source_note', 'license_note', 'is_original_sample', 'is_copyable_default')
        }),
    )


@admin.register(AudioAsset)
class AudioAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'duration_seconds', 'is_active')
    list_filter = ('is_active', 'section__section_type')
    search_fields = ('title', 'transcript', 'section__title')
    fieldsets = (
        ('Audio file', {
            'fields': ('section', 'title', 'audio_file', 'duration_seconds', 'mime_type')
        }),
        ('Metadata', {
            'fields': ('transcript', 'storage_provider', 'original_license', 'playback_policy', 'is_active')
        }),
    )


admin.site.index_title = 'IELTS Content'
admin.site.site_header = 'BandUp IELTS Administration'
admin.site.site_title = 'BandUp IELTS Admin'
