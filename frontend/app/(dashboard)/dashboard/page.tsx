'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/useAuthStore';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const displayName = user?.username || user?.email?.split('@')[0] || 'Student';

  return (
    <div className="space-y-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm shadow-slate-900/5">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
            <h1 className="mt-4 text-3xl font-semibold text-slate-900">Welcome back, {displayName}.</h1>
            <p className="mt-2 text-sm text-slate-600">
              Your IELTS practice hub is ready. Continue tests, track progress, and improve your band score.
            </p>
          </div>
          <div className="grid gap-3 sm:flex sm:items-center">
            <Button asChild>
              <Link href="/tests">Start New Mock Test</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          { label: 'Tests Taken', value: '0' },
          { label: 'Current Band', value: 'N/A' },
          { label: 'Streak', value: '0' },
        ].map((stat) => (
          <div key={stat.label} className="rounded-3xl border border-slate-200 bg-white p-6 text-center shadow-sm shadow-slate-900/5">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{stat.label}</p>
            <p className="mt-4 text-3xl font-semibold text-slate-900">{stat.value}</p>
          </div>
        ))}
      </section>

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
