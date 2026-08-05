'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/useAuthStore';
import { getTestDetail, startAttempt, type TestDetail } from '@/lib/api/exam';

interface TestDetailPageProps {
  params: {
    slug: string;
  };
}

export default function TestDetailPage({ params }: TestDetailPageProps) {
  const { slug } = params;
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [test, setTest] = useState<TestDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const loadTest = async () => {
      try {
        const data = await getTestDetail(slug);
        setTest(data);
      } catch (err) {
        setError('Unable to load test details.');
      } finally {
        setIsLoading(false);
      }
    };

    loadTest();
  }, [slug, isAuthenticated, router]);

  const handleStart = async () => {
    if (!test) return;
    setStarting(true);
    try {
      const response = await startAttempt({
        test_id: test.id,
        mode: 'exam',
        client_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        locale: navigator.language,
        device_info: {
          platform: navigator.platform,
          userAgent: navigator.userAgent,
        },
      });
      router.push(`/exam/${response.attempt_id}`);
    } catch (err) {
      setError('Unable to start the exam attempt.');
    } finally {
      setStarting(false);
    }
  };

  if (isLoading) {
    return <div>Loading test details...</div>;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  if (!test) {
    return <div>No test data available.</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{test.title}</CardTitle>
          <CardDescription>{test.description || 'No description available.'}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-slate-600">Duration</p>
              <p>{test.duration_minutes ? `${test.duration_minutes} minutes` : 'Varies'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600">Sections</p>
              <p>{test.sections?.length ?? 'Unknown'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Ready to begin?</CardTitle>
          <CardDescription>Start your attempt and enter the exam room. Your answers are autosaved while you work.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleStart} disabled={starting}>
            {starting ? 'Starting...' : 'Start Exam'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
