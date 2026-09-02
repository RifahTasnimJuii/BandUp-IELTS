from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.attempts.models import Attempt, AttemptSectionState
from apps.grading.services import calculate_question_score, calculate_section_band_score
from apps.writing.models import WritingSubmission
from apps.speaking.models import SpeakingAudioSubmission
import re
from django.conf import settings


def lock_attempt_responses(attempt):
    now = timezone.now()
    attempt.answer_responses.filter(is_locked=False).update(is_locked=True, locked_at=now, submitted_at=now)


def grade_objective_sections(attempt):
    section_scores = {}

    for answer_response in attempt.answer_responses.select_related('question__question_group__section'):
        question = answer_response.question
        section = question.question_group.section

        if question.type in [
            question.QuestionType.WRITING_PROMPT,
            question.QuestionType.SPEAKING_PROMPT,
        ]:
            continue

        raw_score = calculate_question_score(question, answer_response)
        section_scores.setdefault(section.id, {
            'section': section,
            'section_type': section.section_type,
            'raw_score': Decimal('0'),
            'question_count': 0,
        })
        section_scores[section.id]['raw_score'] += raw_score
        section_scores[section.id]['question_count'] += 1

    section_bands = {}

    for section_data in section_scores.values():
        section = section_data['section']
        band_score = calculate_section_band_score(
            attempt.test,
            section.section_type,
            section_data['raw_score'],
        )
        section_state, _ = AttemptSectionState.objects.update_or_create(
            attempt=attempt,
            section=section,
            defaults={
                'state': AttemptSectionState.SectionState.COMPLETED,
                'raw_score': section_data['raw_score'],
                'band_score': band_score,
                'is_locked': True,
                'completed_at': timezone.now(),
            },
        )
        section_bands.setdefault(section.section_type, []).append(section_state.band_score)

    attempt.listening_band = _average_bands(section_bands.get('listening', []))
    attempt.reading_band = _average_bands(section_bands.get('reading', []))
    attempt.save(update_fields=['listening_band', 'reading_band'])


def _average_bands(band_scores):
    valid_scores = [band for band in band_scores if band is not None]
    if not valid_scores:
        return None
    return sum(valid_scores) / Decimal(len(valid_scores))


def _load_ai_evaluation_tasks():
    from apps.writing.tasks import task_evaluate_writing_submission
    from apps.speaking.tasks import task_evaluate_speaking_submission
    return task_evaluate_writing_submission, task_evaluate_speaking_submission


def evaluate_writing_offline(submission):
    words = re.findall(r"[A-Za-z']+", submission.answer_text.lower())
    total_words = len(words)
    unique_ratio = len(set(words)) / total_words if total_words else 0
    sentences = [part.strip() for part in re.split(r'[.!?]+', submission.answer_text) if part.strip()]
    average_sentence_length = total_words / len(sentences) if sentences else 0
    minimum = 150 if submission.task_number == WritingSubmission.TaskNumber.TASK_1 else 250
    length_score = 5.0 if total_words < minimum else 6.0
    lexical = max(5.5, min(6.5, 6.0 + (0.5 if unique_ratio >= 0.55 else -0.5 if unique_ratio < 0.35 else 0)))
    structure = max(5.5, min(6.5, 6.0 + (0.5 if len(sentences) >= 4 and 10 <= average_sentence_length <= 28 else -0.5)))
    criteria = {
        'task_achievement': length_score,
        'coherence_cohesion': structure,
        'lexical_resource': lexical,
        'grammatical_range': structure,
    }
    band = max(4.0, min(7.0, round(sum(criteria.values()) / len(criteria) * 2) / 2))
    submission.band_score = band
    submission.criteria_scores = criteria
    submission.ai_feedback = {'feedback': 'Automated provisional estimate'}
    submission.evaluation_status = WritingSubmission.EvaluationStatus.COMPLETED
    submission.model_name = 'offline-heuristic'
    submission.save(update_fields=['band_score', 'criteria_scores', 'ai_feedback', 'evaluation_status', 'model_name'])
    return submission


def evaluate_pending_writing_submissions(attempt):
    for submission in attempt.writing_submissions.filter(evaluation_status=WritingSubmission.EvaluationStatus.PENDING):
        if getattr(settings, 'OPENAI_API_KEY', ''):
            task_evaluate_writing_submission, _ = _load_ai_evaluation_tasks()
            submission.evaluation_status = WritingSubmission.EvaluationStatus.IN_PROGRESS
            submission.save(update_fields=['evaluation_status'])
            task_evaluate_writing_submission.delay(str(submission.id))
        else:
            evaluate_writing_offline(submission)


def _dispatch_ai_evaluations(attempt):
    task_evaluate_writing_submission, task_evaluate_speaking_submission = _load_ai_evaluation_tasks()
    dispatched = 0

    for submission in attempt.writing_submissions.filter(evaluation_status=WritingSubmission.EvaluationStatus.PENDING):
        submission.evaluation_status = WritingSubmission.EvaluationStatus.IN_PROGRESS
        submission.save(update_fields=['evaluation_status'])
        task_evaluate_writing_submission.delay(str(submission.id))
        dispatched += 1

    for submission in attempt.speaking_submissions.filter(evaluation_status=SpeakingAudioSubmission.EvaluationStatus.PENDING):
        submission.evaluation_status = SpeakingAudioSubmission.EvaluationStatus.IN_PROGRESS
        submission.save(update_fields=['evaluation_status'])
        task_evaluate_speaking_submission.delay(str(submission.id))
        dispatched += 1

    return dispatched


def _has_pending_ai_evaluations(attempt):
    return attempt.writing_submissions.filter(
        evaluation_status__in=[WritingSubmission.EvaluationStatus.PENDING, WritingSubmission.EvaluationStatus.IN_PROGRESS]
    ).exists() or attempt.speaking_submissions.filter(
        evaluation_status__in=[SpeakingAudioSubmission.EvaluationStatus.PENDING, SpeakingAudioSubmission.EvaluationStatus.IN_PROGRESS]
    ).exists()


def _calculate_ai_band_scores(attempt):
    writing_scores = [submission.band_score for submission in attempt.writing_submissions.filter(evaluation_status=WritingSubmission.EvaluationStatus.COMPLETED) if submission.band_score is not None]
    speaking_scores = [submission.band_score for submission in attempt.speaking_submissions.filter(evaluation_status=SpeakingAudioSubmission.EvaluationStatus.COMPLETED) if submission.band_score is not None]

    attempt.writing_band = _average_bands([Decimal(score) for score in writing_scores]) if writing_scores else None
    attempt.speaking_band = _average_bands([Decimal(score) for score in speaking_scores]) if speaking_scores else None


def _calculate_overall_band(attempt):
    bands = [band for band in [attempt.listening_band, attempt.reading_band, attempt.writing_band, attempt.speaking_band] if band is not None]
    if not bands:
        return None
    return sum(bands) / Decimal(len(bands))


def finalize_attempt_after_ai_evaluations(attempt_id):
    attempt = Attempt.objects.select_related('test').get(pk=attempt_id)
    if _has_pending_ai_evaluations(attempt):
        return attempt

    _calculate_ai_band_scores(attempt)
    attempt.overall_band = _calculate_overall_band(attempt)
    attempt.state = Attempt.State.COMPLETED
    attempt.save(update_fields=['writing_band', 'speaking_band', 'overall_band', 'state'])
    return attempt


def grade_and_finalize_attempt(attempt_id):
    attempt = Attempt.objects.select_related('test').get(pk=attempt_id)
    lock_attempt_responses(attempt)
    from apps.attempts.views import AttemptViewSet
    AttemptViewSet._create_writing_submissions(attempt)
    evaluate_pending_writing_submissions(attempt)
    grade_objective_sections(attempt)
    dispatched = _dispatch_ai_evaluations(attempt)

    if dispatched > 0:
        attempt.state = Attempt.State.EVALUATING
        attempt.save(update_fields=['state'])
    else:
        finalize_attempt_after_ai_evaluations(attempt_id)

    return attempt
