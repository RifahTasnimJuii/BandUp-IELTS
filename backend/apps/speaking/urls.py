from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SpeakingAudioSubmissionViewSet

router = DefaultRouter()
router.register('speaking-submissions', SpeakingAudioSubmissionViewSet, basename='speaking-submission')

urlpatterns = [
    path('', include(router.urls)),
]
