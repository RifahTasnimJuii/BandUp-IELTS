from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdminUser
from .models import AIEvaluation
from .serializers import AIEvaluationSerializer


class AIEvaluationViewSet(viewsets.ModelViewSet):
    queryset = AIEvaluation.objects.all()
    serializer_class = AIEvaluationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
