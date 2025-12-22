from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from reviews.models import PlatformReview
from datetime import timedelta, date


def home_view(request):
    total_tests = 0
    avg_scores = {
        'reading': 0.0,
        'listening': 0.0,
        'writing': 0.0
    }

    # Try to import review model, but fail gracefully if missing
    try:
        from reviews.models import PlatformReview
        reviews_enabled = True
    except ImportError:
        reviews_enabled = False

    if request.user.is_authenticated:
        try:
            from reading.models import UserReadingAttempt
            from listening.models import UserListeningAttempt
            from writing.models import WritingSubmission

            reading_qs = UserReadingAttempt.objects.filter(user=request.user)
            listening_qs = UserListeningAttempt.objects.filter(user=request.user)
            writing_qs = WritingSubmission.objects.filter(user=request.user)

            total_tests = reading_qs.count() + listening_qs.count()

            avg_scores['reading'] = round(
                reading_qs.aggregate(Avg('band_score'))['band_score__avg'] or 0, 1
            )

            avg_scores['listening'] = round(
                listening_qs.aggregate(Avg('band_score'))['band_score__avg'] or 0, 1
            )

            latest_writing = writing_qs.order_by('-submitted_at').first()
            if latest_writing and hasattr(latest_writing, 'feedback'):
                avg_scores['writing'] = latest_writing.feedback.band_score

        except Exception:
            pass

    # Dynamic performance snapshot
    performance_snapshot = [
        {'module': 'Reading', 'band': avg_scores['reading'], 'color': 'primary'},
        {'module': 'Listening', 'band': avg_scores['listening'], 'color': 'success'},
        {'module': 'Writing', 'band': avg_scores['writing'], 'color': 'warning'},
    ]

    # Get latest approved reviews if table exists
    reviews = []
    if reviews_enabled:
        try:
            reviews = PlatformReview.objects.filter(is_approved=True).order_by('-created_at')[:3]
        except Exception:
            reviews = []

    context = {
        'total_tests': total_tests,
        'avg_reading': avg_scores['reading'],
        'avg_listening': avg_scores['listening'],
        'avg_writing': avg_scores['writing'],
        'performance_snapshot': performance_snapshot,
        'reviews': reviews
    }

    return render(request, 'home.html', context)




@login_required
def dashboard_view(request):
    """Professional, dynamic IELTS dashboard view"""

    recent_activities = []
    total_tests = 0
    avg_reading = 0
    avg_listening = 0
    total_writing_tests = 0

    # Initialize variables to avoid errors
    total_reading_tests = 0
    total_listening_tests = 0

    try:
        from reading.models import UserReadingAttempt
        from listening.models import UserListeningAttempt
        from writing.models import WritingSubmission

        # ===== Reading Attempts =====
        reading_attempts = UserReadingAttempt.objects.filter(user=request.user).order_by('-completed_at')
        total_reading_tests = reading_attempts.count()
        avg_reading = round(reading_attempts.aggregate(Avg('band_score'))['band_score__avg'] or 0, 1)
        for attempt in reading_attempts[:5]:  # Show 5 recent
            recent_activities.append({
                'module': 'Reading',
                'module_color': 'primary',
                'test': attempt.test.title if hasattr(attempt, 'test') else 'Test',
                'score': f"{attempt.score}/{attempt.total_questions}",
                'band_score': attempt.band_score,
                'date': attempt.completed_at,
                'time_taken': getattr(attempt, 'time_taken', 0),
                'review_url': f"/reading/results/{attempt.id}/"
            })

        # ===== Listening Attempts =====
        listening_attempts = UserListeningAttempt.objects.filter(user=request.user).order_by('-completed_at')
        total_listening_tests = listening_attempts.count()
        avg_listening = round(listening_attempts.aggregate(Avg('band_score'))['band_score__avg'] or 0, 1)
        for attempt in listening_attempts[:5]:
            recent_activities.append({
                'module': 'Listening',
                'module_color': 'success',
                'test': attempt.test.title if hasattr(attempt, 'test') else 'Test',
                'score': f"{attempt.score}/{attempt.total_questions}",
                'band_score': attempt.band_score,
                'date': attempt.completed_at,
                'time_taken': getattr(attempt, 'time_taken', 0),
                'review_url': f"/listening/results/{attempt.id}/"
            })

        # ===== Writing Submissions =====
        writing_submissions = WritingSubmission.objects.filter(user=request.user).order_by('-submitted_at')
        total_writing_tests = writing_submissions.count()
        for submission in writing_submissions[:5]:
            band_score = submission.feedback.band_score if hasattr(submission, 'feedback') else 0
            recent_activities.append({
                'module': 'Writing',
                'module_color': 'warning',
                'test': f"Task {submission.prompt.get_task_type_display()}" if hasattr(submission,
                                                                                       'prompt') else 'Writing Task',
                'score': f"{submission.word_count} words",
                'band_score': band_score,
                'date': submission.submitted_at,
                'time_taken': getattr(submission, 'time_taken', 0),
                'review_url': f"/writing/feedback/{submission.id}/"
            })

        total_tests = total_reading_tests + total_listening_tests + total_writing_tests

    except ImportError:
        # Models not created yet
        pass

    # Sort recent activities by date
    recent_activities.sort(key=lambda x: x['date'] if 'date' in x else date.min, reverse=True)
    recent_activities = recent_activities[:10]

    # ===== Study Hours & Weekly Stats =====
    study_hours = total_tests * 1  # Estimate: 1 hour per test
    week_tests = total_tests // 4  # Approximate weekly tests

    # ===== Targets (Dynamic) =====
    target_reading = 8.0
    target_listening = 8.0
    target_writing_essays = 10

    context = {
        'total_tests': total_tests,
        'tests_this_week': week_tests,
        'avg_reading': avg_reading,
        'avg_listening': avg_listening,
        'study_hours': study_hours,
        'streak_days': 7,  # Could be calculated dynamically from login/activity history
        'recent_attempts': recent_activities,
        'writing_count': total_writing_tests,
        'target_reading': target_reading,
        'target_listening': target_listening,
        'target_writing_essays': target_writing_essays,
    }

    return render(request, 'dashboard.html', context)


def about_view(request):
    """About page view"""
    return render(request, 'about.html')


def contact_view(request):
    """Contact page view"""
    return render(request, 'contact.html')


def privacy_view(request):
    """Privacy policy page"""
    return render(request, 'privacy.html')


def terms_view(request):
    """Terms of service page"""
    return render(request, 'terms.html')