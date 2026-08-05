from django.contrib import admin

from .models import Attempt, AttemptSectionState, AnswerResponse, ExamViolationEvent


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'mode', 'state', 'started_at', 'expires_at', 'submitted_at')
    list_filter = ('mode', 'state', 'is_auto_submitted')
    search_fields = ('user__email', 'test__title', 'audit_reason')


@admin.register(AttemptSectionState)
class AttemptSectionStateAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'section', 'state', 'started_at', 'ends_at', 'completed_at')
    list_filter = ('state', 'is_locked')
    search_fields = ('attempt__id', 'section__title')


@admin.register(AnswerResponse)
class AnswerResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_flagged', 'is_locked', 'submitted_at')
    list_filter = ('is_flagged', 'is_locked')
    search_fields = ('attempt__id', 'question__prompt')


@admin.register(ExamViolationEvent)
class ExamViolationEventAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'violation_type', 'severity', 'auto_action_taken', 'created_at', 'resolved_at')
    list_filter = ('violation_type', 'severity', 'auto_action_taken')
    search_fields = ('attempt__id', 'details', 'metadata')
