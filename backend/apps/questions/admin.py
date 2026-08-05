from django.contrib import admin

from .models import AnswerOption, CorrectAnswerRule, Question, QuestionGroup


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 0
    fields = ('text', 'order', 'explanation')


class CorrectAnswerRuleInline(admin.StackedInline):
    model = CorrectAnswerRule
    extra = 0
    fields = (
        'rule_type',
        'accepted_answers',
        'value',
        'case_sensitive',
        'trim_whitespace',
        'ignore_punctuation',
        'max_words',
        'min_words',
        'partial_credit',
        'points_override',
        'is_active',
    )


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ('type', 'prompt', 'instruction', 'order', 'points', 'is_active')


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'is_required')
    list_filter = ('is_required',)
    search_fields = ('title', 'instruction')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'question_group', 'type', 'order', 'points', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('prompt', 'instruction', 'difficulty')
    inlines = [AnswerOptionInline, CorrectAnswerRuleInline]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'text')
    search_fields = ('text',)


@admin.register(CorrectAnswerRule)
class CorrectAnswerRuleAdmin(admin.ModelAdmin):
    list_display = ('question', 'rule_type', 'is_active')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('metadata',)
