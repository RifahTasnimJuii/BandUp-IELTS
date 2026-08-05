from celery import shared_task
from django.utils import timezone

from apps.attempts.models import Attempt
from apps.attempts.services import lock_attempt_responses, grade_and_finalize_attempt


@shared_task(bind=True)
def task_auto_submit_expired_attempts(self):
    now = timezone.now()
    expired_attempts = Attempt.objects.filter(
        state__in=[Attempt.State.CREATED, Attempt.State.IN_PROGRESS],
        expires_at__lt=now,
    )
    submitted_count = 0

    for attempt in expired_attempts:
        attempt.state = Attempt.State.SUBMITTED
        attempt.submitted_at = now
        attempt.ended_at = now
        attempt.is_auto_submitted = True
        attempt.save(update_fields=['state', 'submitted_at', 'ended_at', 'is_auto_submitted'])
        lock_attempt_responses(attempt)
        grade_and_finalize_attempt.delay(str(attempt.id))
        submitted_count += 1

    return {'submitted_attempts': submitted_count}


@shared_task(bind=True)
def task_grade_and_finalize_attempt(self, attempt_id):
    grade_and_finalize_attempt(attempt_id)
    return {'attempt_id': attempt_id}
