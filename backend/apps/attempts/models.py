from django.db import models
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.common.models import TimeStampedModel, UUIDModel
from apps.questions.models import Question
from apps.test_catalog.models import Section, Test


class Attempt(UUIDModel, TimeStampedModel):
    class Mode(models.TextChoices):
        PRACTICE = 'practice', 'Practice'
        EXAM = 'exam', 'Exam'

    class State(models.TextChoices):
        CREATED = 'created', 'Created'
        IN_PROGRESS = 'in_progress', 'In Progress'
        SUBMITTED = 'submitted', 'Submitted'
        EXPIRED = 'expired', 'Expired'
        EVALUATING = 'evaluating', 'Evaluating'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.EXAM)
    state = models.CharField(max_length=16, choices=State.choices, default=State.CREATED)
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    current_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    server_start_time = models.DateTimeField(null=True, blank=True)
    client_timezone = models.CharField(max_length=64, blank=True)
    locale = models.CharField(max_length=16, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    violation_count = models.PositiveIntegerField(default=0)
    is_auto_submitted = models.BooleanField(default=False)
    is_review_allowed = models.BooleanField(default=False)
    overall_band = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    listening_band = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    reading_band = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    writing_band = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    speaking_band = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    audit_reason = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['test']),
            models.Index(fields=['state']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f'Attempt {self.id} by {self.user.email} on {self.test.title}'


class AttemptSectionState(UUIDModel, TimeStampedModel):
    class SectionState(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        SKIPPED = 'skipped', 'Skipped'
        LOCKED = 'locked', 'Locked'

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='section_states')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='attempt_states')
    state = models.CharField(max_length=16, choices=SectionState.choices, default=SectionState.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    remaining_seconds = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(default=0)
    raw_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    band_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    autosave_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'section')
        ordering = ['attempt', 'section']

    def __str__(self):
        return f'{self.attempt} / {self.section} [{self.state}]'


class AnswerResponse(UUIDModel, TimeStampedModel):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answer_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_responses')
    value_json = models.JSONField(default=dict, blank=True)
    answer_text = models.TextField(null=True, blank=True)
    selected_options = models.JSONField(null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    is_cleared = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['attempt', 'question']

    def __str__(self):
        return f'AnswerResponse {self.question_id} for Attempt {self.attempt_id}'


class ExamViolationEvent(UUIDModel, TimeStampedModel):
    class ViolationType(models.TextChoices):
        TAB_SWITCH = 'tab_switch', 'Tab Switch'
        VISIBILITY_HIDDEN = 'visibility_hidden', 'Visibility Hidden'
        FULLSCREEN_EXIT = 'fullscreen_exit', 'Fullscreen Exit'
        COPY_ATTEMPT = 'copy_attempt', 'Copy Attempt'
        PASTE_ATTEMPT = 'paste_attempt', 'Paste Attempt'
        MULTIPLE_TABS = 'multiple_tabs', 'Multiple Tabs'
        NETWORK_DISCONNECT = 'network_disconnect', 'Network Disconnect'
        NO_HEARTBEAT = 'no_heartbeat', 'No Heartbeat'
        AUDIO_PLAYBACK_ERROR = 'audio_playback_error', 'Audio Playback Error'
        MANUAL_REVIEW = 'manual_review', 'Manual Review'

    class Severity(models.TextChoices):
        WARNING = 'warning', 'Warning'
        CRITICAL = 'critical', 'Critical'

    class AutoAction(models.TextChoices):
        NONE = 'none', 'None'
        WARNING_SHOWN = 'warning_shown', 'Warning Shown'
        ATTEMPT_LOCKED = 'attempt_locked', 'Attempt Locked'
        AUTO_SUBMITTED = 'auto_submitted', 'Auto Submitted'

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='violation_events')
    violation_type = models.CharField(max_length=32, choices=ViolationType.choices)
    details = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.WARNING)
    auto_action_taken = models.CharField(max_length=32, choices=AutoAction.choices, default=AutoAction.NONE)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.violation_type} for Attempt {self.attempt_id}'
