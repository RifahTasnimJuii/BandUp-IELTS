from django.contrib import admin

from .models import SpeakingAudioSubmission


@admin.register(SpeakingAudioSubmission)
class SpeakingAudioSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'question', 'part_number', 'evaluation_status', 'band_score', 'uploaded_at')
    list_filter = ('evaluation_status', 'transcription_status', 'consent_given')
    search_fields = ('attempt__id', 'question__prompt', 'storage_key')
