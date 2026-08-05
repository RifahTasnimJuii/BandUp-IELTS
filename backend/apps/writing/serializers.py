from rest_framework import serializers

from .models import WritingSubmission


class WritingSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingSubmission
        fields = '__all__'


class WritingSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingSubmission
        fields = [
            'attempt',
            'question',
            'task_number',
            'prompt',
            'answer_text',
            'below_min_word_warning',
            'evaluation_status',
            'model_name',
            'prompt_version',
            'token_usage',
            'estimated_cost',
            'latency_ms',
            'manual_override_score',
            'manual_feedback',
        ]
