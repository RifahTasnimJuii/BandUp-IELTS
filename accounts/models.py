from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_band = models.FloatField(default=7.0)
    target_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    study_hours_per_week = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



