'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getAnalyticsDashboard, getScoreTrend, type DashboardAnalytics, type ScoreTrendPoint } from '@/lib/api/analytics';

function AnalyticsPageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-12 w-48 rounded-xl bg-slate-200 dark:bg-slate-800" />
      <div className="grid gap-4 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="h-28 rounded-3xl bg-slate-200 dark:bg-slate-800" />
        ))}
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="h-80 rounded-3xl bg-slate-200 dark:bg-slate-800" />
        <div className="h-80 rounded-3xl bg-slate-200 dark:bg-slate-800" />
      </div>
      <div className="h-60 rounded-3xl bg-slate-200 dark:bg-slate-800" />
    </div>
  );
}

function chartValue(value: number | string | null | undefined) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
}

export default function AnalyticsPageClient() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DashboardAnalytics | null>(null);
  const [trend, setTrend] = useState<ScoreTrendPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const [dashboardData, trendData] = await Promise.all([getAnalyticsDashboard(), getScoreTrend()]);
        setDashboard(dashboardData);
        setTrend(trendData);
      } catch {
        setError('Unable to load your analytics right now.');
      } finally {
        setIsLoading(false);
      }
    };

    void loadAnalytics();
  }, []);

  const scoreTrendData = useMemo(() => {
    if (trend.length > 0) {
      return trend.map((entry) => ({
        name: entry.label ?? entry.date ?? 'Attempt',
        band: chartValue(entry.band ?? entry.score),
      }));
    }

    const fallback = dashboard?.recent_scores ?? [];

    return fallback.map((entry) => ({
      name: String(entry.label ?? entry.date ?? 'Attempt'),
      band: chartValue(entry.band ?? entry.score),
    }));
  }, [dashboard, trend]);

  const radarData = useMemo(() => {
    const writing = dashboard?.writing_criteria ?? dashboard?.skill_summary?.writing ?? {};
    const speaking = dashboard?.speaking_criteria ?? dashboard?.skill_summary?.speaking ?? {};

    const keys = Array.from(new Set([...Object.keys(writing), ...Object.keys(speaking)])).slice(0, 8);

    return keys.map((key) => ({
      subject: key.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()),
      writing: chartValue(writing[key]),
      speaking: chartValue(speaking[key]),
    }));
  }, [dashboard]);

  const weakAreas = useMemo(() => {
    const items = dashboard?.weak_areas ?? [];

    return items.map((item) => ({
      label: item.label,
      score: chartValue(item.score ?? item.value),
    }));
  }, [dashboard]);

  if (isLoading) return <AnalyticsPageSkeleton />;

  if (error || !dashboard) {
    return (
      <div className="rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700 dark:border-red-500/25 dark:bg-red-500/10 dark:text-red-200">
        <p className="font-semibold">Analytics unavailable</p>
        <p>{error ?? 'No analytics are available yet.'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-sky-600 dark:text-sky-300">Analytics</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900 dark:text-slate-100">Your performance dashboard</h1>
        </div>
        <Button aria-label="Take a practice test" onClick={() => router.push('/tests')} className="w-full sm:w-auto">
          Take a Practice Test
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <CardContent className="p-5">
            <p className="text-sm text-slate-500 dark:text-slate-400">Average Band</p>
            <p className="mt-3 text-3xl font-bold text-slate-900 dark:text-slate-100">{chartValue(dashboard.overall_average_band).toFixed(1)}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <CardContent className="p-5">
            <p className="text-sm text-slate-500 dark:text-slate-400">Writing</p>
            <p className="mt-3 text-3xl font-bold text-slate-900 dark:text-slate-100">{chartValue(dashboard.section_averages?.writing).toFixed(1)}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <CardContent className="p-5">
            <p className="text-sm text-slate-500 dark:text-slate-400">Speaking</p>
            <p className="mt-3 text-3xl font-bold text-slate-900 dark:text-slate-100">{chartValue(dashboard.section_averages?.speaking).toFixed(1)}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <CardHeader>
            <CardTitle className="dark:text-slate-100">Score trend</CardTitle>
            <CardDescription className="dark:text-slate-400">Your recent band performance over time.</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={scoreTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" opacity={0.4} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis domain={[4, 9]} stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="band" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <CardHeader>
            <CardTitle className="dark:text-slate-100">Skills radar</CardTitle>
            <CardDescription className="dark:text-slate-400">Writing vs Speaking skill profile.</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="75%">
                <PolarGrid stroke="#cbd5e1" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                <PolarRadiusAxis angle={30} domain={[0, 9]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Radar dataKey="writing" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
                <Radar dataKey="speaking" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.2} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <CardHeader>
          <CardTitle className="dark:text-slate-100">Weak areas</CardTitle>
          <CardDescription className="dark:text-slate-400">Modules and skill areas needing more attention.</CardDescription>
        </CardHeader>
        <CardContent className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={weakAreas}>
              <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" opacity={0.3} />
              <XAxis dataKey="label" stroke="#94a3b8" />
              <YAxis domain={[0, 9]} stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="score" fill="#f59e0b" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
