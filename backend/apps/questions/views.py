from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdminUser
from .models import AnswerOption, CorrectAnswerRule, Question, QuestionGroup
from .serializers import (
    AnswerOptionSerializer,
    CorrectAnswerRuleSerializer,
    QuestionGroupSerializer,
    QuestionSerializer,
)


class AdminQuestionGroupViewSet(viewsets.ModelViewSet):
    queryset = QuestionGroup.objects.all()
    serializer_class = QuestionGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AdminQuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AdminAnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AdminCorrectAnswerRuleViewSet(viewsets.ModelViewSet):
    queryset = CorrectAnswerRule.objects.all()
    serializer_class = CorrectAnswerRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
