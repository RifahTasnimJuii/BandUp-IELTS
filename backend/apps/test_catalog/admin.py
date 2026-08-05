from django.contrib import admin

from .models import AudioAsset, Passage, Section, Test


class PassageInline(admin.StackedInline):
    model = Passage
    extra = 0
    fields = ('title', 'body_text', 'source_note', 'license_note', 'is_original_sample', 'is_copyable_default', 'order')


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
    list_display = ('title', 'module_type', 'is_published', 'is_featured', 'published_at')
    list_filter = ('module_type', 'is_published', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'test', 'section_type', 'order', 'is_published')
    list_filter = ('section_type', 'is_published')
    search_fields = ('title', 'instruction_text')
    inlines = [PassageInline]


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'word_count')
    list_filter = ('section__section_type',)
    search_fields = ('title', 'body_text')


@admin.register(AudioAsset)
class AudioAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'is_active', 'duration_seconds')
    list_filter = ('is_active', 'storage_provider')
    search_fields = ('title', 'transcript', 'mime_type')
