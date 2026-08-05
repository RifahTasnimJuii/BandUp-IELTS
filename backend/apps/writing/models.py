from django.db import models

from apps.attempts.models import Attempt
from apps.common.models import TimeStampedModel, UUIDModel
from apps.questions.models import Question


class WritingSubmission(UUIDModel, TimeStampedModel):
    class TaskNumber(models.IntegerChoices):
        TASK_1 = 1, 'Task 1'
        TASK_2 = 2, 'Task 2'

    class EvaluationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        PENDING_HUMAN_REVIEW = 'pending_human_review', 'Pending Human Review'

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='writing_submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='writing_submissions')
    task_number = models.IntegerField(choices=TaskNumber.choices)
    prompt = models.TextField()
    answer_text = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    below_min_word_warning = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
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

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['-submitted_at']

    def save(self, *args, **kwargs):
        self.word_count = len(self.answer_text.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f'WritingSubmission {self.attempt_id} - {self.question_id}'
