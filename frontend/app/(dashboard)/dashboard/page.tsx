'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/useAuthStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getAnalyticsDashboard, type DashboardAnalytics } from '@/lib/api/analytics';

const formatBand = (value: number | string | null | undefined) => value === null || value === undefined ? '—' : Number(value).toFixed(1);

function StatCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return <Card><CardContent className="p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold">{value}</p><p className="mt-2 text-sm text-slate-500">{helper}</p></CardContent></Card>;
}

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const displayName = user?.username || user?.email?.split('@')[0] || 'Student';
  const { data, isLoading, error } = useQuery<DashboardAnalytics>({ queryKey: ['analytics-dashboard'], queryFn: getAnalyticsDashboard });

  if (isLoading) return <div className="animate-pulse text-slate-500">Loading your dashboard...</div>;
  if (error || !data) return <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">Unable to load your dashboard right now.</div>;

  const hasAttempts = data.tests_taken > 0;
  const weak = data.weak_area;

  return (
    <div className="space-y-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm shadow-slate-900/5">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
            <h1 className="mt-4 text-3xl font-semibold text-slate-900">{hasAttempts ? `Welcome back, ${displayName}.` : 'Welcome to BandUp IELTS'}</h1>
            <p className="mt-2 text-sm text-slate-600">
              {hasAttempts ? 'Here is your latest practice progress.' : "You haven't taken any mock tests yet."}
            </p>
            {!hasAttempts ? <Button asChild className="mt-6"><Link href="/tests">Take your first mock test</Link></Button> : null}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><StatCard label="Current band" value={formatBand(data.overall_band)} helper={hasAttempts ? 'Latest overall band' : 'Not assessed yet'} /><StatCard label="Tests taken" value={String(data.tests_taken)} helper="Completed mock tests" /><StatCard label="Weak area" value={weak ? `${weak.label} (${formatBand(weak.score)})` : '—'} helper={weak ? 'Lowest average module band' : 'Complete a test to discover your weak areas'} /><StatCard label="Readiness" value={`${data.readiness_score}%`} helper={hasAttempts ? 'Based on completed tests' : 'Not assessed yet'} /></section>

      {!hasAttempts ? <Card><CardHeader><CardTitle>How it works</CardTitle></CardHeader><CardContent className="grid gap-4 sm:grid-cols-3"><div><b>1. Take a test</b><p className="mt-1 text-sm text-slate-500">Complete a timed mock exam.</p></div><div><b>2. Get AI feedback</b><p className="mt-1 text-sm text-slate-500">See your section scores and feedback.</p></div><div><b>3. Improve</b><p className="mt-1 text-sm text-slate-500">Use your results to plan practice.</p></div></CardContent></Card> : <><Card><CardHeader><CardTitle>Module bands</CardTitle></CardHeader><CardContent className="grid gap-4 sm:grid-cols-4">{Object.entries(data.module_bands).map(([module, score]) => <div key={module}><p className="text-sm capitalize text-slate-500">{module}</p><p className="mt-1 text-2xl font-semibold">{formatBand(score)}</p></div>)}</CardContent></Card><Card><CardHeader><CardTitle>Recommended next step</CardTitle></CardHeader><CardContent><p className="text-slate-700">{weak ? `Your ${weak.label} band is lowest (${formatBand(weak.score)}). Take a ${weak.label} practice test.` : 'Complete another test to receive a recommendation.'}</p></CardContent></Card><Card><CardHeader><CardTitle>Recent attempts</CardTitle></CardHeader><CardContent className="space-y-3">{data.recent_attempts.map((attempt) => <div key={attempt.id} className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3"><div><p className="font-medium">{attempt.test_title}</p><p className="text-sm text-slate-500">{new Date(attempt.date).toLocaleDateString()}</p></div><div className="flex items-center gap-4"><span>Band {formatBand(attempt.overall_band)}</span><Link className="text-sm font-medium text-sky-700" href={`/results/${attempt.id}`}>View Results</Link></div></div>)}</CardContent></Card></>}

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">Ready for your next IELTS challenge?</p>
          <h2 className="mt-4 text-2xl font-semibold text-slate-900">Browse published mock tests.</h2>
          <p className="mt-3 text-sm text-slate-600">Explore IELTS Academic and General modules, then begin a timed practice session instantly.</p>
          <div className="mt-6">
            <Button asChild>
              <Link href="/tests">Browse Tests</Link>
            </Button>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white shadow-sm shadow-slate-900/10">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Focus area</p>
          <h2 className="mt-4 text-2xl font-semibold">Practice under exam conditions.</h2>
          <p className="mt-3 text-sm text-slate-300">Use the exam engine to simulate real IELTS timing, section order, and scoring.</p>
        </div>
      </section>
    </div>
  );
}
