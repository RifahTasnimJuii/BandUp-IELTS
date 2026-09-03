from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import JsonResponse

from apps.attempts.views import AttemptResultAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', lambda request: JsonResponse({'status': 'ok'})),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/profile/', include('apps.accounts.urls')),
    path('api/', include('apps.test_catalog.urls')),
    path('api/questions/', include('apps.questions.urls')),
    path('api/grading/', include('apps.grading.urls')),
    path('api/attempts/', include('apps.attempts.urls')),
    path('api/results/<uuid:attempt_id>/', AttemptResultAPIView.as_view(), name='attempt-result'),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/admin/', include('apps.admin_dashboard.urls')),
    path('api/writing/', include('apps.writing.urls')),
    path('api/speaking/', include('apps.speaking.urls')),
    path('api/ai-evaluation/', include('apps.ai_evaluation.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
