'use client';

import * as React from 'react';
import { Play, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AudioPlayer from '@/components/exam/audio-player';
import { QuestionRenderer, type ExamQuestion } from '@/components/exam/question-renderers';
import { speak, stopAllAudio } from '@/lib/audio-controller';

interface ListeningPart { order: number; title: string; audio_url: string | null; questions: ExamQuestion[] }
export interface ListeningSectionProps { audioAsset?: { title?: string; audio_file?: string; transcript?: string; playback_policy?: { allow_replay?: boolean; allow_seek?: boolean } }; parts?: ListeningPart[]; transcript?: string; questions?: ExamQuestion[]; strictExamMode?: boolean; isLocked?: boolean }

export const ListeningSection: React.FC<ListeningSectionProps> = ({ audioAsset, parts = [], transcript, questions = [], strictExamMode = false, isLocked = false }) => {
  const groups = React.useMemo(() => { const map = new Map<string, ExamQuestion[]>(); questions.forEach((question) => { const key = question.question_group?.id ?? 'default'; map.set(key, [...(map.get(key) ?? []), question]); }); return Array.from(map.values()); }, [questions]);
  const actualParts = parts.length ? parts : Array.from({ length: 4 }, (_, index) => ({ order: index + 1, title: `Listening Part ${index + 1}`, audio_url: null, questions: groups[index] ?? [] }));
  React.useEffect(() => () => stopAllAudio(), []);
  const playFallback = (part: ListeningPart) => { if (!isLocked) speak(part.title + '. ' + part.questions.map((question) => question.prompt).join('. ')); };
  return <div className="space-y-6">
    <div className="flex items-center gap-3"><Volume2 size={18} /><span className="font-medium">Listening test: four parts</span></div>
    {actualParts.map((part) => <section key={part.order} className="border border-slate-200 bg-white p-4"><div className="mb-4 flex items-center justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Part {part.order} (Questions {(part.order - 1) * 10 + 1}–{part.order * 10})</p><h3 className="text-lg font-semibold text-slate-900">{part.title}</h3></div>{part.audio_url ? <AudioPlayer src={part.audio_url} title={`Part ${part.order}`} strictExamMode={strictExamMode} allowReplay={false} allowSeek={false} isLocked={isLocked} /> : <Button type="button" variant="outline" onClick={() => playFallback(part)} disabled={isLocked}><Play size={15} className="mr-2" /> Play Part {part.order}</Button>}</div><div className="space-y-4">{part.questions.map((question, index) => <QuestionRenderer key={question.id} question={question} index={(part.order - 1) * 10 + index} isLocked={isLocked} />)}</div></section>)}
    {!parts.length && audioAsset ? <AudioPlayer src={audioAsset.audio_file} transcript={audioAsset.transcript ?? transcript} title={audioAsset.title ?? 'Listening Audio'} strictExamMode={strictExamMode} allowReplay={false} allowSeek={false} isLocked={isLocked} /> : null}
  </div>;
};
export default ListeningSection;
