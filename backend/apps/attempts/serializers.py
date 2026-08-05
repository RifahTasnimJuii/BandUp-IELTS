from rest_framework import serializers

from apps.questions.models import Question
from .models import AnswerResponse, Attempt, AttemptSectionState, ExamViolationEvent


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = '__all__'


class AttemptSectionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptSectionState
        fields = '__all__'


class AnswerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerResponse
        fields = '__all__'


class ExamViolationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamViolationEvent
        fields = '__all__'


class AttemptStartSerializer(serializers.Serializer):
    test_id = serializers.UUIDField()
    mode = serializers.ChoiceField(choices=Attempt.Mode.choices)
    client_timezone = serializers.CharField(required=False, allow_blank=True)
    locale = serializers.CharField(required=False, allow_blank=True)
    device_info = serializers.JSONField(required=False)


class AttemptHeartbeatSerializer(serializers.Serializer):
    last_heartbeat_at = serializers.DateTimeField()


class ExamViolationEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamViolationEvent
        fields = ['violation_type', 'details', 'metadata', 'severity', 'auto_action_taken']


class AnswerResponseSaveSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = AnswerResponse
        fields = ['question_id', 'value_json', 'answer_text', 'selected_options', 'is_flagged', 'is_cleared', 'is_locked']

    def create(self, validated_data):
        question_id = validated_data.pop('question_id')
        question = Question.objects.get(pk=question_id)
        return AnswerResponse.objects.create(question=question, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
