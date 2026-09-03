'use client';

import * as React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { QuestionRenderer, type ExamQuestion } from '@/components/exam/question-renderers';
import Passage from '@/components/exam/passage';

interface ReadingPassage { id: string; title?: string; body_text?: string; source_note?: string }
export interface ReadingSectionProps { passage?: ReadingPassage; passages?: ReadingPassage[]; questions?: ExamQuestion[]; title?: string; isLocked?: boolean }

export const ReadingSection: React.FC<ReadingSectionProps> = ({ passage, passages = [], questions = [], title, isLocked = false }) => {
  const available = React.useMemo(() => passages.length ? passages : passage ? [passage] : [], [passage, passages]);
  const [activeId, setActiveId] = React.useState(available[0]?.id ?? '');
  const refs = React.useRef<Record<string, HTMLDivElement | null>>({});
  React.useEffect(() => { if (!available.some((item) => item.id === activeId)) setActiveId(available[0]?.id ?? ''); }, [activeId, available]);
  const groups = React.useMemo(() => {
    const byPassage = new Map<string, ExamQuestion[][]>();
    questions.forEach((question) => { const passageId = question.question_group?.passage_id ?? 'default'; const current = byPassage.get(passageId) ?? []; const groupId = question.question_group?.id ?? 'default'; const group = current.find((items) => items[0]?.question_group?.id === groupId); if (group) group.push(question); else current.push([question]); byPassage.set(passageId, current); });
    return byPassage;
  }, [questions]);
  const activeIndex = Math.max(available.findIndex((item) => item.id === activeId), 0);
  const activeGroups = groups.get(available[activeIndex]?.id ?? 'default') ?? [];
  const offset = [0, 13, 26][activeIndex] ?? 0;
  const panel = <div className="space-y-4">{activeGroups.map((items, groupIndex) => { const start = offset + activeGroups.slice(0, groupIndex).reduce((sum, group) => sum + group.length, 0); const key = items[0]?.question_group?.id ?? String(groupIndex); return <div key={key} ref={(node) => { refs.current[key] = node; }}><h3 className="mb-2 border-b border-slate-200 pb-2 font-semibold text-slate-800">Questions {start + 1}–{start + items.length} <span className="font-normal text-slate-500">• {items[0]?.question_group?.instruction}</span></h3>{items.map((question, index) => <QuestionRenderer key={question.id} question={question} index={start + index} isLocked={isLocked} />)}</div>; })}</div>;
  return <Tabs value={activeId} onValueChange={setActiveId} className="space-y-4"><TabsList className="grid w-full grid-cols-3">{available.map((item, index) => <TabsTrigger key={item.id} value={item.id}>Passage {index + 1} (Q{[1, 14, 27][index]}–{[13, 26, 40][index]})</TabsTrigger>)}</TabsList><div className="flex gap-2 overflow-x-auto">{activeGroups.map((items, index) => { const start = offset + activeGroups.slice(0, index).reduce((sum, group) => sum + group.length, 0); const key = items[0]?.question_group?.id ?? String(index); return <button key={key} type="button" className="shrink-0 rounded-full border px-3 py-1 text-xs" onClick={() => refs.current[key]?.scrollIntoView({ behavior: 'smooth' })}>{start + 1}–{start + items.length}</button>; })}</div><div className="hidden lg:block"><div className="grid gap-4 lg:h-[calc(100vh-13rem)] lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]"><div className="overflow-y-auto"><Passage title={available[activeIndex]?.title ?? title} bodyText={available[activeIndex]?.body_text ?? ''} sourceNote={available[activeIndex]?.source_note} /></div><div className="overflow-y-auto">{panel}</div></div></div>{available.map((item, index) => <TabsContent key={item.id} value={item.id} className="lg:hidden"><Passage title={item.title} bodyText={item.body_text} sourceNote={item.source_note} />{index === activeIndex ? <div className="mt-4">{panel}</div> : null}</TabsContent>)}</Tabs>;
};
export default ReadingSection;
