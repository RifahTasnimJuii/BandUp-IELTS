'use client';

import * as React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { QuestionRenderer, type ExamQuestion } from '@/components/exam/question-renderers';
import Passage from '@/components/exam/passage';

export interface ReadingSectionProps {
  passage?: {
    title?: string;
    body_text?: string;
    source_note?: string;
  };
  questions?: ExamQuestion[];
  title?: string;
  isLocked?: boolean;
}

export const ReadingSection: React.FC<ReadingSectionProps> = ({
  passage,
  questions = [],
  title,
  isLocked = false,
}) => {
  const groupedQuestions = React.useMemo(() => {
    const groups = new Map<string, ExamQuestion[]>();

    questions.forEach((question) => {
      const groupKey = question.question_group?.id ?? question.question_group?.title ?? 'default';
      const existingGroup = groups.get(groupKey) ?? [];
      existingGroup.push(question);
      groups.set(groupKey, existingGroup);
    });

    return Array.from(groups.entries()).map(([key, items]) => ({
      id: key,
      title: items[0]?.question_group?.title ?? 'Questions',
      instruction: items[0]?.question_group?.instruction ?? '',
      questions: items,
    }));
  }, [questions]);

  const content = (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
      <div className="lg:sticky lg:top-24 lg:self-start">
        <Passage
          title={passage?.title ?? title ?? 'Reading Passage'}
          bodyText={passage?.body_text ?? ''}
          sourceNote={passage?.source_note}
        />
      </div>

      <div className="space-y-6">
        {groupedQuestions.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            No reading questions available yet.
          </div>
        ) : (
          groupedQuestions.map((group) => (
            <div key={group.id} className="space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <h3 className="text-base font-semibold text-slate-900">{group.title}</h3>
                {group.instruction ? <p className="mt-1 text-sm text-slate-600">{group.instruction}</p> : null}
              </div>

              {group.questions.map((question, index) => (
                <QuestionRenderer key={question.id} question={question} index={index} isLocked={isLocked} />
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <>
      <div className="hidden lg:block">{content}</div>
      <div className="lg:hidden">
        <Tabs defaultValue="passage" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="passage">Passage</TabsTrigger>
            <TabsTrigger value="questions">Questions</TabsTrigger>
          </TabsList>
          <TabsContent value="passage" className="mt-4">
            <Passage
              title={passage?.title ?? title ?? 'Reading Passage'}
              bodyText={passage?.body_text ?? ''}
              sourceNote={passage?.source_note}
            />
          </TabsContent>
          <TabsContent value="questions" className="mt-4 space-y-4">
            {groupedQuestions.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
                No reading questions available yet.
              </div>
            ) : (
              groupedQuestions.map((group) => (
                <div key={group.id} className="space-y-4">
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <h3 className="text-base font-semibold text-slate-900">{group.title}</h3>
                    {group.instruction ? <p className="mt-1 text-sm text-slate-600">{group.instruction}</p> : null}
                  </div>

                  {group.questions.map((question, index) => (
                    <QuestionRenderer key={question.id} question={question} index={index} isLocked={isLocked} />
                  ))}
                </div>
              ))
            )}
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
};

export default ReadingSection;
