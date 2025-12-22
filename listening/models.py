from django.db import models
from django.contrib.auth.models import User


class ListeningTest(models.Model):
    title = models.CharField(max_length=200)
    test_number = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='listening_audio/', blank=True, null=True)
    transcript = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class ListeningSection(models.Model):
    test = models.ForeignKey(ListeningTest, related_name='sections', on_delete=models.CASCADE)
    section_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test.title} - Section {self.section_number}"


class ListeningQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('form_completion', 'Form Completion'),
        ('map_labeling', 'Map Labeling'),
        ('sentence_completion', 'Sentence Completion'),
    ]
    section = models.ForeignKey(ListeningSection, related_name='questions', on_delete=models.CASCADE)
    question_number = models.IntegerField()
    text = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    correct_answer = models.TextField()
    field_count = models.IntegerField(default=1)  # For form completion
    time_start = models.IntegerField(default=0)  # seconds in audio
    time_end = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.section} - Q{self.question_number}"

    def get_choices(self):
        """
        Return multiple choice options.
        First checks for QuestionOption objects, falls back to old format.
        """
        # If we have QuestionOption objects, use them
        if hasattr(self, 'options') and self.options.exists():
            options_list = []
            for option in self.options.all():
                options_list.append({
                    'label': option.option_label,
                    'value': option.option_label,
                    'text': option.option_text,
                    'is_correct': option.is_correct
                })
            return options_list

        # Fallback to old format (for backward compatibility)
        # Old format: correct_answer contains semicolon-separated options
        # The correct answer is the first option in the list
        choices = []
        parts = self.correct_answer.split(';')
        if len(parts) > 1:
            # Assume first option is correct (for backward compatibility)
            for i, part in enumerate(parts):
                label = chr(65 + i)  # A, B, C, D...
                choices.append({
                    'label': label,
                    'value': label,
                    'text': part.strip(),
                    'is_correct': (i == 0)  # First option is correct in old format
                })
        else:
            # Single answer - not multiple choice
            choices = [{
                'label': 'A',
                'value': 'A',
                'text': self.correct_answer,
                'is_correct': True
            }]

        return choices

    def check_answer(self, user_answer):
        """Check if user's answer is correct"""
        if self.question_type == 'multiple_choice':
            # For multiple choice, check against correct_answer field
            correct_answers = [c.strip().lower() for c in self.correct_answer.split(';')]
            return user_answer.lower() in correct_answers
        else:
            # For other types
            correct_answers = [c.strip().lower() for c in self.correct_answer.split(';')]
            return user_answer.lower() in correct_answers


# ADD THIS AT THE END, after ListeningQuestion is defined
class QuestionOption(models.Model):
    """Stores options for multiple choice questions"""
    question = models.ForeignKey(ListeningQuestion, related_name='options', on_delete=models.CASCADE)
    option_label = models.CharField(max_length=10)  # A, B, C, D or 1, 2, 3, etc.
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['option_label']

    def __str__(self):
        return f"{self.option_label}: {self.option_text[:50]}"


class UserListeningAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    band_score = models.FloatField(default=0)
    time_taken = models.IntegerField(default=0)  # seconds
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} Attempt"