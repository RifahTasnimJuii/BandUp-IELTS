# reading/admin.py (SIMPLIFIED VERSION)
from django.contrib import admin
from .models import ReadingTest, ReadingQuestion, UserReadingAttempt, UserAnswer

class ReadingTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'test_number', 'test_type', 'source', 'is_active')
    list_filter = ('test_type', 'source', 'is_active')
    search_fields = ('title', 'passage_text')
    fields = ('title', 'test_number', 'test_type', 'source', 'time_limit',
              'passage_title', 'passage_text', 'is_active')

class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_number', 'test', 'question_type', 'correct_answer')
    list_filter = ('question_type', 'test')
    search_fields = ('text', 'correct_answer')
    ordering = ('test', 'question_number')

admin.site.register(ReadingTest, ReadingTestAdmin)
admin.site.register(ReadingQuestion, ReadingQuestionAdmin)
admin.site.register(UserReadingAttempt)
admin.site.register(UserAnswer)