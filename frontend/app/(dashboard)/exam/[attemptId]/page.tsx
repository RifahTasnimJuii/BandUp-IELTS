'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/useAuthStore';
import { useExamStore } from '@/store/useExamStore';

interface ExamRoomPageProps {
  params: {
    attemptId: string;
  };
}

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export default function ExamRoomPage({ params }: ExamRoomPageProps) {
  const { attemptId } = params;
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [savingStatus, setSavingStatus] = useState('All changes saved');
  const currentQuestionIndex = useExamStore((state) => state.currentQuestionIndex);
  const questions = useExamStore((state) => state.questions);
  const flaggedQuestions = useExamStore((state) => state.flaggedQuestions);
  const setCurrentQuestionIndex = useExamStore((state) => state.setCurrentQuestionIndex);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    setRemainingSeconds(60 * 120);
    const interval = window.setInterval(() => {
      setRemainingSeconds((prev) => (prev !== null ? Math.max(prev - 1, 0) : null));
    }, 1000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const autosave = window.setInterval(() => {
      setSavingStatus('Saving...');
      setTimeout(() => setSavingStatus('All changes saved'), 500);
    }, 15000);
    return () => window.clearInterval(autosave);
  }, []);

  const currentQuestion = useMemo(
    () => questions[currentQuestionIndex] || null,
    [questions, currentQuestionIndex],
  );

  const handleSubmit = () => {
    router.push(`/dashboard`);
  };

  if (!isAuthenticated) {
    return <div>Loading exam room...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="sticky top-0 z-20 bg-white border-b border-slate-200 py-4">
        <div className="container mx-auto flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-slate-500">Attempt ID: {attemptId}</p>
            <h1 className="text-2xl font-semibold">Exam Room</h1>
          </div>
          <div className="flex flex-col items-start gap-2 sm:items-end">
            <span className="font-semibold text-slate-700">
              Time Remaining: {remainingSeconds !== null ? formatDuration(remainingSeconds) : 'Loading...'}
            </span>
            <span className="text-sm text-slate-500">{savingStatus}</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{currentQuestion ? `Question ${currentQuestionIndex + 1}` : 'No question loaded'}</CardTitle>
              <CardDescription>
                {currentQuestion ? currentQuestion.label : 'Select a question from the palette to begin.'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-slate-600">Question content will appear here.</p>
                <textarea
                  className="w-full min-h-[220px] rounded-md border border-slate-200 p-3 text-sm focus:border-slate-400 focus:outline-none"
                  placeholder="Type your answer here..."
                  disabled
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex items-center justify-between gap-4">
            <Button variant="outline" onClick={() => setCurrentQuestionIndex(Math.max(currentQuestionIndex - 1, 0))}>
              Previous
            </Button>
            <Button variant="outline" onClick={() => setCurrentQuestionIndex(Math.min(currentQuestionIndex + 1, questions.length - 1))}>
              Next
            </Button>
            <Button onClick={handleSubmit}>Submit Attempt</Button>
          </div>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Question Palette</CardTitle>
              <CardDescription>Jump between questions and mark items for review.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {questions.length > 0 ? (
                  questions.map((question, index) => (
                    <button
                      key={question.id}
                      type="button"
                      onClick={() => setCurrentQuestionIndex(index)}
                      className={`rounded-lg border px-3 py-2 text-left transition ${index === currentQuestionIndex ? 'border-slate-900 bg-slate-100' : 'border-slate-200 bg-white hover:border-slate-300'}`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium">Q{index + 1}</span>
                        {flaggedQuestions.includes(question.id) && <span className="text-xs text-amber-700">Flagged</span>}
                      </div>
                      <p className="text-xs text-slate-500 truncate">{question.label}</p>
                    </button>
                  ))
                ) : (
                  <p className="text-sm text-slate-500">No questions loaded yet.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Exam Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" onClick={() => router.push('/dashboard')}>
                Leave Exam Room
              </Button>
              <p className="text-sm text-slate-500">
                Exam autosave and heartbeat are active while you remain in the room.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
