from django.contrib import admin

from .models import ScoringBandMapping


@admin.register(ScoringBandMapping)
class ScoringBandMappingAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'test', 'raw_score_min', 'raw_score_max', 'band_score', 'is_default')
    list_filter = ('section_type', 'is_default')
    search_fields = ('description',)
