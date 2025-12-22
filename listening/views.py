from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
from django.db.models import Min, Max
from django.http import JsonResponse
import time

from .models import ListeningTest, ListeningSection, ListeningQuestion, UserListeningAttempt
from .utils import calculate_listening_band


def listening_tests_view(request):
    """Display all listening tests"""
    tests = ListeningTest.objects.filter(is_active=True).order_by('test_number')

    user_attempts = {}
    if request.user.is_authenticated:
        attempts = UserListeningAttempt.objects.filter(user=request.user)
        for a in attempts:
            if a.test.id not in user_attempts:
                user_attempts[a.test.id] = a
            elif a.completed_at > user_attempts[a.test.id].completed_at:
                user_attempts[a.test.id] = a

    return render(request, 'listening/tests_list.html', {
        'tests': tests,
        'user_attempts': user_attempts
    })


@login_required
def listening_test_view(request, test_id):
    test = get_object_or_404(ListeningTest, id=test_id, is_active=True)
    sections = test.sections.all().order_by('section_number')

    # Get all sections with their actual question objects
    sections_data = []
    for section in sections:
        questions = section.questions.all().order_by('question_number')
        sections_data.append({
            'section_obj': section,  # Keep the actual section object
            'number': section.section_number,
            'title': section.title,
            'description': section.description,
            'questions': questions  # These are actual Question objects
        })

    section_times = []
    for section in sections:
        start = section.questions.aggregate(Min('time_start'))['time_start__min'] or 0
        end = section.questions.aggregate(Max('time_end'))['time_end__max'] or 0
        section_times.append({'start': start, 'end': end})

    # Get audio duration if audio exists
    audio_duration = 0
    if test.audio_file:
        # You might want to get actual duration here, but for now we'll estimate
        audio_duration = 30 * 60  # 30 minutes default

    return render(request, 'listening/listening_test.html', {
        'test': test,
        'sections': sections_data,
        'section_times': json.dumps(section_times),
        'audio_duration': audio_duration
    })


@login_required
def submit_listening_test(request, test_id):
    """Handle test submission"""
    if request.method != 'POST':
        return redirect('listening_test', test_id=test_id)

    test = get_object_or_404(ListeningTest, id=test_id)
    sections = test.sections.all()
    total_questions = 0
    correct_count = 0
    user_answers = {}

    # Check if time is up
    time_taken = int(request.POST.get('time_taken', 2400))

    for section in sections:
        for question in section.questions.all():
            total_questions += 1
            key = f'section{section.section_number}_q{question.question_number}'

            # Handle different question types
            if question.question_type == 'form_completion':
                answer_parts = []
                for i in range(1, question.field_count + 1):
                    field_key = f'{key}_f{i}'
                    answer_part = request.POST.get(field_key, '').strip().lower()
                    answer_parts.append(answer_part)
                answer = ';'.join(answer_parts)
                user_answers[key] = answer
            else:
                answer = request.POST.get(key, '').strip().lower()
                user_answers[key] = answer

            # Check correctness using the model method
            if question.check_answer(answer):
                correct_count += 1

    # Calculate band score
    score_percentage = (correct_count / total_questions) * 100 if total_questions else 0
    band = calculate_listening_band(score_percentage)

    # Save attempt
    attempt = UserListeningAttempt.objects.create(
        user=request.user,
        test=test,
        score=correct_count,
        total_questions=total_questions,
        band_score=band,
        time_taken=time_taken,
        completed_at=timezone.now(),
        answers=user_answers
    )

    messages.success(request, f'Test submitted! Score: {correct_count}/{total_questions}, Band: {band}')
    return redirect('listening_results', attempt_id=attempt.id)


@login_required
def listening_results_view(request, attempt_id):
    """Show results after submission"""
    attempt = get_object_or_404(UserListeningAttempt, id=attempt_id, user=request.user)
    test = attempt.test
    sections = test.sections.all().prefetch_related('questions')

    # Prepare section data with answers
    sections_data = []
    for section in sections:
        questions_data = []
        for question in section.questions.all():
            key = f'section{section.section_number}_q{question.question_number}'
            user_answer = attempt.answers.get(key, 'No answer')

            questions_data.append({
                'question': question,
                'user_answer': user_answer,
                'is_correct': str(user_answer).lower() in [c.strip().lower()
                                                           for c in question.correct_answer.split(';')]
            })

        sections_data.append({
            'section': section,
            'questions': questions_data
        })

    accuracy = (attempt.score / attempt.total_questions) * 100 if attempt.total_questions else 0

    return render(request, 'listening/listening_results.html', {
        'attempt': attempt,
        'test': test,
        'accuracy': round(accuracy, 1),
        'sections_data': sections_data,
        'user_answers': attempt.answers
    })


@login_required
def save_listening_progress(request, test_id):
    """Save user progress during test"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        user_answers = data.get('answers', {})

        # Save to session
        request.session[f'listening_test_{test_id}_progress'] = {
            'answers': user_answers,
            'timestamp': time.time()
        }

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def load_listening_progress(request, test_id):
    """Load saved progress"""
    progress = request.session.get(f'listening_test_{test_id}_progress')
    if progress:
        return JsonResponse({'status': 'success', 'data': progress})
    return JsonResponse({'status': 'no_data'})