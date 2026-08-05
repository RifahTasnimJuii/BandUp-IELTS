import { create } from 'zustand';

export interface ExamAnswerValue {
  answer_text?: string;
  selected_options?: string[];
  value_json?: Record<string, unknown>;
}

interface ExamState {
  attemptId: string | null;
  expiresAt: string | null;
  serverTimeOffset: number;
  currentSection: string | null;
  currentQuestionIndex: number;
  questions: Array<{ id: string; label: string }>; 
  answers: Record<string, ExamAnswerValue>;
  flaggedQuestions: string[];
  setAttemptContext: (attemptId: string, expiresAt: string, serverTimeOffset: number) => void;
  setQuestions: (questions: Array<{ id: string; label: string }>) => void;
  setCurrentSection: (sectionName: string) => void;
  setCurrentQuestionIndex: (index: number) => void;
  setAnswer: (questionId: string, value: ExamAnswerValue) => void;
  toggleFlaggedQuestion: (questionId: string) => void;
  resetExam: () => void;
}

export const useExamStore = create<ExamState>((set) => ({
  attemptId: null,
  expiresAt: null,
  serverTimeOffset: 0,
  currentSection: null,
  currentQuestionIndex: 0,
  questions: [],
  answers: {},
  flaggedQuestions: [],
  setAttemptContext: (attemptId, expiresAt, serverTimeOffset) =>
    set({ attemptId, expiresAt, serverTimeOffset }),
  setQuestions: (questions) => set({ questions }),
  setCurrentSection: (sectionName) => set({ currentSection: sectionName }),
  setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),
  setAnswer: (questionId, value) =>
    set((state) => ({
      answers: {
        ...state.answers,
        [questionId]: {
          ...state.answers[questionId],
          ...value,
        },
      },
    })),
  toggleFlaggedQuestion: (questionId) =>
    set((state) => ({
      flaggedQuestions: state.flaggedQuestions.includes(questionId)
        ? state.flaggedQuestions.filter((id) => id !== questionId)
        : [...state.flaggedQuestions, questionId],
    })),
  resetExam: () =>
    set({
      attemptId: null,
      expiresAt: null,
      serverTimeOffset: 0,
      currentSection: null,
      currentQuestionIndex: 0,
      questions: [],
      answers: {},
      flaggedQuestions: [],
    }),
}));
