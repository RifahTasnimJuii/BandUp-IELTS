import api from '../api';
import type { ExamPaper, ExamAnswerValue } from '@/store/useExamStore';

export interface StartAttemptResponse {
  attempt_id: string;
  started_at: string;
  expires_at: string;
  server_time: string;
  config: {
    heartbeat_interval_seconds: number;
    autosave_interval_seconds: number;
  };
}

export interface TestDetail {
  id: string;
  slug: string;
  title: string;
  description?: string;
  duration_minutes?: number;
  sections?: Array<{
    id: string;
    title: string;
    description?: string;
  }>;
}

export const startAttempt = async (payload: {
  test_id: string;
  mode: string;
  client_timezone: string;
  locale: string;
  device_info: Record<string, unknown>;
}) => {
  const response = await api.post<StartAttemptResponse>('/attempts/start/', payload);
  return response.data;
};

export const getTestDetail = async (slug: string) => {
  const response = await api.get<TestDetail>(`/tests/${slug}/`);
  return response.data;
};

export const submitAttempt = async (attemptId: string, answers: Record<string, unknown>) => {
  const response = await api.post(`/attempts/${attemptId}/submit/`, { answers });
  return response.data;
};

export const getAttemptPaper = async (attemptId: string) => {
  const response = await api.get<ExamPaper>(`/attempts/${attemptId}/paper/`);
  return response.data;
};

export const getAttemptState = async (attemptId: string) => {
  const response = await api.get(`/attempts/${attemptId}/state/`);
  return response.data as { expires_at: string; remaining_seconds: number | null; answers: Array<{ question: string; answer_text?: string; selected_options?: string[]; value_json?: Record<string, unknown>; is_flagged?: boolean }>; section_states?: Array<{ section: string; state: string }> };
};

export const startSection = async (attemptId: string, sectionId: string) => {
  const response = await api.post(`/attempts/${attemptId}/sections/${sectionId}/start/`);
  return response.data;
};

export const completeSection = async (attemptId: string, sectionId: string) => {
  const response = await api.post(`/attempts/${attemptId}/sections/${sectionId}/complete/`);
  return response.data;
};

export const autosaveAnswer = async (attemptId: string, questionId: string, answer: ExamAnswerValue, isFlagged = false) => {
  const response = await api.post(`/attempts/${attemptId}/autosave/`, {
    question_id: questionId,
    ...answer,
    is_flagged: isFlagged,
  });
  return response.data;
};

export const uploadSpeakingAudio = async (attemptId: string, questionId: string, audioFile: File) => {
  const formData = new FormData();
  formData.append('question_id', questionId);
  formData.append('audio', audioFile, audioFile.name);

  const response = await api.post(`/attempts/${attemptId}/speaking/upload/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const saveSpeakingConsent = async () => {
  const response = await api.patch('/auth/me/consent/', { speaking_audio_consent: true });
  return response.data;
};
