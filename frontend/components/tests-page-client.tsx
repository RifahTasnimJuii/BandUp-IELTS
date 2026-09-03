'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Card, CardDescription, CardFooter, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getTests, type TestCatalogItem } from '@/lib/api/tests';
import { startAttempt } from '@/lib/api/exam';

export default function TestsPageClient() {
  const router = useRouter();
  const [starting, setStarting] = useState<string | null>(null);
  const { data, isLoading, isError, error } = useQuery<TestCatalogItem[]>({
    queryKey: ['tests'],
    queryFn: getTests,
    staleTime: 1000 * 60 * 2,
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Test catalog</p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900">Available IELTS mock tests</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">Browse published tests and begin your next full exam simulation.</p>
        </div>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="animate-pulse rounded-3xl border border-slate-200 bg-white p-6" />
          ))}
        </div>
      )}

      {isError && (
        <div className="rounded-3xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
          {String((error as Error)?.message || 'Unable to load tests. Please refresh the page.')}
        </div>
      )}

      {!isLoading && !isError && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data && data.length ? (
            data.map((test) => (
              <Card key={test.id}>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">{test.module_type === 'both' ? 'Academic + General' : test.module_type === 'academic' ? 'Academic' : 'General'}</p>
                    <CardTitle>{test.title}</CardTitle>
                  </div>
                  <CardDescription>{test.description || 'A complete IELTS mock test with listening, reading, writing, and speaking sections.'}</CardDescription>
                </div>
                <CardFooter>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-slate-700">
                    {test.module_type}
                  </span>
                  <Button size="sm" aria-label={`Start ${test.title}`} disabled={starting === test.id} onClick={async () => { setStarting(test.id); try { const response = await startAttempt({ test_id: test.id, mode: 'exam', client_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, locale: navigator.language, device_info: { platform: navigator.platform, userAgent: navigator.userAgent } }); router.push(`/exam/${response.attempt_id}`); } finally { setStarting(null); } }}>{starting === test.id ? 'Starting...' : 'Start Exam'}</Button>
                </CardFooter>
              </Card>
            ))
          ) : (
            <div className="rounded-3xl border border-slate-200 bg-white p-8 text-slate-600">
              No published tests are available yet. Check back soon.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
