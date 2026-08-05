from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.test_catalog.models import AudioAsset, Passage, Section


class QuestionGroup(UUIDModel, TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='question_groups')
    title = models.CharField(max_length=255)
    instruction = models.TextField(blank=True)
    passage = models.ForeignKey(Passage, on_delete=models.SET_NULL, null=True, blank=True, related_name='question_groups')
    audio_asset = models.ForeignKey(AudioAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='question_groups')
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)

    class Meta:
        ordering = ['section', 'order']

    def __str__(self):
        return self.title


class Question(UUIDModel, TimeStampedModel):
    class QuestionType(models.TextChoices):
        MCQ_SINGLE = 'mcq_single', 'MCQ Single'
        MCQ_MULTIPLE = 'mcq_multiple', 'MCQ Multiple'
        TRUE_FALSE_NOT_GIVEN = 'true_false_not_given', 'True/False/Not Given'
        YES_NO_NOT_GIVEN = 'yes_no_not_given', 'Yes/No/Not Given'
        FILL_BLANK = 'fill_blank', 'Fill Blank'
        SENTENCE_COMPLETION = 'sentence_completion', 'Sentence Completion'
        SUMMARY_COMPLETION = 'summary_completion', 'Summary Completion'
        MATCHING_HEADINGS = 'matching_headings', 'Matching Headings'
        MATCHING_ITEMS = 'matching_items', 'Matching Items'
        SHORT_ANSWER = 'short_answer', 'Short Answer'
        WRITING_PROMPT = 'writing_prompt', 'Writing Prompt'
        SPEAKING_PROMPT = 'speaking_prompt', 'Speaking Prompt'

    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=32, choices=QuestionType.choices)
    prompt = models.TextField()
    instruction = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    points = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    options_json = models.JSONField(default=list, blank=True)
    correct_answer_json = models.JSONField(default=dict, blank=True)
    validation_rules_json = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=64, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['question_group', 'order']

    def clean(self):
        if self.type in [
            self.QuestionType.MCQ_SINGLE,
            self.QuestionType.MCQ_MULTIPLE,
            self.QuestionType.TRUE_FALSE_NOT_GIVEN,
            self.QuestionType.YES_NO_NOT_GIVEN,
        ]:
            if not isinstance(self.options_json, list) or len(self.options_json) == 0:
                raise ValidationError({'options_json': 'Options must be provided for choice-based questions.'})
        if self.type in [
            self.QuestionType.FILL_BLANK,
            self.QuestionType.SENTENCE_COMPLETION,
            self.QuestionType.SUMMARY_COMPLETION,
            self.QuestionType.SHORT_ANSWER,
            self.QuestionType.WRITING_PROMPT,
            self.QuestionType.SPEAKING_PROMPT,
        ]:
            if not isinstance(self.correct_answer_json, dict):
                raise ValidationError({'correct_answer_json': 'Correct answer structure is required.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.prompt[:70]}...'


class AnswerOption(UUIDModel, TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    text = models.CharField(max_length=1024)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('question', 'order')
        ordering = ['question', 'order']

    def __str__(self):
        return self.text


class CorrectAnswerRule(UUIDModel, TimeStampedModel):
    class RuleType(models.TextChoices):
        EXACT = 'exact', 'Exact'
        ACCEPTED_VARIANTS = 'accepted_variants', 'Accepted Variants'
        CONTAINS = 'contains', 'Contains'
        REGEX = 'regex', 'Regex'
        KEYWORD_SET = 'keyword_set', 'Keyword Set'
        NUMERIC_TOLERANCE = 'numeric_tolerance', 'Numeric Tolerance'
        DATE_VARIANTS = 'date_variants', 'Date Variants'
        MATCHING_PAIRS = 'matching_pairs', 'Matching Pairs'
        MANUAL_REVIEW = 'manual_review', 'Manual Review'
        SEMANTIC = 'semantic', 'Semantic'

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='correct_answer_rules')
    rule_type = models.CharField(max_length=32, choices=RuleType.choices)
    accepted_answers = models.JSONField(default=list, blank=True)
    value = models.JSONField(default=dict, blank=True)
    case_sensitive = models.BooleanField(default=False)
    trim_whitespace = models.BooleanField(default=True)
    ignore_punctuation = models.BooleanField(default=False)
    max_words = models.PositiveIntegerField(null=True, blank=True)
    min_words = models.PositiveIntegerField(null=True, blank=True)
    partial_credit = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    points_override = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.rule_type} for {self.question.id}'
