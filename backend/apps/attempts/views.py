from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.common.permissions import IsAdminUser
from apps.questions.models import Question
from apps.test_catalog.models import Test
from .models import AnswerResponse, Attempt, ExamViolationEvent
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
        }
        if attempt.expires_at and attempt.started_at:
            data['remaining_seconds'] = int((attempt.expires_at - timezone.now()).total_seconds())
        return Response(data)

    @action(detail=True, methods=['post'], url_path='autosave')
    def autosave(self, request, pk=None):
        attempt = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = AnswerResponseSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer_response, created = AnswerResponse.objects.update_or_create(
            attempt=attempt,
            question=Question.objects.get(pk=serializer.validated_data['question_id']),
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

        task_grade_and_finalize_attempt.delay(str(attempt.id))
        return Response(
            {
                'detail': 'Attempt submitted and grading queued.',
                'attempt_id': attempt.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


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
