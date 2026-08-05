from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdminUser
from .models import SpeakingAudioSubmission
from .serializers import SpeakingAudioSubmissionSerializer


class SpeakingAudioSubmissionViewSet(viewsets.ModelViewSet):
    queryset = SpeakingAudioSubmission.objects.all()
    serializer_class = SpeakingAudioSubmissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
