from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.accounts.models import User
from apps.common.models import TimeStampedModel, UUIDModel


class Test(UUIDModel, TimeStampedModel):
    class ModuleType(models.TextChoices):
        ACADEMIC = 'academic', 'Academic'
        GENERAL = 'general', 'General'
        BOTH = 'both', 'Both'

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    module_type = models.CharField(max_length=16, choices=ModuleType.choices, default=ModuleType.BOTH)
    attempt_limit = models.PositiveIntegerField(default=0)
    strict_exam_mode = models.BooleanField(default=False)
    allow_practice_replay = models.BooleanField(default=True)
    copy_protection_enabled = models.BooleanField(default=False)
    default_section_order = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    scoring_config = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_tests')

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.title)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Section(UUIDModel, TimeStampedModel):
    class SectionType(models.TextChoices):
        LISTENING = 'listening', 'Listening'
        READING = 'reading', 'Reading'
        WRITING = 'writing', 'Writing'
        SPEAKING = 'speaking', 'Speaking'

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    section_type = models.CharField(max_length=16, choices=SectionType.choices)
    duration_seconds = models.PositiveIntegerField(default=0)
    extra_transfer_time_seconds = models.PositiveIntegerField(default=0)
    instruction_text = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_locked_by_default = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        unique_together = ('test', 'section_type', 'order')
        ordering = ['test', 'order']

    def __str__(self):
        return f'{self.test.title} – {self.title}'


class Passage(UUIDModel, TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='passages')
    title = models.CharField(max_length=255)
    body_text = models.TextField()
    source_note = models.CharField(max_length=512, blank=True)
    license_note = models.CharField(max_length=512, blank=True)
    is_original_sample = models.BooleanField(default=False)
    is_copyable_default = models.BooleanField(default=True)
    word_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['section', 'order']

    def clean(self):
        if not self.body_text.strip():
            raise ValidationError({'body_text': 'Passage body text cannot be empty.'})

    def save(self, *args, **kwargs):
        self.clean()
        self.word_count = len(self.body_text.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AudioAsset(UUIDModel, TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='audio_assets')
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='audio_assets/')
    duration_seconds = models.PositiveIntegerField(default=0)
    transcript = models.TextField(blank=True)
    mime_type = models.CharField(max_length=128, blank=True)
    storage_provider = models.CharField(max_length=128, blank=True)
    signed_url_expires_at = models.DateTimeField(null=True, blank=True)
    original_license = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    playback_policy = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title
