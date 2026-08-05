from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttemptStartAPIView, AttemptViewSet

router = DefaultRouter()
router.register('attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('start/', AttemptStartAPIView.as_view(), name='attempt-start'),
    path('', include(router.urls)),
]
