from django.urls import path
from . import views

urlpatterns = [
    path('', views.writing_prompts_view, name='writing_prompts'),
    path('prompt/<int:prompt_id>/', views.writing_prompt_view, name='writing_prompt'),
    #path('submit/<int:prompt_id>/', views.submit_writing, name='submit_writing'),
    path('feedback/<int:submission_id>/', views.writing_feedback_view, name='writing_feedback'),
    path('progress/', views.writing_progress_view, name='writing_progress'),
]