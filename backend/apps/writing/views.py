from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdminUser
from .models import WritingSubmission
from .serializers import WritingSubmissionSerializer


class WritingSubmissionViewSet(viewsets.ModelViewSet):
    queryset = WritingSubmission.objects.all()
    serializer_class = WritingSubmissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
