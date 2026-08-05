from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminAnswerOptionViewSet,
    AdminCorrectAnswerRuleViewSet,
    AdminQuestionGroupViewSet,
    AdminQuestionViewSet,
)

router = DefaultRouter()
router.register('question-groups', AdminQuestionGroupViewSet, basename='admin-question-group')
router.register('questions', AdminQuestionViewSet, basename='admin-question')
router.register('answer-options', AdminAnswerOptionViewSet, basename='admin-answer-option')
router.register('correct-answer-rules', AdminCorrectAnswerRuleViewSet, basename='admin-correct-answer-rule')

urlpatterns = [
    path('', include(router.urls)),
]
