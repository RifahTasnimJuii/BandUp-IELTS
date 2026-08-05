from rest_framework import serializers

from .models import ScoringBandMapping


class ScoringBandMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringBandMapping
        fields = '__all__'

    def validate(self, data):
        raw_score_min = data.get('raw_score_min')
        raw_score_max = data.get('raw_score_max')
        if raw_score_min is not None and raw_score_max is not None and raw_score_min >= raw_score_max:
            raise serializers.ValidationError('raw_score_max must be greater than raw_score_min.')
        return data
