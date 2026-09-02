from django import forms
from django.contrib import admin
from django.db import models

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
    list_display = ('title', 'section', 'order', 'is_required', 'question_count')
    list_filter = ('is_required', 'section__section_type')
    search_fields = ('title', 'instruction', 'section__title')
    inlines = [QuestionInline]
    readonly_fields = ('question_count',)

    @admin.display(description='Questions')
    def question_count(self, obj):
        return obj.questions.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'question_group', 'type', 'order', 'points', 'is_active')
    list_filter = ('type', 'is_active', 'question_group__section__section_type')
    search_fields = ('prompt', 'instruction', 'difficulty', 'question_group__title')
    inlines = [AnswerOptionInline, CorrectAnswerRuleInline]
    formfield_overrides = {
        models.JSONField: {'widget': forms.Textarea(attrs={'rows': 8, 'class': 'vLargeTextField'})}
    }
    fieldsets = (
        ('Question content', {
            'fields': ('question_group', 'type', 'prompt', 'instruction', 'order', 'points', 'difficulty', 'tags')
        }),
        ('Validation', {
            'fields': ('options_json', 'correct_answer_json', 'validation_rules_json', 'explanation', 'is_active')
        }),
    )


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'text')
    search_fields = ('text', 'question__prompt')


@admin.register(CorrectAnswerRule)
class CorrectAnswerRuleAdmin(admin.ModelAdmin):
    list_display = ('question', 'rule_type', 'is_active')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('question__prompt', 'metadata')
