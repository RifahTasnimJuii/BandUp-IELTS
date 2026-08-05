from celery import shared_task


@shared_task(bind=True)
def task_evaluate_writing_submission(self, submission_id):
    from apps.ai_evaluation.services import evaluate_writing_submission
    from apps.attempts.services import finalize_attempt_after_ai_evaluations

    submission = evaluate_writing_submission(submission_id)
    finalize_attempt_after_ai_evaluations(submission.attempt_id)
    return {'submission_id': submission_id, 'status': submission.evaluation_status}
