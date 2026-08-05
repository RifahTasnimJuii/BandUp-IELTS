import api from '../api';

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
