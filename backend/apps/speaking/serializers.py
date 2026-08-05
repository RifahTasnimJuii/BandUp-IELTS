from rest_framework import serializers

from .models import SpeakingAudioSubmission


class SpeakingAudioSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingAudioSubmission
        fields = '__all__'
