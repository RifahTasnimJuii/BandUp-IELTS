from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ReadingTest, ReadingQuestion, UserReadingAttempt, UserAnswer
from .utils import reading_band_score

@login_required
def reading_test(request, test_id):
    test = get_object_or_404(ReadingTest, id=test_id, is_active=True)
    questions = test.questions.all()

    if request.method == "POST":
        time_taken = int(request.POST.get("time_taken", 0))
        correct = 0

        attempt = UserReadingAttempt.objects.create(
            user=request.user,
            test=test,
            score=0,
            total_questions=test.total_questions,
            band_score=0,
            time_taken=time_taken
        )

        for q in questions:
            user_ans = request.POST.get(f"q_{q.id}", "").strip()

            is_correct = user_ans.lower() == q.correct_answer.lower()
            if is_correct:
                correct += 1

            UserAnswer.objects.create(
                attempt=attempt,
                question=q,
                user_answer=user_ans,
                is_correct=is_correct
            )

        attempt.score = correct
        attempt.band_score = reading_band_score(correct)
        attempt.save()

        return redirect("reading_results", attempt.id)

    return render(request, "reading/reading_test.html", {
        "test": test,
        "questions": questions,
    })


@login_required
def reading_result(request, attempt_id):
    attempt = get_object_or_404(
        UserReadingAttempt,
        id=attempt_id,
        user=request.user
    )
    return render(request, "reading/reading_results.html", {
        "attempt": attempt
    })


@login_required
def reading_review(request, attempt_id):
    attempt = get_object_or_404(
        UserReadingAttempt,
        id=attempt_id,
        user=request.user
    )

    answers = attempt.answers.select_related("question")

    return render(request, "reading/reading_review.html", {
        "attempt": attempt,
        "answers": answers
    })


@login_required
def reading_test_list(request):
    test_type = request.GET.get('type', 'all')

    tests = ReadingTest.objects.filter(is_active=True)

    if test_type in ['academic', 'general']:
        tests = tests.filter(test_type=test_type)

    # User's completed attempts (latest per test)
    attempts = (
        UserReadingAttempt.objects
        .filter(user=request.user)
        .order_by('test', '-completed_at')
    )

    user_attempts = {}
    for a in attempts:
        if a.test_id not in user_attempts:
            user_attempts[a.test_id] = a

    context = {
        'tests': tests,
        'user_attempts': user_attempts,
    }
    return render(request, 'reading/tests_list.html', context)