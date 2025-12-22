from django.urls import path
from .views import reading_test_list, reading_test, reading_result, reading_review

urlpatterns = [
    path('', reading_test_list, name='tests_list'),
    path('test/<int:test_id>/', reading_test, name='reading_test'),
    path('result/<int:attempt_id>/', reading_result, name='reading_results'),
    path('review/<int:attempt_id>/', reading_review, name='reading_review'),
]
