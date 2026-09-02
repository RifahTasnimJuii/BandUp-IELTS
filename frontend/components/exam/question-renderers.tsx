'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useExamStore, type ExamAnswerValue } from '@/store/useExamStore';

export type ExamQuestionType =
  | 'mcq_single'
  | 'mcq_multiple'
  | 'true_false_not_given'
  | 'yes_no_not_given'
  | 'fill_blank'
  | 'sentence_completion'
  | 'summary_completion'
  | 'matching_headings'
  | 'matching_items'
  | 'short_answer'
  | 'writing_prompt'
  | 'speaking_prompt'
  | 'map_label';

export interface ExamQuestionOption {
  value: string;
  label: string;
}

export interface ExamQuestion {
  id: string;
  type: ExamQuestionType;
  prompt: string;
  instruction?: string;
  label?: string;
  options_json?: Array<string | Record<string, unknown>>;
  validation_rules_json?: Record<string, unknown>;
  visual_json?: Record<string, unknown> | null;
  question_group?: {
    id?: string;
    title?: string;
    instruction?: string;
  };
}

interface QuestionRendererProps {
  question: ExamQuestion;
  index: number;
  isLocked?: boolean;
}

const normalizeOptions = (options: Array<string | Record<string, unknown>> | undefined): ExamQuestionOption[] => {
  if (!Array.isArray(options)) return [];

  return options.map((option, index) => {
    if (typeof option === 'string') {
      return { value: option, label: option };
    }

    const record = option ?? {};
    const label = String(record.label ?? record.text ?? record.value ?? `Option ${index + 1}`);
    const value = String(record.value ?? record.id ?? label);

    return { value, label };
  });
};

const getSelectedValueFromAnswer = (answer?: ExamAnswerValue): string => {
  if (!answer) return '';

  if (Array.isArray(answer.selected_options) && answer.selected_options.length > 0) {
    return String(answer.selected_options[0]);
  }

  if (typeof answer.answer_text === 'string') {
    return answer.answer_text;
  }

  if (answer.value_json && typeof answer.value_json.value === 'string') {
    return answer.value_json.value;
  }

  return '';
};

const getSelectedValuesFromAnswer = (answer?: ExamAnswerValue): string[] => {
  if (!answer) return [];

  if (Array.isArray(answer.selected_options)) {
    return answer.selected_options.map(String);
  }

  if (typeof answer.answer_text === 'string') {
    return [answer.answer_text];
  }

  if (answer.value_json && Array.isArray(answer.value_json.values)) {
    return answer.value_json.values.map((item) => String(item));
  }

  return [];
};

const parseValidationLimit = (record: Record<string, unknown> | undefined, key: string): number | undefined => {
  const value = record?.[key];
  if (typeof value === 'number') return value;
  if (typeof value === 'string' && value.trim() !== '') return Number(value);
  return undefined;
};

const QuestionShell: React.FC<React.PropsWithChildren<{ question: ExamQuestion; index: number; isLocked?: boolean; onClear: () => void; }>> = ({
  question,
  index,
  isLocked,
  onClear,
  children,
}) => (
  <div
    className={`rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition ${isLocked ? 'cursor-not-allowed opacity-90' : ''}`}
    aria-disabled={isLocked}
  >
    <div className="mb-3 flex items-start justify-between gap-3">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Question {index + 1}</p>
        {question.question_group?.title ? (
          <p className="mt-1 text-xs text-slate-500">{question.question_group.title}</p>
        ) : null}
      </div>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onClear}
        disabled={isLocked}
        className="text-slate-600 hover:text-slate-900"
      >
        Clear Answer
      </Button>
    </div>

    <div className="space-y-3">
      {question.instruction ? <p className="text-xs uppercase tracking-wide text-slate-500">{question.instruction}</p> : null}
      <p className="text-base font-medium leading-7 text-slate-800">{question.prompt}</p>
      {children}
    </div>

    {isLocked ? (
      <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800">
        Time&apos;s up - Answers locked
      </div>
    ) : null}
  </div>
);

export const MCQSingle: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answerValue = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const options = normalizeOptions(question.options_json);

  const handleClear = () => {
    if (!isLocked) {
      setAnswer(question.id, { selected_options: [] });
    }
  };

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={handleClear}>
      <RadioGroup
        value={getSelectedValueFromAnswer(answerValue)}
        onValueChange={(value) => {
          if (!isLocked) {
            setAnswer(question.id, { selected_options: [value] });
          }
        }}
        className="space-y-3"
      >
        {options.map((option) => (
          <div key={option.value} className="flex items-center space-x-3 rounded-lg border border-slate-200 p-3">
            <RadioGroupItem value={option.value} id={`${question.id}-${option.value}`} disabled={isLocked} />
            <Label htmlFor={`${question.id}-${option.value}`} className="flex-1 cursor-pointer text-sm text-slate-700">
              {option.label}
            </Label>
          </div>
        ))}
      </RadioGroup>
    </QuestionShell>
  );
};

export const MCQMultiple: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answerValue = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const options = normalizeOptions(question.options_json);
  const selectedValues = getSelectedValuesFromAnswer(answerValue);

  const handleToggle = (value: string, checked: boolean) => {
    if (isLocked) return;

    const next = checked ? [...selectedValues, value] : selectedValues.filter((item) => item !== value);
    setAnswer(question.id, { selected_options: next });
  };

  const handleClear = () => {
    if (!isLocked) {
      setAnswer(question.id, { selected_options: [] });
    }
  };

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={handleClear}>
      <div className="space-y-3">
        {options.map((option) => {
          const checked = selectedValues.includes(option.value);
          return (
            <label
              key={option.value}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition ${checked ? 'border-slate-900 bg-slate-50' : 'border-slate-200 hover:border-slate-300'}`}
            >
              <Checkbox
                checked={checked}
                onCheckedChange={(value) => handleToggle(option.value, Boolean(value))}
                disabled={isLocked}
              />
              <span className="text-sm text-slate-700">{option.label}</span>
            </label>
          );
        })}
      </div>
    </QuestionShell>
  );
};

export const BooleanChoiceQuestion: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answerValue = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const options = normalizeOptions(question.options_json);
  const defaultOptions = options.length > 0 ? options : [{ value: 'true', label: 'True' }, { value: 'false', label: 'False' }, { value: 'not_given', label: 'Not Given' }];
  const currentValue = getSelectedValueFromAnswer(answerValue);

  const handleClear = () => {
    if (!isLocked) {
      setAnswer(question.id, { selected_options: [] });
    }
  };

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={handleClear}>
      <RadioGroup
        value={currentValue}
        onValueChange={(value) => {
          if (!isLocked) {
            setAnswer(question.id, { selected_options: [value] });
          }
        }}
        className="grid gap-3 sm:grid-cols-3"
      >
        {defaultOptions.map((option) => (
          <div key={option.value} className="flex items-center space-x-2 rounded-lg border border-slate-200 p-3">
            <RadioGroupItem value={option.value} id={`${question.id}-${option.value}`} disabled={isLocked} />
            <Label htmlFor={`${question.id}-${option.value}`} className="cursor-pointer text-sm text-slate-700">
              {option.label}
            </Label>
          </div>
        ))}
      </RadioGroup>
    </QuestionShell>
  );
};

export const TextAnswerQuestion: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answerValue = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const validationRules = question.validation_rules_json ?? {};
  const maxWords = parseValidationLimit(validationRules, 'max_words');
  const maxChars = parseValidationLimit(validationRules, 'max_chars');
  const currentValue = typeof answerValue?.answer_text === 'string' ? answerValue.answer_text : '';

  const handleClear = () => {
    if (!isLocked) {
      setAnswer(question.id, { answer_text: '' });
    }
  };

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={handleClear}>
      <div className="space-y-2">
        <Input
          value={currentValue}
          placeholder="Type your answer here..."
          maxLength={maxChars}
          disabled={isLocked}
          onChange={(event) => {
            if (!isLocked) {
              setAnswer(question.id, { answer_text: event.target.value });
            }
          }}
          className="min-h-[48px] rounded-xl border-slate-200 bg-white text-sm"
        />
        {maxWords || maxChars ? (
          <p className="text-xs text-slate-500">
            {maxWords ? `Max words: ${maxWords}` : null}
            {maxWords && maxChars ? ' • ' : null}
            {maxChars ? `Max characters: ${maxChars}` : null}
          </p>
        ) : null}
      </div>
    </QuestionShell>
  );
};

export const MatchingQuestion: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answerValue = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const options = normalizeOptions(question.options_json);
  const currentValue = typeof answerValue?.answer_text === 'string' ? answerValue.answer_text : '';

  const handleClear = () => {
    if (!isLocked) {
      setAnswer(question.id, { answer_text: '' });
    }
  };

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={handleClear}>
      <div className="space-y-3">
        <Select
          value={currentValue || undefined}
          onValueChange={(value) => {
            if (!isLocked) {
              setAnswer(question.id, { answer_text: value });
            }
          }}
          disabled={isLocked}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select an option" />
          </SelectTrigger>
          <SelectContent>
            {options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </QuestionShell>
  );
};

export const MapLabelRenderer: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  const answer = useExamStore((state) => state.answers[question.id]);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const visual = question.visual_json ?? {};
  const spots = Array.isArray(visual.spots) ? visual.spots as Array<{ letter: string; x: number; y: number }> : [];
  const currentValue = typeof answer?.answer_text === 'string' ? answer.answer_text : '';

  return (
    <QuestionShell question={question} index={index} isLocked={isLocked} onClear={() => setAnswer(question.id, { answer_text: '' })}>
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-900">
          <svg viewBox="0 0 100 100" className="h-72 w-full" role="img" aria-label={String(visual.title ?? 'Listening map')}>
            <rect width="100" height="100" fill="currentColor" className="text-slate-100 dark:text-slate-800" />
            <path d="M5 48H95M22 5V95M5 18L95 82M8 88L92 12" stroke="currentColor" strokeWidth="5" className="text-white dark:text-slate-700" />
            <path d="M5 48H95M22 5V95M5 18L95 82M8 88L92 12" stroke="currentColor" strokeWidth="1" className="text-slate-300 dark:text-slate-600" />
            {spots.map((spot) => <g key={spot.letter}><circle cx={spot.x} cy={spot.y} r="5" className="fill-sky-600 dark:fill-sky-400" /><text x={spot.x} y={spot.y + 1.5} textAnchor="middle" className="fill-white text-[4px] font-bold">{spot.letter}</text></g>)}
            {visual.north ? <text x="92" y="8" textAnchor="middle" className="fill-slate-700 text-[5px] font-bold dark:fill-slate-200">N</text> : null}
          </svg>
        </div>
        <Select value={currentValue || undefined} onValueChange={(value) => setAnswer(question.id, { answer_text: value })} disabled={isLocked}>
          <SelectTrigger><SelectValue placeholder="Select a letter" /></SelectTrigger>
          <SelectContent>{'ABCDEFGH'.split('').map((letter) => <SelectItem key={letter} value={letter}>{letter}</SelectItem>)}</SelectContent>
        </Select>
      </div>
  </QuestionShell>
  );
};

export const QuestionRenderer: React.FC<QuestionRendererProps> = ({ question, index, isLocked = false }) => {
  switch (question.type) {
    case 'mcq_single':
      return <MCQSingle question={question} index={index} isLocked={isLocked} />;
    case 'mcq_multiple':
      return <MCQMultiple question={question} index={index} isLocked={isLocked} />;
    case 'true_false_not_given':
    case 'yes_no_not_given':
      return <BooleanChoiceQuestion question={question} index={index} isLocked={isLocked} />;
    case 'fill_blank':
    case 'sentence_completion':
    case 'summary_completion':
    case 'short_answer':
      return <TextAnswerQuestion question={question} index={index} isLocked={isLocked} />;
    case 'matching_headings':
    case 'matching_items':
      return <MatchingQuestion question={question} index={index} isLocked={isLocked} />;
    case 'map_label':
      return <MapLabelRenderer question={question} index={index} isLocked={isLocked} />;
    default:
      return <TextAnswerQuestion question={question} index={index} isLocked={isLocked} />;
  }
};

export default QuestionRenderer;
