'use client';

import * as React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useExamStore } from '@/store/useExamStore';
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface WritingTask {
  id: string;
  title: string;
  prompt: string;
  minWords: number;
  questionId?: string;
  visual?: {
    chart_type?: 'line' | 'bar';
    title?: string;
    x_label?: string;
    y_label?: string;
    series?: Array<{ name: string; data: Array<{ label: string; value: number }> }>;
  } | null;
}

interface WritingSectionProps {
  tasks?: WritingTask[];
  isLocked?: boolean;
}

const defaultTasks: WritingTask[] = [
  {
    id: 'task1',
    title: 'Task 1',
    prompt: 'The charts below show... Describe the main information and make comparisons where relevant.',
    minWords: 150,
    questionId: 'writing-task-1',
  },
  {
    id: 'task2',
    title: 'Task 2',
    prompt: 'Some people believe... To what extent do you agree or disagree? Give reasons and examples.',
    minWords: 250,
    questionId: 'writing-task-2',
  },
];

const countWords = (value: string) => {
  const normalized = value.trim();
  if (!normalized) return 0;
  return normalized.split(/\s+/).filter(Boolean).length;
};

export const WritingSection: React.FC<WritingSectionProps> = ({
  tasks = defaultTasks,
  isLocked = false,
}) => {
  const [activeTab, setActiveTab] = React.useState(tasks[0]?.id ?? 'task1');
  const setAnswer = useExamStore((state) => state.setAnswer);

  const activeTask = tasks.find((task) => task.id === activeTab) ?? tasks[0] ?? defaultTasks[0];
  const answer = useExamStore((state) => state.answers[activeTask.questionId ?? activeTask.id]);
  const value = typeof answer?.answer_text === 'string' ? answer.answer_text : '';
  const wordCount = countWords(value);
  const belowMinWords = wordCount < activeTask.minWords;

  React.useEffect(() => {
    if (tasks.length > 0 && !tasks.some((task) => task.id === activeTab)) {
      setActiveTab(tasks[0].id);
    }
  }, [activeTab, tasks]);

  const handleChange = (nextValue: string) => {
    if (isLocked) return;
    setAnswer(activeTask.questionId ?? activeTask.id, { answer_text: nextValue });
  };

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          {tasks.map((task) => (
            <TabsTrigger key={task.id} value={task.id}>
              {task.title}
            </TabsTrigger>
          ))}
        </TabsList>

        {tasks.map((task) => (
          <TabsContent key={task.id} value={task.id} className="mt-5 space-y-5">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <h3 className="text-lg font-semibold text-slate-900">{task.title}</h3>
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                  {wordCount} words
                </span>
              </div>

              <p className="text-sm leading-7 text-slate-700">{task.prompt}</p>
            </div>

            {task.visual?.series?.length ? (
              <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
                <p className="mb-3 text-sm font-semibold text-slate-800 dark:text-slate-100">{task.visual.title}</p>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    {task.visual.chart_type === 'bar' ? (
                      <BarChart data={task.visual.series[0].data.map((point, index) => ({ label: point.label, ...Object.fromEntries(task.visual!.series!.map((series) => [series.name, series.data[index]?.value ?? 0])) }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.3} /><XAxis dataKey="label" label={{ value: task.visual.x_label, position: 'insideBottom', offset: -5 }} /><YAxis label={{ value: task.visual.y_label, angle: -90, position: 'insideLeft' }} /><Tooltip /><Legend />{task.visual.series.map((series) => <Bar key={series.name} dataKey={series.name} fill={series.name === '2019' ? '#0284c7' : '#f59e0b'} />)}</BarChart>
                    ) : (
                      <LineChart data={task.visual.series[0].data.map((point, index) => ({ label: point.label, ...Object.fromEntries(task.visual!.series!.map((series) => [series.name, series.data[index]?.value ?? 0])) }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" opacity={0.3} /><XAxis dataKey="label" label={{ value: task.visual.x_label, position: 'insideBottom', offset: -5 }} /><YAxis label={{ value: task.visual.y_label, angle: -90, position: 'insideLeft' }} /><Tooltip /><Legend />{task.visual.series.map((series, index) => <Line key={series.name} type="monotone" dataKey={series.name} stroke={index === 0 ? '#0284c7' : '#f59e0b'} strokeWidth={3} />)}</LineChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>
            ) : null}

            <div className="space-y-3">
              <Textarea
                value={value}
                onChange={(event) => handleChange(event.target.value)}
                disabled={isLocked}
                placeholder="Type your answer here..."
                className="min-h-[320px] resize-y text-base leading-7"
              />

              {belowMinWords && !isLocked ? (
                <div className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800">
                  Warning: word count is below the minimum required for {task.title} ({task.minWords} words).
                </div>
              ) : null}

              {isLocked ? (
                <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
                  Time&apos;s up - Answers locked
                </div>
              ) : null}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default WritingSection;
