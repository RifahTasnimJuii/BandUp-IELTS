from django.contrib import admin

from .models import WritingSubmission


@admin.register(WritingSubmission)
class WritingSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'question', 'task_number', 'evaluation_status', 'band_score', 'submitted_at')
    list_filter = ('evaluation_status',)
    search_fields = ('attempt__id', 'question__prompt', 'model_name')
