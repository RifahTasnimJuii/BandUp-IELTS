from django.db import models

from apps.attempts.models import Attempt
from apps.common.models import TimeStampedModel, UUIDModel
from apps.questions.models import Question


class SpeakingAudioSubmission(UUIDModel, TimeStampedModel):
    class PartNumber(models.IntegerChoices):
        PART_1 = 1, 'Part 1'
        PART_2 = 2, 'Part 2'
        PART_3 = 3, 'Part 3'

    class AudioFileUrlMethod(models.TextChoices):
        SIGNED_URL = 'signed_url', 'Signed URL'
        PRIVATE_MEDIA = 'private_media', 'Private Media'

    class TranscriptionStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class EvaluationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        PENDING_HUMAN_REVIEW = 'pending_human_review', 'Pending Human Review'

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='speaking_submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='speaking_submissions')
    part_number = models.IntegerField(choices=PartNumber.choices)
    prompt = models.TextField()
    storage_key = models.CharField(max_length=512)
    audio_file_url_method = models.CharField(max_length=32, choices=AudioFileUrlMethod.choices)
    duration_seconds = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=128)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prep_seconds_allowed = models.PositiveIntegerField(default=0)
    prep_seconds_used = models.PositiveIntegerField(default=0)
    recording_started_at = models.DateTimeField(null=True, blank=True)
    recording_ended_at = models.DateTimeField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    transcription_status = models.CharField(max_length=32, choices=TranscriptionStatus.choices, default=TranscriptionStatus.PENDING)
    evaluation_status = models.CharField(max_length=32, choices=EvaluationStatus.choices, default=EvaluationStatus.PENDING)
    band_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    criteria_scores = models.JSONField(default=dict, blank=True)
    ai_feedback = models.JSONField(default=dict, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    improvement_suggestions = models.JSONField(default=list, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    prompt_version = models.CharField(max_length=255, blank=True)
    token_usage = models.JSONField(default=dict, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    manual_override_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    manual_feedback = models.JSONField(default=dict, blank=True)
    consent_given = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'SpeakingAudioSubmission {self.attempt_id} part {self.part_number}'
