from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attempts.models import Attempt


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        attempts = list(Attempt.objects.filter(user=request.user, state=Attempt.State.COMPLETED).select_related('test').order_by('-started_at', '-created_at'))
        recent_attempts = attempts[:10]
        band_values = [float(attempt.overall_band) for attempt in attempts if attempt.overall_band is not None]
        section_values = {
            'listening': [float(attempt.listening_band) for attempt in attempts if attempt.listening_band is not None],
            'reading': [float(attempt.reading_band) for attempt in attempts if attempt.reading_band is not None],
            'writing': [float(attempt.writing_band) for attempt in attempts if attempt.writing_band is not None],
            'speaking': [float(attempt.speaking_band) for attempt in attempts if attempt.speaking_band is not None],
        }

        def average(values):
            return round(sum(values) / len(values), 2) if values else None

        recent_scores = [
            {'label': attempt.test.title[:20], 'date': attempt.started_at or attempt.created_at, 'band': float(attempt.overall_band)}
            for attempt in recent_attempts
            if attempt.overall_band is not None
        ][::-1]

        module_bands = {module: average(section_values[module]) for module in section_values}
        available_modules = [(module, score) for module, score in module_bands.items() if score is not None]
        weak_area = None
        if available_modules:
            module, score = min(available_modules, key=lambda item: item[1])
            weak_area = {'label': module.title(), 'score': score}

        payload = {
            'tests_taken': len(attempts),
            'overall_band': float(attempts[0].overall_band) if attempts and attempts[0].overall_band is not None else None,
            'overall_average_band': average(band_values),
            'module_bands': module_bands,
            'section_averages': module_bands,
            'weak_area': weak_area,
            'weak_areas': [{'label': module.title(), 'score': score} for module, score in available_modules],
            'recent_scores': recent_scores,
            'score_trend': recent_scores,
            'recent_attempts': [
                {'id': str(attempt.id), 'test_title': attempt.test.title, 'date': attempt.started_at or attempt.created_at, 'overall_band': float(attempt.overall_band) if attempt.overall_band is not None else None}
                for attempt in recent_attempts
            ],
            'readiness_score': min(100, len(attempts) * 20),
        }
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='score-trend')
    def score_trend(self, request):
        attempts = Attempt.objects.filter(user=request.user).exclude(overall_band__isnull=True).order_by('-started_at')[:12]
        payload = [
            {'label': attempt.test.title[:20], 'band': float(attempt.overall_band)}
            for attempt in attempts
            if attempt.overall_band is not None
        ][::-1]
        return Response(payload, status=status.HTTP_200_OK)
