from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('reading/', include('reading.urls')),
    path('listening/', include('listening.urls')),
    path('writing/', include('writing.urls')),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)