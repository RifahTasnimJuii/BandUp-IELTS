from django import template

register = template.Library()

@register.filter
def get_answer(user_answers, key):
    return user_answers.get(key, '-')

@register.filter
def get(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)