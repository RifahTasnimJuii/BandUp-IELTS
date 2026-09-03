from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.common.permissions import IsAdminUser
from apps.questions.models import Question
from apps.speaking.models import SpeakingAudioSubmission
from django.conf import settings
from apps.writing.models import WritingSubmission
from apps.test_catalog.models import Test
from apps.writing.models import WritingSubmission
from .models import AnswerResponse, Attempt, AttemptSectionState, ExamViolationEvent
from .serializers import (
    AnswerResponseSaveSerializer,
    AnswerResponseSerializer,
    AttemptHeartbeatSerializer,
    AttemptSerializer,
    AttemptStartSerializer,
    ExamViolationEventCreateSerializer,
    ExamViolationEventSerializer,
)
from .tasks import task_grade_and_finalize_attempt


class UserAttemptPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.user == request.user


class AttemptViewSet(viewsets.ModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='state')
    def state(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        data = {
            'id': attempt.id,
            'state': attempt.state,
            'started_at': attempt.started_at,
            'expires_at': attempt.expires_at,
            'submitted_at': attempt.submitted_at,
            'remaining_seconds': None,
            'answers': AnswerResponseSerializer(attempt.answer_responses.all(), many=True).data,
            'section_states': [
                {
                    'section': str(section_state.section_id),
                    'state': section_state.state,
                    'started_at': section_state.started_at,
                    'completed_at': section_state.completed_at,
                }
                for section_state in attempt.section_states.all()
            ],
        }
        if attempt.expires_at and attempt.started_at:
            data['remaining_seconds'] = int((attempt.expires_at - timezone.now()).total_seconds())
        return Response(data)

    @action(detail=True, methods=['get'], url_path='paper')
    def paper(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset().select_related('test'), pk=pk)
        sections = []
        for section in attempt.test.sections.prefetch_related('passages', 'audio_assets', 'question_groups__questions').all():
            passages = section.passages.all()
            audio = section.audio_assets.filter(is_active=True).first()
            audio_parts = section.audio_assets.filter(is_active=True, title__regex=r'^Listening Part [1-4]$').order_by('title')
            question_groups = list(section.question_groups.all())
            sections.append({
                'id': str(section.id),
                'title': section.title,
                'section_type': section.section_type,
                'order': section.order,
                'duration_seconds': section.duration_seconds,
                'instruction_text': section.instruction_text,
                'passage': {
                    'id': str(passages[0].id),
                    'title': passages[0].title,
                    'body_text': passages[0].body_text,
                    'source_note': passages[0].source_note,
                } if passages else None,
                'passages': [
                    {'id': str(passage.id), 'title': passage.title, 'body_text': passage.body_text, 'source_note': passage.source_note}
                    for passage in passages
                ],
                'audio': {
                    'id': str(audio.id),
                    'title': audio.title,
                    'audio_file': audio.audio_file.url if audio.audio_file else None,
                    'duration_seconds': audio.duration_seconds,
                    'playback_policy': audio.playback_policy,
                    'transcript': audio.transcript,
                } if audio else None,
                'parts': [
                    {
                        'order': group.order,
                        'title': group.title,
                        'audio_url': next((part.audio_file.url for part in audio_parts if part.title == f'Listening Part {group.order}' and part.audio_file), None),
                        'questions': [
                            {
                                'id': str(question.id), 'order': question.order, 'type': question.type,
                                'prompt': question.prompt, 'instruction': question.instruction,
                                'points': question.points, 'prompt_audio_url': question.prompt_audio_file.url if question.prompt_audio_file else None,
                                'options': [{'id': str(option.id), 'order': option.order, 'text': option.text} for option in question.answer_options.all()] or [{'id': str(index), 'order': index, 'text': option} for index, option in enumerate(question.options_json or [], 1) if isinstance(option, str)],
                                'validation_rules': question.validation_rules_json,
                                'visual_json': question.options_json if isinstance(question.options_json, dict) else None,
                                'question_group': {'id': str(group.id), 'title': group.title, 'instruction': group.instruction, 'order': group.order, 'passage_id': str(group.passage_id) if group.passage_id else None},
                            }
                            for question in group.questions.all()
                        ],
                    }
                    for group in question_groups if section.section_type == 'listening'
                ],
                'speaking_audio_assets': [
                    {'title': asset.title, 'audio_url': asset.audio_file.url if asset.audio_file else None}
                    for asset in section.audio_assets.filter(is_active=True)
                    if section.section_type == 'speaking' and asset.audio_file
                ],
                'question_groups': [
                    {
                        'id': str(group.id),
                        'title': group.title,
                        'instruction': group.instruction,
                        'order': group.order,
                        'passage_id': str(group.passage_id) if group.passage_id else None,
                        'questions': [
                            {
                                'id': str(question.id),
                                'order': question.order,
                                'type': question.type,
                                'prompt': question.prompt,
                                'prompt_audio_url': question.prompt_audio_file.url if question.prompt_audio_file else None,
                                'instruction': question.instruction,
                                'points': question.points,
                                'options': [
                                    {'id': str(option.id), 'order': option.order, 'text': option.text}
                                    for option in question.answer_options.all()
                                ] or [
                                    {'id': str(index), 'order': index, 'text': option}
                                    for index, option in enumerate(question.options_json or [], 1)
                                    if isinstance(option, str)
                                ],
                                'validation_rules': question.validation_rules_json,
                                'visual_json': question.options_json if isinstance(question.options_json, dict) else None,
                                'question_group': {'id': str(group.id), 'title': group.title, 'instruction': group.instruction, 'order': group.order, 'passage_id': str(group.passage_id) if group.passage_id else None},
                            }
                            for question in group.questions.all()
                        ],
                    }
                    for group in section.question_groups.all()
                ],
            })
        return Response({
            'attempt_id': str(attempt.id),
            'test': {'id': str(attempt.test.id), 'title': attempt.test.title, 'slug': attempt.test.slug},
            'server_time': timezone.now(),
            'expires_at': attempt.expires_at,
            'sections': sections,
        })

    @action(detail=True, methods=['post'], url_path=r'sections/(?P<section_id>[^/.]+)/start')
    def start_section(self, request, pk=None, section_id=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        section = get_object_or_404(attempt.test.sections, pk=section_id)
        section_state, _ = attempt.section_states.update_or_create(
            section=section,
            defaults={
                'state': AttemptSectionState.SectionState.ACTIVE,
                'started_at': timezone.now(),
                'remaining_seconds': section.duration_seconds,
                'duration_seconds': section.duration_seconds,
                'is_locked': False,
            },
        )
        attempt.current_section = section
        attempt.state = Attempt.State.IN_PROGRESS
        attempt.save(update_fields=['current_section', 'state'])
        return Response({'section': str(section_state.section_id), 'state': section_state.state})

    @action(detail=True, methods=['post'], url_path=r'sections/(?P<section_id>[^/.]+)/complete')
    def complete_section(self, request, pk=None, section_id=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        section = get_object_or_404(attempt.test.sections, pk=section_id)
        section_state, _ = attempt.section_states.update_or_create(
            section=section,
            defaults={
                'state': AttemptSectionState.SectionState.COMPLETED,
                'completed_at': timezone.now(),
                'remaining_seconds': 0,
                'duration_seconds': section.duration_seconds,
                'is_locked': True,
            },
        )
        return Response({'section': str(section_state.section_id), 'state': section_state.state})

    @action(detail=True, methods=['post'], url_path='autosave')
    def autosave(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = AnswerResponseSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = get_object_or_404(
            Question.objects.filter(question_group__section__test=attempt.test),
            pk=serializer.validated_data['question_id'],
        )
        answer_response, created = AnswerResponse.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'value_json': serializer.validated_data.get('value_json', {}),
                'answer_text': serializer.validated_data.get('answer_text'),
                'selected_options': serializer.validated_data.get('selected_options'),
                'is_flagged': serializer.validated_data.get('is_flagged', False),
                'is_cleared': serializer.validated_data.get('is_cleared', False),
                'is_locked': serializer.validated_data.get('is_locked', False),
            },
        )
        return Response(AnswerResponseSerializer(answer_response).data)

    @action(detail=True, methods=['post'], url_path='heartbeat')
    def heartbeat(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = AttemptHeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt.last_heartbeat_at = serializer.validated_data['last_heartbeat_at']
        attempt.save(update_fields=['last_heartbeat_at'])
        return Response({'detail': 'Heartbeat recorded.'})

    @action(detail=True, methods=['post'], url_path='violations')
    def violations(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ExamViolationEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(attempt=attempt)
        return Response(ExamViolationEventSerializer(event).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        if attempt.state not in [Attempt.State.CREATED, Attempt.State.IN_PROGRESS]:
            return Response(
                {'detail': 'Attempt cannot be submitted from its current state.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        attempt.answer_responses.filter(is_locked=False).update(
            is_locked=True,
            locked_at=now,
            submitted_at=now,
        )
        attempt.state = Attempt.State.SUBMITTED
        attempt.submitted_at = now
        attempt.ended_at = now
        attempt.save(update_fields=['state', 'submitted_at', 'ended_at'])

        self._create_writing_submissions(attempt)

        task_grade_and_finalize_attempt.delay(str(attempt.id))
        return Response(
            {
                'detail': 'Attempt submitted and grading queued.',
                'attempt_id': attempt.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @staticmethod
    def _create_writing_submissions(attempt):
        for question in Question.objects.filter(
            question_group__section__test=attempt.test,
            type=Question.QuestionType.WRITING_PROMPT,
        ):
            answer = attempt.answer_responses.filter(question=question).first()
            answer_text = (answer.answer_text if answer else '') or ''
            if not answer_text.strip():
                continue
            task_number = question.correct_answer_json.get('task_number', question.order) if isinstance(question.correct_answer_json, dict) else question.order
            WritingSubmission.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'task_number': task_number,
                    'prompt': question.prompt,
                    'answer_text': answer_text,
                    'evaluation_status': WritingSubmission.EvaluationStatus.PENDING,
                },
            )

    @action(detail=True, methods=['post'], url_path='speaking/upload')
    def speaking_upload(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        question = get_object_or_404(
            Question.objects.filter(question_group__section__test=attempt.test, type=Question.QuestionType.SPEAKING_PROMPT),
            pk=request.data.get('question_id'),
        )
        audio = request.FILES.get('audio')
        if audio is None:
            return Response({'detail': 'An audio file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        path = default_storage.save(f'speaking_submissions/{attempt.id}/{audio.name}', audio)
        prompt_data = question.correct_answer_json if isinstance(question.correct_answer_json, dict) else {}
        submission, _ = SpeakingAudioSubmission.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'part_number': question.order,
                'prompt': question.prompt,
                'storage_key': path,
                'audio_file_url_method': SpeakingAudioSubmission.AudioFileUrlMethod.PRIVATE_MEDIA,
                'duration_seconds': int(prompt_data.get('recording_seconds', 0)),
                'mime_type': audio.content_type or 'audio/webm',
                'prep_seconds_allowed': int(prompt_data.get('prep_seconds', 0)),
                'consent_given': bool(getattr(request.user.profile, 'speaking_audio_consent', False)),
                'evaluation_status': SpeakingAudioSubmission.EvaluationStatus.PENDING_HUMAN_REVIEW if not getattr(settings, 'OPENAI_API_KEY', '') else SpeakingAudioSubmission.EvaluationStatus.PENDING,
            },
        )
        return Response({'id': str(submission.id), 'status': 'Recorded', 'evaluation_status': submission.evaluation_status}, status=status.HTTP_201_CREATED)


class AttemptStartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttemptStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test = get_object_or_404(Test, pk=serializer.validated_data['test_id'])
        attempt = Attempt.objects.create(
            user=request.user,
            test=test,
            mode=serializer.validated_data['mode'],
            state=Attempt.State.CREATED,
            started_at=timezone.now(),
            server_start_time=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(minutes=120),
            client_timezone=serializer.validated_data.get('client_timezone', ''),
            locale=serializer.validated_data.get('locale', ''),
            device_info=serializer.validated_data.get('device_info', {}),
        )
        return Response(
            {
                'attempt_id': attempt.id,
                'started_at': attempt.started_at,
                'expires_at': attempt.expires_at,
                'server_time': timezone.now(),
                'config': {
                    'heartbeat_interval_seconds': 30,
                    'autosave_interval_seconds': 15,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class AttemptResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _serialize_feedback(self, submission):
        if submission is None:
            return None

        ai_payload = submission.ai_feedback or {}
        criteria = submission.criteria_scores or {}
        return {
            'status': submission.evaluation_status,
            'band_score': submission.band_score,
            'criteria_scores': criteria,
            'strengths': ai_payload.get('strengths', submission.strengths or []),
            'weaknesses': ai_payload.get('weaknesses', submission.weaknesses or []),
            'improvement_suggestions': ai_payload.get('improvement_suggestions', submission.improvement_suggestions or []),
            'feedback': ai_payload.get('feedback', '') or getattr(submission, 'prompt', ''),
            'criterion_feedback': ai_payload.get('criterion_feedback', {}),
        }

    def get(self, request, attempt_id):
        attempt = get_object_or_404(Attempt.objects.select_related('test'), pk=attempt_id, user=request.user)

        objective_review = []
        for answer in attempt.answer_responses.select_related('question').all():
            question = answer.question
            if question.type in [Question.QuestionType.WRITING_PROMPT, Question.QuestionType.SPEAKING_PROMPT]:
                continue

            user_answer = answer.answer_text
            if user_answer is None and answer.selected_options:
                user_answer = answer.selected_options
            if user_answer is None:
                user_answer = answer.value_json if isinstance(answer.value_json, (str, list, dict)) else None

            correct_answer = question.correct_answer_json
            if isinstance(correct_answer, dict):
                correct_answer = correct_answer.get('answer') or correct_answer.get('correct_answer') or correct_answer.get('value')

            expected = question.correct_answer_json.get('answer') if isinstance(question.correct_answer_json, dict) else question.correct_answer_json
            if question.type in [Question.QuestionType.MCQ_SINGLE, Question.QuestionType.TRUE_FALSE_NOT_GIVEN, Question.QuestionType.YES_NO_NOT_GIVEN]:
                is_correct = bool(answer.selected_options) and str(answer.selected_options[0]).strip().lower() == str(expected).strip().lower()
            elif question.type == Question.QuestionType.MCQ_MULTIPLE:
                is_correct = set(map(str, answer.selected_options or [])) == set(map(str, expected or []))
            else:
                is_correct = bool(user_answer) and str(user_answer).strip().lower() == str(expected).strip().lower()

            objective_review.append({
                'id': str(answer.id),
                'question_number': question.order,
                'question_label': f'Q{question.order}',
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
            })

        writing_submission = attempt.writing_submissions.order_by('-submitted_at').first()
        speaking_submission = attempt.speaking_submissions.order_by('-uploaded_at').first()

        payload = {
            'attempt_id': str(attempt.id),
            'overall_band': float(attempt.overall_band) if attempt.overall_band is not None else None,
            'is_review_allowed': bool(attempt.is_review_allowed),
            'section_scores': {
                'listening': float(attempt.listening_band) if attempt.listening_band is not None else None,
                'reading': float(attempt.reading_band) if attempt.reading_band is not None else None,
                'writing': float(attempt.writing_band) if attempt.writing_band is not None else None,
                'speaking': float(attempt.speaking_band) if attempt.speaking_band is not None else None,
            },
            'objective_review': objective_review,
            'writing_feedback': self._serialize_feedback(writing_submission),
            'speaking_feedback': self._serialize_feedback(speaking_submission),
            'status': attempt.state,
        }

        return Response(payload, status=status.HTTP_200_OK)
