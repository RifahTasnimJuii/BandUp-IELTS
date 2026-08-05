from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdminUser
from .models import ScoringBandMapping
from .serializers import ScoringBandMappingSerializer


class AdminScoringBandMappingViewSet(viewsets.ModelViewSet):
    queryset = ScoringBandMapping.objects.all()
    serializer_class = ScoringBandMappingSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
