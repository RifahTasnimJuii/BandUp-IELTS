'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ListeningSection } from '@/components/exam/listening-section';
import { ReadingSection } from '@/components/exam/reading-section';
import { SpeakingSection } from '@/components/exam/sections/speaking-section';
import { WritingSection } from '@/components/exam/sections/writing-section';
import type { ExamQuestion } from '@/components/exam/question-renderers';
import { autosaveAnswer, getAttemptPaper, getAttemptState, submitAttempt } from '@/lib/api/exam';
import { useAuthStore } from '@/store/useAuthStore';
import { useExamStore, type ExamPaperQuestion } from '@/store/useExamStore';

const formatDuration = (seconds: number) => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;

const mapQuestion = (question: ExamPaperQuestion): ExamQuestion => ({
  id: question.id,
  type: question.type as ExamQuestion['type'],
  prompt: question.prompt,
  instruction: question.instruction,
  options_json: question.options.map((option) => ({
    value: option.text.match(/^([A-Z])\./)?.[1] ?? option.text,
    label: option.text,
  })),
  validation_rules_json: question.validation_rules,
  visual_json: question.visual_json,
  question_group: question.question_group,
});

export default function ExamRoomPage({ params }: { params: { attemptId: string } }) {
  const { attemptId } = params;
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingStatus, setSavingStatus] = useState('All changes saved');
  const [submitState, setSubmitState] = useState<'idle' | 'submitting' | 'error'>('idle');
  const [submitNotice, setSubmitNotice] = useState<string | null>(null);
  const [globalExpiresAt, setGlobalExpiresAt] = useState<string | null>(null);
  const [phase, setPhase] = useState<'instructions' | 'questions' | 'complete'>('instructions');
  const paper = useExamStore((state) => state.paper);
  const sections = useExamStore((state) => state.sections);
  const sectionIndex = useExamStore((state) => state.currentSectionIndex);
  const questionIndex = useExamStore((state) => state.currentQuestionIndex);
  const answers = useExamStore((state) => state.answers);
  const flaggedQuestions = useExamStore((state) => state.flaggedQuestions);
  const setPaper = useExamStore((state) => state.setPaper);
  const setAttemptContext = useExamStore((state) => state.setAttemptContext);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const setSectionIndex = useExamStore((state) => state.setCurrentSectionIndex);
  const setQuestionIndex = useExamStore((state) => state.setCurrentQuestionIndex);
  const completedSectionIds = useExamStore((state) => state.completedSectionIds);
  const completeSection = useExamStore((state) => state.completeSection);
  const hydrated = useRef(false);

  useEffect(() => {
    if (!isAuthenticated) { router.push('/login'); return; }
    let cancelled = false;
    Promise.all([getAttemptPaper(attemptId), getAttemptState(attemptId)]).then(([nextPaper, state]) => {
      if (cancelled) return;
      setPaper(nextPaper);
      setAttemptContext(attemptId, state.expires_at, Date.parse(nextPaper.server_time) - Date.now());
      setGlobalExpiresAt(state.expires_at);
      setRemainingSeconds(state.remaining_seconds ?? 0);
      state.answers.forEach((answer) => setAnswer(answer.question, {
        answer_text: answer.answer_text ?? undefined,
        selected_options: answer.selected_options ?? undefined,
        value_json: answer.value_json ?? undefined,
      }));
      hydrated.current = true;
      setPhase('instructions');
      setLoading(false);
    }).catch((error) => {
      console.error('Unable to load exam paper', error);
      setSubmitNotice('Unable to load the exam paper.');
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [attemptId, isAuthenticated, router, setAnswer, setAttemptContext, setPaper]);

  const currentSection = sections[sectionIndex];
  const sectionQuestions = useMemo(() => currentSection?.question_groups.flatMap((group) => group.questions) ?? [], [currentSection]);
  const currentPaperQuestion = sectionQuestions[questionIndex];
  const currentQuestion = currentPaperQuestion ? mapQuestion(currentPaperQuestion) : null;

  useEffect(() => {
    if (!hydrated.current || !currentPaperQuestion) return;
    const answer = answers[currentPaperQuestion.id];
    if (!answer) return;
    setSavingStatus('Saving...');
    const timer = window.setTimeout(() => {
      autosaveAnswer(attemptId, currentPaperQuestion.id, answer, flaggedQuestions.includes(currentPaperQuestion.id))
        .then(() => setSavingStatus('All changes saved'))
        .catch(() => setSavingStatus('Save failed'));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [answers, attemptId, currentPaperQuestion, flaggedQuestions]);

  useEffect(() => {
    if (phase !== 'questions' || remainingSeconds === null || remainingSeconds <= 0) return;
    const timer = window.setInterval(() => setRemainingSeconds((value) => {
      const globalRemaining = globalExpiresAt ? Math.max(Math.ceil((Date.parse(globalExpiresAt) - Date.now()) / 1000), 0) : Number.MAX_SAFE_INTEGER;
      return value === null ? null : Math.min(Math.max(value - 1, 0), globalRemaining);
    }), 1000);
    return () => window.clearInterval(timer);
  }, [globalExpiresAt, phase, remainingSeconds]);

  const startSection = () => {
    setQuestionIndex(0);
    setRemainingSeconds(Math.min(currentSection?.duration_seconds ?? 0, remainingSeconds ?? Number.MAX_SAFE_INTEGER));
    setPhase('questions');
  };
  const goNext = () => questionIndex < sectionQuestions.length - 1 ? setQuestionIndex(questionIndex + 1) : undefined;
  const goPrevious = () => questionIndex > 0 ? setQuestionIndex(questionIndex - 1) : undefined;
  const handleSubmit = useCallback(async () => {
    if (submitState === 'submitting') return;
    setSubmitState('submitting');
    setSubmitNotice('Submitting your exam...');
    try { await submitAttempt(attemptId, answers); router.push(`/results/${attemptId}`); }
    catch (error) { console.error('Attempt submission failed', error); setSubmitState('error'); setSubmitNotice('Submission failed. Please try again.'); }
  }, [answers, attemptId, router, submitState]);
  const finishSection = useCallback(async () => {
    if (!currentSection || completedSectionIds.includes(currentSection.id)) return;
    completeSection(currentSection.id);
    if (sectionIndex >= sections.length - 1) {
      await handleSubmit();
      return;
    }
    setPhase('complete');
  }, [completeSection, completedSectionIds, currentSection, handleSubmit, sectionIndex, sections.length]);

  useEffect(() => {
    if (phase === 'questions' && remainingSeconds === 0) void finishSection();
  }, [finishSection, phase, remainingSeconds]);

  if (!isAuthenticated || loading) return <div>Loading exam paper...</div>;

  if (!currentSection) return <div>No exam sections are available.</div>;

  if (phase === 'instructions') return <div className="mx-auto max-w-3xl space-y-6"><Card><CardHeader><CardTitle>{currentSection.title} instructions</CardTitle><CardDescription>{formatDuration(currentSection.duration_seconds)} section</CardDescription></CardHeader><CardContent className="space-y-5"><p className="leading-7 text-slate-700">{currentSection.instruction_text || 'Answer all questions. You may review answers while this section is active.'}</p><p className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">You cannot return to this section once submitted.</p><Button onClick={startSection}>Start Section</Button></CardContent></Card></div>;

  if (phase === 'complete') return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>{currentSection.title} complete</CardTitle><CardDescription>Moving to the next section...</CardDescription></CardHeader><CardContent><Button onClick={() => { setSectionIndex(sectionIndex + 1); setPhase('instructions'); }}>Continue</Button></CardContent></Card></div>;

  const renderSection = () => {
    if (!currentQuestion || !currentSection) return <p className="text-sm text-slate-500">No questions loaded yet.</p>;
    if (currentSection.section_type === 'listening') return <ListeningSection audioAsset={currentSection.audio ?? undefined} questions={[currentQuestion]} strictExamMode={Boolean(paper?.test)} isLocked={remainingSeconds === 0} />;
    if (currentSection.section_type === 'writing') return <WritingSection tasks={sectionQuestions.map((question, index) => ({ id: question.id, questionId: question.id, title: `Task ${index + 1}`, prompt: question.prompt, minWords: Number(question.validation_rules.min_words ?? 0), visual: question.visual_json as never }))} isLocked={remainingSeconds === 0} />;
    if (currentSection.section_type === 'speaking') return <SpeakingSection prompts={sectionQuestions.map((question, index) => ({ id: question.id, questionId: question.id, part: `Part ${index + 1}`, prompt: question.prompt, durationSeconds: Number(question.validation_rules.recording_seconds ?? 60), preparationSeconds: Number(question.validation_rules.prep_seconds ?? 0) }))} attemptId={attemptId} isLocked={remainingSeconds === 0} />;
    return <ReadingSection passage={currentSection.passage ?? undefined} questions={[currentQuestion]} title={currentSection.title} isLocked={remainingSeconds === 0} />;
  };

  return <div className="space-y-6">
    <div className="sticky top-0 z-20 border-b border-slate-200 bg-white py-4"><div className="container mx-auto flex justify-between"><div><p className="text-sm text-slate-500">{paper?.test.title}</p><h1 className="text-2xl font-semibold">{currentSection?.title ?? 'Exam Room'}</h1></div><div className="text-right"><p className="font-semibold">Time Remaining: {remainingSeconds === null ? 'Loading...' : formatDuration(remainingSeconds)}</p><p className="text-sm text-slate-500">{savingStatus}</p></div></div></div>
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]"><div className="space-y-6"><Card className="border-none bg-transparent shadow-none"><CardHeader className="px-0 pt-0"><CardTitle>{currentQuestion ? `Question ${questionIndex + 1}` : 'Section overview'}</CardTitle><CardDescription>{currentQuestion?.prompt ?? currentSection?.instruction_text}</CardDescription></CardHeader><CardContent className="p-0">{renderSection()}</CardContent></Card>
      <div className="flex items-center justify-between gap-3"><Button variant="outline" onClick={goPrevious} disabled={questionIndex === 0}>Previous</Button><Button variant="outline" onClick={goNext} disabled={questionIndex === sectionQuestions.length - 1}>Next</Button><Button onClick={() => void finishSection()} disabled={submitState === 'submitting'}>{currentSection.section_type === 'speaking' ? 'Submit Section' : 'Submit Section'}</Button></div>{submitNotice ? <p className="text-sm text-red-700">{submitNotice}</p> : null}</div>
      <Card><CardHeader><CardTitle>Question Palette</CardTitle><CardDescription>Questions in this section only.</CardDescription></CardHeader><CardContent className="grid gap-2">{sectionQuestions.map((question, index) => <button key={question.id} type="button" onClick={() => setQuestionIndex(index)} className={`rounded-lg border px-3 py-2 text-left ${question.id === currentPaperQuestion?.id ? 'border-slate-900 bg-slate-100' : 'border-slate-200'}`}><span>Q{index + 1}</span>{answers[question.id] ? <span className="ml-2 text-xs text-emerald-700">Answered</span> : null}{flaggedQuestions.includes(question.id) ? <span className="ml-2 text-xs text-amber-700">Flagged</span> : null}</button>)}</CardContent></Card>
    </div>
  </div>;
}
