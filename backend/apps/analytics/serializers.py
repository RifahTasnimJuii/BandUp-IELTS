from rest_framework import serializers


class DashboardAnalyticsSerializer(serializers.Serializer):
    tests_taken = serializers.IntegerField(required=False)
    overall_band = serializers.FloatField(required=False, allow_null=True)
    module_bands = serializers.DictField(required=False)
    weak_area = serializers.DictField(required=False, allow_null=True)
    recent_attempts = serializers.ListField(required=False)
    readiness_score = serializers.IntegerField(required=False)
    overall_average_band = serializers.FloatField(required=False, allow_null=True)
    section_averages = serializers.DictField(required=False)
    weak_areas = serializers.ListField(required=False)
    recent_scores = serializers.ListField(required=False)
    writing_criteria = serializers.DictField(required=False)
    speaking_criteria = serializers.DictField(required=False)


class ScoreTrendSerializer(serializers.Serializer):
    label = serializers.CharField(required=False, allow_blank=True)
    band = serializers.FloatField(required=False, allow_null=True)
