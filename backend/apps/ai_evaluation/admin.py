from django.contrib import admin

from .models import AIEvaluation


@admin.register(AIEvaluation)
class AIEvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'provider', 'model_name', 'created_at', 'completed_at')
    list_filter = ('status', 'provider')
    search_fields = ('provider', 'model_name', 'error_message')
