from django.contrib import admin
from .models import PlatformReview

@admin.register(PlatformReview)
class PlatformReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('user__username', 'comment')

