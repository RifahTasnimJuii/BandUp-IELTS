from rest_framework import serializers

from .models import AIEvaluation


class AIEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEvaluation
        fields = '__all__'
