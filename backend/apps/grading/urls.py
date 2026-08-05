from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminScoringBandMappingViewSet

router = DefaultRouter()
router.register('scoring-band-mappings', AdminScoringBandMappingViewSet, basename='admin-scoring-band-mapping')

urlpatterns = [
    path('', include(router.urls)),
]
