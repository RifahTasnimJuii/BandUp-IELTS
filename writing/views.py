from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json


def writing_prompts_view(request):
    """Display all writing prompts"""
    # Mock prompts
    task1_prompts = [
        {'id': 1, 'title': 'Academic Task 1: Line Graph', 'task_type': 'task1'},
        {'id': 2, 'title': 'General Task 1: Formal Letter', 'task_type': 'task1'},
    ]

    task2_prompts = [
        {'id': 3, 'title': 'Some people believe that...', 'task_type': 'task2'},
        {'id': 4, 'title': 'Discuss both views...', 'task_type': 'task2'},
    ]

    return render(request, 'writing/prompts_list.html', {
        'task1_prompts': task1_prompts,
        'task2_prompts': task2_prompts,
        'recent_submissions': []
    })


@login_required
def writing_prompt_view(request, prompt_id):
    """Display a specific writing prompt"""
    mock_prompt = {
        'id': prompt_id,
        'title': f'Writing Prompt {prompt_id}',
        'task_type': 'task2' if prompt_id % 2 == 0 else 'task1',
        'prompt_text': 'Discuss the advantages and disadvantages of this approach.',
    }

    return render(request, 'writing/writing_prompt.html', {
        'prompt': mock_prompt,
        'word_limit': 150 if mock_prompt['task_type'] == 'task1' else 250,
        'previous_submission': None
    })


@login_required
def submit_writing(request, prompt_id):
    """Handle writing submission - placeholder"""
    messages.success(request, f'Writing submitted for prompt {prompt_id}! (Placeholder)')
    return redirect('writing_feedback', submission_id=1)


@login_required
def writing_feedback_view(request, submission_id):
    """Display writing feedback"""
    mock_feedback = {
        'task_response_score': 7,
        'coherence_score': 6,
        'lexical_resource_score': 7,
        'grammatical_range_score': 6,
        'overall_score': 6.5,
        'band_score': 6.5,
        'detailed_feedback': 'This is a placeholder feedback. Your essay shows good structure but needs more varied vocabulary.',
        'suggestions': '1. Use more academic vocabulary\n2. Add more examples\n3. Improve conclusion'
    }

    return render(request, 'writing/writing_feedback.html', {
        'submission': {'id': submission_id, 'prompt': {'title': 'Sample Prompt'}},
        'feedback': mock_feedback,
        'scores_json': json.dumps([7, 6, 7, 6]),
        'score_labels_json': json.dumps(['Task Response', 'Coherence', 'Vocabulary', 'Grammar']),
        'suggestions_list': ['Use more academic vocabulary', 'Add more examples', 'Improve conclusion']
    })


@login_required
def writing_progress_view(request):
    """Display writing progress"""
    return render(request, 'writing/progress.html', {
        'submissions': [],
        'total_submissions': 0,
        'avg_band': 0,
        'best_submission': None,
        'dates_json': '[]',
        'bands_json': '[]'
    })