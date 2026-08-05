from django.db import models
from django.core.exceptions import ValidationError

from apps.common.models import TimeStampedModel, UUIDModel
from apps.speaking.models import SpeakingAudioSubmission
from apps.writing.models import WritingSubmission


class AIEvaluation(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        STARTED = 'started', 'Started'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        PENDING_HUMAN_REVIEW = 'pending_human_review', 'Pending Human Review'

    writing_submission = models.ForeignKey(WritingSubmission, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_evaluations')
    speaking_submission = models.ForeignKey(SpeakingAudioSubmission, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_evaluations')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    provider = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    prompt_version = models.CharField(max_length=255, blank=True)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    criteria_scores = models.JSONField(default=dict, blank=True)
    feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    improvement_suggestions = models.JSONField(default=list, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    token_usage = models.JSONField(default=dict, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if bool(self.writing_submission) == bool(self.speaking_submission):
            raise ValidationError('Exactly one of writing_submission or speaking_submission must be set.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'AIEvaluation {self.id} ({self.status})'
