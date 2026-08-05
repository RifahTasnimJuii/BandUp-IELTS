import json
import re
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from apps.ai_evaluation.models import AIEvaluation
from apps.writing.models import WritingSubmission
from apps.speaking.models import SpeakingAudioSubmission


def _create_openai_client():
    import openai

    openai.api_key = settings.OPENAI_API_KEY
    return openai


def _format_response_to_dict(response):
    if hasattr(response, 'to_dict'):
        return response.to_dict()
    if isinstance(response, dict):
        return response
    return {'raw': str(response)}


def _parse_json_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _extract_numeric_score(text):
    match = re.search(r'(?<!\d)([0-9](?:\.[05])?)(?!\d)', text)
    if match:
        return float(match.group(1))
    return None


def _build_writing_prompt(submission):
    return [
        {
            'role': 'system',
            'content': (
                'You are an IELTS writing examiner. Evaluate the student response based on IELTS writing band descriptors, ' 
                'including task response, coherence and cohesion, lexical resource, and grammatical range and accuracy.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Prompt: {submission.prompt}\n\n'
                f'Answer: {submission.answer_text}\n\n'
                'Return a JSON object with keys: band_score, criteria_scores, feedback, strengths, weaknesses, improvement_suggestions. '
                'Use a band score between 0.0 and 9.0 in 0.5 increments. '
                'If you cannot produce a valid score, still provide feedback and suggestions.'
            ),
        },
    ]


def _build_speaking_prompt(submission):
    transcript_text = submission.transcript or ''
    if not transcript_text:
        transcript_text = 'Transcript unavailable. Evaluate based on prompt and any audio metadata available.'

    return [
        {
            'role': 'system',
            'content': (
                'You are an IELTS speaking examiner. Evaluate the candidate response based on fluency, coherence, lexical resource, pronunciation, and grammatical accuracy.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Prompt: {submission.prompt}\n\n'
                f'Transcript: {transcript_text}\n\n'
                'Return a JSON object with keys: band_score, criteria_scores, feedback, strengths, weaknesses, improvement_suggestions. '
                'Use a band score between 0.0 and 9.0 in 0.5 increments.'
            ),
        },
    ]


def _safe_parse_evaluation_output(content):
    payload = _parse_json_content(content)
    if payload is None:
        band_score = _extract_numeric_score(content)
        return {
            'band_score': band_score,
            'criteria_scores': {},
            'feedback': content,
            'strengths': [],
            'weaknesses': [],
            'improvement_suggestions': [],
        }

    return {
        'band_score': payload.get('band_score'),
        'criteria_scores': payload.get('criteria_scores', {}),
        'feedback': payload.get('feedback', '') or payload.get('comments', ''),
        'strengths': payload.get('strengths', []),
        'weaknesses': payload.get('weaknesses', []),
        'improvement_suggestions': payload.get('improvement_suggestions', []),
    }


def evaluate_writing_submission(submission_id):
    submission = WritingSubmission.objects.get(pk=submission_id)
    if submission.evaluation_status == WritingSubmission.EvaluationStatus.COMPLETED:
        return submission

    evaluation = AIEvaluation.objects.create(
        writing_submission=submission,
        status=AIEvaluation.Status.STARTED,
        provider='openai',
        model_name=settings.OPENAI_MODEL,
        prompt_version=settings.OPENAI_PROMPT_VERSION,
        request_payload={},
        response_payload={},
        started_at=timezone.now(),
    )

    client = _create_openai_client()
    messages = _build_writing_prompt(submission)
    request_payload = {
        'model': settings.OPENAI_MODEL,
        'messages': messages,
        'temperature': 0.0,
    }
    evaluation.request_payload = request_payload
    evaluation.save(update_fields=['request_payload'])

    try:
        response = client.ChatCompletion.create(**request_payload)
        response_payload = _format_response_to_dict(response)
        evaluation.response_payload = response_payload

        content = response['choices'][0]['message']['content']
        parsed = _safe_parse_evaluation_output(content)
        evaluation.score = parsed['band_score']
        evaluation.criteria_scores = parsed['criteria_scores']
        evaluation.feedback = parsed['feedback']
        evaluation.strengths = parsed['strengths']
        evaluation.weaknesses = parsed['weaknesses']
        evaluation.improvement_suggestions = parsed['improvement_suggestions']
        evaluation.status = AIEvaluation.Status.COMPLETED
        evaluation.completed_at = timezone.now()
        evaluation.save(update_fields=[
            'response_payload',
            'score',
            'criteria_scores',
            'feedback',
            'strengths',
            'weaknesses',
            'improvement_suggestions',
            'status',
            'completed_at',
        ])

        submission.evaluation_status = WritingSubmission.EvaluationStatus.COMPLETED
        submission.band_score = parsed['band_score']
        submission.criteria_scores = parsed['criteria_scores']
        submission.ai_feedback = {
            'feedback': parsed['feedback'],
            'strengths': parsed['strengths'],
            'weaknesses': parsed['weaknesses'],
            'improvement_suggestions': parsed['improvement_suggestions'],
        }
        submission.model_name = settings.OPENAI_MODEL
        submission.prompt_version = settings.OPENAI_PROMPT_VERSION
        submission.save(update_fields=[
            'evaluation_status',
            'band_score',
            'criteria_scores',
            'ai_feedback',
            'model_name',
            'prompt_version',
        ])

        return submission
    except Exception as exc:
        evaluation.status = AIEvaluation.Status.FAILED
        evaluation.error_message = str(exc)
        evaluation.completed_at = timezone.now()
        evaluation.save(update_fields=['status', 'error_message', 'completed_at'])

        submission.evaluation_status = WritingSubmission.EvaluationStatus.FAILED
        submission.save(update_fields=['evaluation_status'])
        raise


def evaluate_speaking_submission(submission_id):
    submission = SpeakingAudioSubmission.objects.get(pk=submission_id)
    if submission.evaluation_status == SpeakingAudioSubmission.EvaluationStatus.COMPLETED:
        return submission

    evaluation = AIEvaluation.objects.create(
        speaking_submission=submission,
        status=AIEvaluation.Status.STARTED,
        provider='openai',
        model_name=settings.OPENAI_MODEL,
        prompt_version=settings.OPENAI_PROMPT_VERSION,
        request_payload={},
        response_payload={},
        started_at=timezone.now(),
    )

    if not submission.transcript:
        evaluation.status = AIEvaluation.Status.FAILED
        evaluation.error_message = 'Missing transcript for speaking evaluation.'
        evaluation.completed_at = timezone.now()
        evaluation.save(update_fields=['status', 'error_message', 'completed_at'])
        submission.evaluation_status = SpeakingAudioSubmission.EvaluationStatus.FAILED
        submission.save(update_fields=['evaluation_status'])
        return submission

    client = _create_openai_client()
    messages = _build_speaking_prompt(submission)
    request_payload = {
        'model': settings.OPENAI_MODEL,
        'messages': messages,
        'temperature': 0.0,
    }

    evaluation.request_payload = request_payload
    evaluation.save(update_fields=['request_payload'])

    try:
        response = client.ChatCompletion.create(**request_payload)
        response_payload = _format_response_to_dict(response)
        evaluation.response_payload = response_payload

        content = response['choices'][0]['message']['content']
        parsed = _safe_parse_evaluation_output(content)
        evaluation.score = parsed['band_score']
        evaluation.criteria_scores = parsed['criteria_scores']
        evaluation.feedback = parsed['feedback']
        evaluation.strengths = parsed['strengths']
        evaluation.weaknesses = parsed['weaknesses']
        evaluation.improvement_suggestions = parsed['improvement_suggestions']
        evaluation.status = AIEvaluation.Status.COMPLETED
        evaluation.completed_at = timezone.now()
        evaluation.save(update_fields=[
            'response_payload',
            'score',
            'criteria_scores',
            'feedback',
            'strengths',
            'weaknesses',
            'improvement_suggestions',
            'status',
            'completed_at',
        ])

        submission.evaluation_status = SpeakingAudioSubmission.EvaluationStatus.COMPLETED
        submission.band_score = parsed['band_score']
        submission.criteria_scores = parsed['criteria_scores']
        submission.ai_feedback = {
            'feedback': parsed['feedback'],
            'strengths': parsed['strengths'],
            'weaknesses': parsed['weaknesses'],
            'improvement_suggestions': parsed['improvement_suggestions'],
        }
        submission.model_name = settings.OPENAI_MODEL
        submission.prompt_version = settings.OPENAI_PROMPT_VERSION
        submission.save(update_fields=[
            'evaluation_status',
            'band_score',
            'criteria_scores',
            'ai_feedback',
            'model_name',
            'prompt_version',
        ])

        return submission
    except Exception as exc:
        evaluation.status = AIEvaluation.Status.FAILED
        evaluation.error_message = str(exc)
        evaluation.completed_at = timezone.now()
        evaluation.save(update_fields=['status', 'error_message', 'completed_at'])

        submission.evaluation_status = SpeakingAudioSubmission.EvaluationStatus.FAILED
        submission.save(update_fields=['evaluation_status'])
        raise
