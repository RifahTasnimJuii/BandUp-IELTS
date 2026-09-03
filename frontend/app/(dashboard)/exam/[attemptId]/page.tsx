'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ListeningSection } from '@/components/exam/listening-section';
import { ReadingSection } from '@/components/exam/reading-section';
import { SpeakingSection } from '@/components/exam/sections/speaking-section';
import { WritingSection } from '@/components/exam/sections/writing-section';
import type { ExamQuestion } from '@/components/exam/question-renderers';
import { autosaveAnswer, completeSection as completeSectionApi, getAttemptPaper, getAttemptState, startSection as startSectionApi, submitAttempt } from '@/lib/api/exam';
import { useAuthStore } from '@/store/useAuthStore';
import { useExamStore, type ExamPaperQuestion } from '@/store/useExamStore';
import { absoluteAudioUrl, stopAllAudio } from '@/lib/audio-controller';

const formatDuration = (seconds: number) => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
const mapQuestion = (question: ExamPaperQuestion): ExamQuestion => ({ id: question.id, type: question.type as ExamQuestion['type'], prompt: question.prompt, instruction: question.instruction, options_json: question.options.map((option) => ({ value: option.text.match(/^([A-Z])\./)?.[1] ?? option.text, label: option.text })), validation_rules_json: question.validation_rules, visual_json: question.visual_json, prompt_audio_url: absoluteAudioUrl(question.prompt_audio_url), question_group: question.question_group });

export default function ExamRoomPage({ params }: { params: { attemptId: string } }) {
  const { attemptId } = params;
  const router = useRouter();
  const selectedSectionId = useSearchParams().get('section');
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingStatus, setSavingStatus] = useState('All changes saved');
  const [submitState, setSubmitState] = useState<'idle' | 'submitting'>('idle');
  const [submitNotice, setSubmitNotice] = useState<string | null>(null);
  const [phase, setPhase] = useState<'instructions' | 'questions'>('instructions');
  const paper = useExamStore((state) => state.paper);
  const sections = useExamStore((state) => state.sections);
  const answers = useExamStore((state) => state.answers);
  const flaggedQuestions = useExamStore((state) => state.flaggedQuestions);
  const completedSectionIds = useExamStore((state) => state.completedSectionIds);
  const setPaper = useExamStore((state) => state.setPaper);
  const setAttemptContext = useExamStore((state) => state.setAttemptContext);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const completeSection = useExamStore((state) => state.completeSection);
  const setCompletedSections = useExamStore((state) => state.setCompletedSections);
  const hydrated = useRef(false);

  useEffect(() => {
    if (!isAuthenticated) { router.push('/login'); return; }
    let cancelled = false;
    Promise.all([getAttemptPaper(attemptId), getAttemptState(attemptId)]).then(([nextPaper, state]) => {
      if (cancelled) return;
      setPaper(nextPaper);
      setAttemptContext(attemptId, state.expires_at, Date.parse(nextPaper.server_time) - Date.now());
      setRemainingSeconds(state.remaining_seconds ?? 0);
      setCompletedSections((state.section_states ?? []).filter((item) => item.state === 'completed').map((item) => item.section));
      state.answers.forEach((answer) => setAnswer(answer.question, { answer_text: answer.answer_text, selected_options: answer.selected_options, value_json: answer.value_json }));
      hydrated.current = true;
      setLoading(false);
    }).catch(() => { setSubmitNotice('Unable to load the exam paper.'); setLoading(false); });
    return () => { cancelled = true; };
  }, [attemptId, isAuthenticated, router, setAnswer, setAttemptContext, setCompletedSections, setPaper]);

  const currentSection = sections.find((section) => section.id === selectedSectionId);
  const sectionQuestions = useMemo(() => currentSection?.question_groups.flatMap((group) => group.questions) ?? [], [currentSection]);

  useEffect(() => {
    if (!hydrated.current || !selectedSectionId) return;
    const pending = sectionQuestions.filter((question) => answers[question.id]);
    if (!pending.length) return;
    setSavingStatus('Saving...');
    const timer = window.setTimeout(() => Promise.all(pending.map((question) => autosaveAnswer(attemptId, question.id, answers[question.id], flaggedQuestions.includes(question.id)))).then(() => setSavingStatus('All changes saved')).catch((error) => { console.error('Autosave failed', { attemptId, questionIds: pending.map((question) => question.id), error }); setSavingStatus('Save failed'); }), 250);
    return () => window.clearTimeout(timer);
  }, [answers, attemptId, flaggedQuestions, sectionQuestions, selectedSectionId]);

  useEffect(() => {
    if (!selectedSectionId || phase !== 'questions' || remainingSeconds === null || remainingSeconds <= 0) return;
    const timer = window.setInterval(() => setRemainingSeconds((value) => Math.max((value ?? 1) - 1, 0)), 1000);
    return () => window.clearInterval(timer);
  }, [phase, remainingSeconds, selectedSectionId]);

  const handleSubmit = useCallback(async () => {
    if (submitState === 'submitting') return;
    setSubmitState('submitting');
    try { await submitAttempt(attemptId, answers); router.push(`/results/${attemptId}`); } catch { setSubmitNotice('Submission failed. Please try again.'); setSubmitState('idle'); }
  }, [answers, attemptId, router, submitState]);

  const finishSection = useCallback(async () => {
    if (!currentSection || completedSectionIds.includes(currentSection.id)) return;
    stopAllAudio();
    await completeSectionApi(attemptId, currentSection.id);
    completeSection(currentSection.id);
    if (completedSectionIds.length + 1 >= sections.length) await handleSubmit();
    else router.push(`/exam/${attemptId}`);
  }, [attemptId, completeSection, completedSectionIds, currentSection, handleSubmit, router, sections.length]);

  useEffect(() => {
    if (selectedSectionId && phase === 'questions' && remainingSeconds === 0) {
      setSubmitNotice("Time's up! Submitting...");
      void handleSubmit();
    }
  }, [handleSubmit, phase, remainingSeconds, selectedSectionId]);

  if (!isAuthenticated || loading) return <div>Loading exam paper...</div>;
  if (!paper) return <div>No exam sections are available.</div>;

  if (!selectedSectionId) {
    const completedCount = completedSectionIds.length;
    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <div><p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Mock Test Hub</p><h1 className="mt-2 text-3xl font-bold text-slate-900">{paper.test.title}</h1><p className="mt-2 text-slate-600">Choose any section to practise. Your progress is saved independently for each section.</p></div>
        <div className="space-y-2"><div className="flex justify-between text-sm font-medium"><span>{completedCount}/{sections.length} sections complete</span><span>{Math.round((completedCount / Math.max(sections.length, 1)) * 100)}%</span></div><div className="h-3 overflow-hidden rounded-full bg-slate-200"><div className="h-full bg-emerald-600" style={{ width: `${(completedCount / Math.max(sections.length, 1)) * 100}%` }} /></div></div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {sections.map((section) => { const completed = completedSectionIds.includes(section.id); return <Card key={section.id} className="border-slate-200"><CardHeader><CardTitle>{section.title}</CardTitle><CardDescription>{Math.round(section.duration_seconds / 60)} minutes · {section.question_groups.flatMap((group) => group.questions).length} questions</CardDescription></CardHeader><CardContent className="space-y-4"><span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${completed ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>{completed ? 'Completed ✓' : 'Not Started'}</span><Button className="w-full" variant={completed ? 'outline' : 'default'} onClick={() => router.push(`/exam/${attemptId}?section=${section.id}`)}>{completed ? 'Review Section' : 'Start Section'}</Button></CardContent></Card>; })}
        </div>
        {completedCount === sections.length ? <Button onClick={() => router.push(`/results/${attemptId}`)}>View Results</Button> : null}
      </div>
    );
  }

  if (!currentSection) return <div>No exam section is available.</div>;
  const questions = sectionQuestions.map(mapQuestion);
  const renderSection = () => {
    if (currentSection.section_type === 'listening') return <ListeningSection audioAsset={currentSection.audio ? { ...currentSection.audio, audio_file: absoluteAudioUrl(currentSection.audio.audio_file) } : undefined} parts={currentSection.parts?.map((part) => ({ ...part, audio_url: absoluteAudioUrl(part.audio_url), questions: part.questions.map(mapQuestion) }))} questions={questions} strictExamMode isLocked={remainingSeconds === 0} />;
    if (currentSection.section_type === 'writing') return <WritingSection tasks={sectionQuestions.map((question, index) => ({ id: question.id, questionId: question.id, title: `Task ${index + 1}`, prompt: question.prompt, minWords: Number(question.validation_rules.min_words ?? 0), visual: question.visual_json as never }))} isLocked={remainingSeconds === 0} />;
    if (currentSection.section_type === 'speaking') return <SpeakingSection prompts={sectionQuestions.map((question, index) => ({ id: question.id, questionId: question.id, part: `Part ${index + 1}`, prompt: question.prompt, promptAudioFile: absoluteAudioUrl(question.prompt_audio_url) ?? undefined, durationSeconds: Number(question.validation_rules.recording_seconds ?? 60), preparationSeconds: Number(question.validation_rules.prep_seconds ?? 0) }))} examinerAudioAssets={currentSection.speaking_audio_assets?.map((asset) => ({ ...asset, audio_url: absoluteAudioUrl(asset.audio_url) ?? null }))} attemptId={attemptId} isLocked={remainingSeconds === 0} />;
    return <ReadingSection passage={currentSection.passage ?? undefined} passages={currentSection.passages} questions={questions} title={currentSection.title} isLocked={remainingSeconds === 0} />;
  };

  if (phase === 'instructions') return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>{currentSection.title} instructions</CardTitle><CardDescription>{formatDuration(currentSection.duration_seconds)} section</CardDescription></CardHeader><CardContent className="space-y-5"><p>{currentSection.instruction_text}</p><Button onClick={() => { void startSectionApi(attemptId, currentSection.id); setRemainingSeconds(currentSection.duration_seconds); setPhase('questions'); }}>Start Section</Button></CardContent></Card></div>;
  return <div className="space-y-6"><div className="sticky top-0 z-20 border-b border-slate-200 bg-white py-4"><div className="flex justify-between"><div><p className="text-sm text-slate-500">{paper.test.title}</p><h1 className="text-2xl font-semibold">{currentSection.title}</h1></div><div className="text-right"><p className="font-semibold">Time Remaining: {formatDuration(remainingSeconds ?? 0)}</p><p className="text-sm text-slate-500">{savingStatus}</p></div></div></div><Card className="border-none bg-transparent shadow-none"><CardContent className="p-0">{renderSection()}</CardContent></Card><div className="flex justify-end gap-3"><Button variant="outline" onClick={() => router.push(`/exam/${attemptId}`)}>Back to Hub</Button><Button onClick={() => void finishSection()} disabled={submitState === 'submitting'}>Submit Section</Button></div>{submitNotice ? <p className="text-sm text-red-700">{submitNotice}</p> : null}</div>;
}
