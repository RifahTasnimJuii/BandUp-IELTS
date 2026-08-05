from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WritingSubmissionViewSet

router = DefaultRouter()
router.register('writing-submissions', WritingSubmissionViewSet, basename='writing-submission')

urlpatterns = [
    path('', include(router.urls)),
]
