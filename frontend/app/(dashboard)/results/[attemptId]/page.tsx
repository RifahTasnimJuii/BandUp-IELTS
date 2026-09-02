'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle2, XCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getAttemptResults, type AttemptResult, type CriteriaScoreMap } from '@/lib/api/results';

const formatBand = (value: number | string | null | undefined) => {
  if (value === null || value === undefined || value === '') return '—';
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  return `Band ${numeric.toFixed(1).replace(/\.0$/, '')}`;
};

const normalizeList = (value: string[] | string | undefined | null) => {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter(Boolean);
  return String(value)
    .split(/\n|\r|•|\-/)
    .map((item) => item.trim())
    .filter(Boolean);
};

const getCriteriaEntries = (criteria?: CriteriaScoreMap) => {
  if (!criteria) return [];
  return Object.entries(criteria).map(([label, score]) => ({
    label: label.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()),
    score: Number(score) || 0,
  }));
};

function ResultsPageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-12 w-40 rounded-xl bg-slate-200 dark:bg-slate-800" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-32 rounded-3xl bg-slate-200 dark:bg-slate-800" />
        ))}
      </div>
      <div className="h-80 rounded-3xl bg-slate-200 dark:bg-slate-800" />
      <div className="h-64 rounded-3xl bg-slate-200 dark:bg-slate-800" />
    </div>
  );
}

function ScoreCard({ label, value, accent = 'from-sky-500 to-indigo-500' }: { label: string; value: string; accent?: string }) {
  return (
    <Card className="overflow-hidden border-0 bg-gradient-to-br text-slate-900 shadow-sm dark:text-slate-50">
      <div className={`h-2 bg-gradient-to-r ${accent}`} />
      <CardContent className="p-5">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <p className="mt-4 text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">{value}</p>
      </CardContent>
    </Card>
  );
}

function SectionScoreCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <CardContent className="p-5">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <p className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-100">{value}</p>
      </CardContent>
    </Card>
  );
}

function ObjectiveReview({ items }: { items: AttemptResult['objective_review'] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <CardHeader>
        <CardTitle className="dark:text-slate-100">Objective Review</CardTitle>
        <CardDescription className="dark:text-slate-400">Check your answers against the correct responses.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => {
          const answer = item.user_answer ?? 'No answer';
          const correct = item.correct_answer ?? 'Not available';
          const isCorrect = item.is_correct ?? false;

          return (
            <div key={`${item.id ?? item.question_number ?? index}`} className="rounded-2xl border border-slate-200 p-4 dark:border-slate-700">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="font-medium text-slate-900 dark:text-slate-100">Question {item.question_number ?? index + 1}</p>
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${isCorrect ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-rose-100 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'}`}>
                  {isCorrect ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                  {isCorrect ? 'Correct' : 'Incorrect'}
                </span>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                  <p className="mb-1 font-medium text-slate-800 dark:text-slate-200">Your answer</p>
                  <p>{answer}</p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                  <p className="mb-1 font-medium text-slate-800 dark:text-slate-200">Correct answer</p>
                  <p>{correct}</p>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

function FeedbackPanel({ label, feedback }: { label: string; feedback?: AttemptResult['writing_feedback'] | AttemptResult['speaking_feedback'] | null }) {
  if (!feedback) return null;

  const status = feedback.status ?? 'completed';
  const criteria = getCriteriaEntries(feedback.criteria_scores);
  const strengths = normalizeList(feedback.strengths);
  const weaknesses = normalizeList(feedback.weaknesses);
  const suggestions = normalizeList(feedback.improvement_suggestions);

  if (status === 'pending_human_review' || status === 'evaluating' || status === 'in_progress') {
    return (
      <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <CardHeader>
          <CardTitle className="dark:text-slate-100">{label}</CardTitle>
          <CardDescription className="dark:text-slate-400">Evaluation is in progress...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200">
            <Sparkles className="h-5 w-5 animate-pulse" />
            <p className="font-medium">AI feedback is being generated for this section.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <CardHeader>
        <CardTitle className="dark:text-slate-100">{label}</CardTitle>
        <CardDescription className="dark:text-slate-400">Band score and feedback summary.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-sky-100 px-3 py-1 text-sm font-semibold text-sky-700 dark:bg-sky-500/10 dark:text-sky-300">
            {formatBand(feedback.band_score)}
          </span>
          {feedback.feedback ? <p className="text-sm text-slate-600 dark:text-slate-300">{feedback.feedback}</p> : null}
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {criteria.length > 0 ? (
            criteria.map((item) => (
              <div key={item.label} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{item.label}</p>
                <p className="mt-2 text-xl font-semibold text-slate-900 dark:text-slate-100">{item.score.toFixed(1)}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500 dark:text-slate-400">No criterion breakdown is available yet.</p>
          )}
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-500/25 dark:bg-emerald-500/10">
            <h4 className="mb-3 font-semibold text-emerald-800 dark:text-emerald-200">Strengths</h4>
            {strengths.length > 0 ? (
              <ul className="space-y-2 text-sm text-emerald-900 dark:text-emerald-100">
                {strengths.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            ) : (
              <p className="text-sm text-emerald-700 dark:text-emerald-300">No strengths recorded.</p>
            )}
          </div>

          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 dark:border-rose-500/25 dark:bg-rose-500/10">
            <h4 className="mb-3 font-semibold text-rose-800 dark:text-rose-200">Weaknesses</h4>
            {weaknesses.length > 0 ? (
              <ul className="space-y-2 text-sm text-rose-900 dark:text-rose-100">
                {weaknesses.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            ) : (
              <p className="text-sm text-rose-700 dark:text-rose-300">No weaknesses recorded.</p>
            )}
          </div>

          <div className="rounded-2xl border border-sky-200 bg-sky-50 p-4 dark:border-sky-500/25 dark:bg-sky-500/10">
            <h4 className="mb-3 font-semibold text-sky-800 dark:text-sky-200">Improvement Tips</h4>
            {suggestions.length > 0 ? (
              <ul className="space-y-2 text-sm text-sky-900 dark:text-sky-100">
                {suggestions.map((item) => <li key={item}>• {item}</li>)}
              </ul>
            ) : (
              <p className="text-sm text-sky-700 dark:text-sky-300">No suggestions available yet.</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ResultsPage({ params }: { params: { attemptId: string } }) {
  const { data: result, isLoading, error } = useQuery<AttemptResult>({
    queryKey: ['attempt-results', params.attemptId],
    queryFn: () => getAttemptResults(params.attemptId),
    refetchInterval: 5000,
    refetchIntervalInBackground: false,
  });

  const sectionScores = useMemo(() => {
    const scores = result?.section_scores ?? {};
    return [
      { label: 'Listening', value: formatBand(scores.listening ?? scores.Listening ?? scores['listening_band'] ?? null) },
      { label: 'Reading', value: formatBand(scores.reading ?? scores.Reading ?? scores['reading_band'] ?? null) },
      { label: 'Writing', value: formatBand(scores.writing ?? scores.Writing ?? scores['writing_band'] ?? null) },
      { label: 'Speaking', value: formatBand(scores.speaking ?? scores.Speaking ?? scores['speaking_band'] ?? null) },
    ];
  }, [result]);

  if (isLoading) return <ResultsPageSkeleton />;

  if (error || !result) {
    const errorMessage = error instanceof Error ? error.message : 'No result data is available for this attempt.';

    return (
      <div className="space-y-4 rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700 dark:border-red-500/25 dark:bg-red-500/10 dark:text-red-200">
        <p className="font-semibold">Results unavailable</p>
        <p>{errorMessage}</p>
        <Link href="/tests">
          <Button variant="outline" className="mt-2 bg-white dark:bg-slate-900 dark:text-slate-100">
            Return to tests
          </Button>
        </Link>
      </div>
    );
  }

  const writingFeedback = result.writing_feedback ?? null;
  const speakingFeedback = result.speaking_feedback ?? null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <Link href="/dashboard">
          <Button variant="outline" className="gap-2 bg-white dark:bg-slate-900 dark:text-slate-100">
            <ArrowLeft size={16} />
            Back to dashboard
          </Button>
        </Link>
      </div>

      <ScoreCard label="Overall Band" value={formatBand(result.overall_band ?? null)} accent="from-sky-500 via-blue-500 to-indigo-600" />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {sectionScores.map((section) => (
          <SectionScoreCard key={section.label} label={section.label} value={section.value} />
        ))}
      </div>

      {result.is_review_allowed ? (
        <ObjectiveReview items={result.objective_review ?? []} />
      ) : null}

      <div className="space-y-6">
        {writingFeedback ? <FeedbackPanel label="Writing Feedback" feedback={writingFeedback} /> : null}
        {speakingFeedback ? <FeedbackPanel label="Speaking Feedback" feedback={speakingFeedback} /> : null}
      </div>
    </div>
  );
}
