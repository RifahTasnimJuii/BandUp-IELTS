from django.urls import path
from .views import listening_tests_view, listening_test_view, submit_listening_test, listening_results_view

urlpatterns = [
    path('', listening_tests_view, name='listening_tests'),
    path('test/<int:test_id>/', listening_test_view, name='listening_test'),
    path('submit/<int:test_id>/', submit_listening_test, name='submit_listening_test'),
    path('result/<int:attempt_id>/', listening_results_view, name='listening_results'),
]
