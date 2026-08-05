from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AIEvaluationViewSet

router = DefaultRouter()
router.register('ai-evaluations', AIEvaluationViewSet, basename='ai-evaluation')

urlpatterns = [
    path('', include(router.urls)),
]
