'use client';

import * as React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AudioPlayer from '@/components/exam/audio-player';
import { QuestionRenderer, type ExamQuestion } from '@/components/exam/question-renderers';

export interface ListeningSectionProps {
  audioAsset?: {
    title?: string;
    audio_file?: string;
    playback_policy?: {
      allow_replay?: boolean;
      allow_seek?: boolean;
    };
  };
  transcript?: string;
  questions?: ExamQuestion[];
  strictExamMode?: boolean;
  isLocked?: boolean;
}

export const ListeningSection: React.FC<ListeningSectionProps> = ({
  audioAsset,
  transcript,
  questions = [],
  strictExamMode = false,
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

  const playbackPolicy = audioAsset?.playback_policy ?? {};
  const playerAllowReplay = playbackPolicy.allow_replay ?? true;
  const playerAllowSeek = playbackPolicy.allow_seek ?? true;

  return (
    <div className="space-y-6">
      <AudioPlayer
        src={audioAsset?.audio_file}
        title={audioAsset?.title ?? 'Listening Audio'}
        strictExamMode={strictExamMode}
        allowReplay={playerAllowReplay}
        allowSeek={playerAllowSeek}
        isLocked={isLocked}
      />

      {transcript ? (
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-7 text-slate-700">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Transcript</p>
          <div className="whitespace-pre-wrap">{transcript}</div>
        </div>
      ) : null}

      <div className="hidden lg:block">
        <div className="space-y-4">
          {groupedQuestions.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
              No listening questions available yet.
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

      <div className="lg:hidden">
        <Tabs defaultValue="questions" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="questions">Questions</TabsTrigger>
            <TabsTrigger value="transcript">Transcript</TabsTrigger>
          </TabsList>
          <TabsContent value="questions" className="mt-4 space-y-4">
            {groupedQuestions.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
                No listening questions available yet.
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
          <TabsContent value="transcript" className="mt-4">
            {transcript ? (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                {transcript}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
                No transcript provided.
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ListeningSection;
