import re
from decimal import Decimal

from apps.grading.models import ScoringBandMapping


def _normalize_text(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip().lower())


def calculate_question_score(question, answer_response):
    raw_score = Decimal('0')
    points = Decimal(question.points or 0)
    correct_answer = question.correct_answer_json or {}
    answer_text = _normalize_text(answer_response.answer_text)
    selected_options = answer_response.selected_options or []

    if question.type == question.QuestionType.MCQ_SINGLE:
        if selected_options and correct_answer.get('answer') is not None:
            if str(selected_options[0]).strip() == str(correct_answer.get('answer')).strip():
                raw_score = points
    elif question.type == question.QuestionType.MCQ_MULTIPLE:
        if isinstance(selected_options, list) and isinstance(correct_answer.get('answer'), list):
            if set(map(str, selected_options)) == set(map(str, correct_answer.get('answer'))):
                raw_score = points
    elif question.type in [
        question.QuestionType.TRUE_FALSE_NOT_GIVEN,
        question.QuestionType.YES_NO_NOT_GIVEN,
    ]:
        if answer_text and _normalize_text(correct_answer.get('answer')) == answer_text:
            raw_score = points
    else:
        if answer_text and _normalize_text(correct_answer.get('answer')) == answer_text:
            raw_score = points
        else:
            for rule in question.correct_answer_rules.all():
                if _match_correct_answer_rule(answer_text, rule):
                    raw_score = points
                    break

    return raw_score


def _match_correct_answer_rule(answer_text, rule):
    normalized_answer = _normalize_text(answer_text)
    accepted = [str(item).strip().lower() for item in (rule.accepted_answers or [])]

    if rule.rule_type == rule.RuleType.EXACT:
        return normalized_answer == _normalize_text(rule.value.get('answer'))
    if rule.rule_type == rule.RuleType.ACCEPTED_VARIANTS:
        return normalized_answer in accepted
    if rule.rule_type == rule.RuleType.CONTAINS:
        return any(term in normalized_answer for term in accepted)
    if rule.rule_type == rule.RuleType.KEYWORD_SET:
        keywords = [str(item).strip().lower() for item in rule.value.get('keywords', [])]
        return all(keyword in normalized_answer for keyword in keywords)
    if rule.rule_type == rule.RuleType.NUMERIC_TOLERANCE:
        try:
            actual = Decimal(normalized_answer)
            expected = Decimal(rule.value.get('value', '0'))
            tolerance = Decimal(rule.value.get('tolerance', '0'))
            return abs(actual - expected) <= tolerance
        except Exception:
            return False

    return False


def calculate_section_band_score(test, section_type, raw_score):
    mapping = ScoringBandMapping.objects.filter(test=test, section_type=section_type).order_by('raw_score_min')
    if not mapping.exists():
        mapping = ScoringBandMapping.objects.filter(test__isnull=True, section_type=section_type).order_by('raw_score_min')

    for band_mapping in mapping:
        if band_mapping.raw_score_min <= raw_score <= band_mapping.raw_score_max:
            return band_mapping.band_score

    return None
