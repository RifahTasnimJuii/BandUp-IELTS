from django.db import models
from django.contrib.auth.models import User
import json


class ReadingTest(models.Model):
    TEST_TYPES = [
        ('academic', 'Academic'),
        ('general', 'General Training'),
    ]

    SOURCES = [
        ('cambridge_15', 'Cambridge IELTS 15'),
        ('cambridge_16', 'Cambridge IELTS 16'),
        ('cambridge_17', 'Cambridge IELTS 17'),
        ('cambridge_18', 'Cambridge IELTS 18'),
        ('cambridge_19', 'Cambridge IELTS 19'),
        ('cambridge_20', 'Cambridge IELTS 20'),
        ('custom', 'Custom Test'),
    ]

    title = models.CharField(max_length=200)
    test_number = models.IntegerField()
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, default='academic')
    source = models.CharField(max_length=20, choices=SOURCES, default='cambridge_16')
    passage_title = models.CharField(max_length=300)
    passage_text = models.TextField(help_text="Full passage text (avoid copyright material)")
    time_limit = models.IntegerField(default=60, help_text="Time limit in minutes")
    total_questions = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (Test {self.test_number})"

    class Meta:
        ordering = ['test_number', 'id']
        unique_together = ['test_number', 'source']


class ReadingQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false_ng', 'True/False/Not Given'),
        ('matching', 'Matching Headings'),
        ('completion', 'Sentence Completion'),
        ('short_answer', 'Short Answer'),
        ('summary', 'Summary Completion'),
    ]

    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    text = models.TextField(help_text="The question text")
    correct_answer = models.CharField(max_length=500, help_text="Correct answer (for multiple choice, use A,B,C,D)")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for the answer")
    word_limit = models.IntegerField(default=1, help_text="Maximum words allowed for answer")
    choices = models.TextField(blank=True, null=True,
                               help_text="JSON for multiple choice: [{'label':'A','text':'Option A'},...]")

    def __str__(self):
        return f"Q{self.question_number}: {self.text[:50]}..."

    def get_choices(self):
        """Parse choices JSON or return empty list"""
        if self.choices:
            try:
                # Try to parse JSON
                import json
                parsed = json.loads(self.choices)

                # Ensure it's a list
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict):
                    # Convert dict to list of dicts
                    return [parsed]
                else:
                    return []
            except:
                # If JSON parsing fails, try to create basic choices
                try:
                    # For simple format like "A, B, C, D"
                    if ',' in self.choices:
                        choices = []
                        for i, letter in enumerate(self.choices.split(',')):
                            letter = letter.strip()
                            if letter:
                                choices.append({
                                    'label': letter,
                                    'text': f'Option {letter}',
                                    'value': letter
                                })
                        return choices
                except:
                    return []
        return []

    class Meta:
        ordering = ['question_number']
        unique_together = ['test', 'question_number']


class UserReadingAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_attempts')
    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    band_score = models.FloatField()
    time_taken = models.IntegerField(help_text="Time taken in seconds")
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}/{self.total_questions}"

    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', 'completed_at']),
        ]


class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserReadingAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ReadingQuestion, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to Q{self.question.question_number}"

    class Meta:
        unique_together = ['attempt', 'question']