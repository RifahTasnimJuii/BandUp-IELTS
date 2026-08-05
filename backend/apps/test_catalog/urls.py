from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminAudioAssetViewSet, AdminPassageViewSet, AdminSectionViewSet, AdminTestViewSet

router = DefaultRouter()
router.register('tests', AdminTestViewSet, basename='admin-test')
router.register('sections', AdminSectionViewSet, basename='admin-section')
router.register('passages', AdminPassageViewSet, basename='admin-passage')
router.register('audio-assets', AdminAudioAssetViewSet, basename='admin-audioasset')

urlpatterns = [
    path('', include(router.urls)),
]
