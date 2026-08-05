from django.urls import path

from .views import ConsentView, LoginView, LogoutView, MeView, RegisterView, TokenRefreshViewCustom

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('me/consent/', ConsentView.as_view(), name='auth-consent'),
]
