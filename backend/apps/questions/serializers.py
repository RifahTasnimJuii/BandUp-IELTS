from rest_framework import serializers

from .models import AnswerOption, CorrectAnswerRule, Question, QuestionGroup


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = '__all__'


class CorrectAnswerRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectAnswerRule
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionGroup
        fields = '__all__'
