import { create } from 'zustand';

export interface ExamAnswerValue {
  answer_text?: string;
  selected_options?: string[];
  value_json?: Record<string, unknown>;
}

export interface ExamPaperQuestion {
  id: string;
  order: number;
  type: string;
  prompt: string;
  instruction?: string;
  points?: number;
  options: Array<{ id: string; order: number; text: string }>;
  validation_rules: Record<string, unknown>;
  visual_json: Record<string, unknown> | null;
  question_group: { id: string; title: string; instruction: string };
}

export interface ExamPaperSection {
  id: string;
  title: string;
  section_type: string;
  order: number;
  duration_seconds: number;
  instruction_text: string;
  passage: { id: string; title: string; body_text: string; source_note?: string } | null;
  audio: { id: string; title: string; audio_file: string | null; duration_seconds: number; playback_policy: Record<string, boolean> } | null;
  question_groups: Array<{ id: string; title: string; instruction: string; order: number; questions: ExamPaperQuestion[] }>;
}

export interface ExamPaper {
  attempt_id: string;
  test: { id: string; title: string; slug: string };
  server_time: string;
  expires_at: string;
  sections: ExamPaperSection[];
}

interface ExamState {
  attemptId: string | null;
  expiresAt: string | null;
  serverTimeOffset: number;
  currentSection: string | null;
  currentQuestionIndex: number;
  paper: ExamPaper | null;
  sections: ExamPaperSection[];
  currentSectionIndex: number;
  completedSectionIds: string[];
  questions: Array<{ id: string; label: string }>; 
  answers: Record<string, ExamAnswerValue>;
  flaggedQuestions: string[];
  setAttemptContext: (attemptId: string, expiresAt: string, serverTimeOffset: number) => void;
  setQuestions: (questions: Array<{ id: string; label: string }>) => void;
  setCurrentSection: (sectionName: string) => void;
  setCurrentQuestionIndex: (index: number) => void;
  setPaper: (paper: ExamPaper) => void;
  setCurrentSectionIndex: (index: number) => void;
  completeSection: (sectionId: string) => void;
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
  paper: null,
  sections: [],
  currentSectionIndex: 0,
  completedSectionIds: [],
  questions: [],
  answers: {},
  flaggedQuestions: [],
  setAttemptContext: (attemptId, expiresAt, serverTimeOffset) =>
    set({ attemptId, expiresAt, serverTimeOffset }),
  setQuestions: (questions) => set({ questions }),
  setCurrentSection: (sectionName) => set({ currentSection: sectionName }),
  setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),
  setPaper: (paper) => set({ paper, sections: [...paper.sections].sort((left, right) => {
    const order = ['listening', 'reading', 'writing', 'speaking'];
    return (order.indexOf(left.section_type) - order.indexOf(right.section_type)) || left.order - right.order;
  }) }),
  setCurrentSectionIndex: (index) => set({ currentSectionIndex: index, currentQuestionIndex: 0, currentSection: null }),
  completeSection: (sectionId) => set((state) => ({ completedSectionIds: state.completedSectionIds.includes(sectionId) ? state.completedSectionIds : [...state.completedSectionIds, sectionId] })),
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
      paper: null,
      sections: [],
      currentSectionIndex: 0,
      completedSectionIds: [],
      questions: [],
      answers: {},
      flaggedQuestions: [],
    }),
}));
