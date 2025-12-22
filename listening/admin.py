from django.contrib import admin
from .models import ListeningTest, ListeningSection, ListeningQuestion, QuestionOption, UserListeningAttempt


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    min_num = 2
    max_num = 6


class ListeningQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_number', 'text', 'question_type', 'section', 'get_correct_answer']
    list_filter = ['question_type', 'section__test']
    search_fields = ['text']
    inlines = [QuestionOptionInline]

    def get_correct_answer(self, obj):
        if obj.question_type == 'multiple_choice' and obj.options.exists():
            correct_option = obj.options.filter(is_correct=True).first()
            return f"{correct_option.option_label}: {correct_option.option_text}" if correct_option else "No correct option set"
        return obj.correct_answer

    get_correct_answer.short_description = 'Correct Answer'


class ListeningSectionAdmin(admin.ModelAdmin):
    list_display = ['section_number', 'title', 'test']
    list_filter = ['test']
    search_fields = ['title', 'description']


class ListeningTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'test_number', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']


class UserListeningAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'total_questions', 'band_score', 'completed_at']
    list_filter = ['test', 'completed_at']
    search_fields = ['user__username']


admin.site.register(ListeningTest, ListeningTestAdmin)
admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningQuestion, ListeningQuestionAdmin)
admin.site.register(UserListeningAttempt, UserListeningAttemptAdmin)