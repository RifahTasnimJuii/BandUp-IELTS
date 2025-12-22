from django.db import models
from django.contrib.auth.models import User

class WritingPrompt(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class WritingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.ForeignKey(WritingPrompt, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Writing Submission"
