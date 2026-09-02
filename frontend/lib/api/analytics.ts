import api from '@/lib/api';

export interface ScoreTrendPoint {
  label?: string;
  date?: string;
  band?: number | string | null;
  score?: number | string | null;
  name?: string;
}

export interface WeakAreaItem {
  label: string;
  score: number;
  value?: number;
}

export interface DashboardAnalytics {
  tests_taken: number;
  overall_band: number | string | null;
  module_bands: Record<string, number | string | null>;
  weak_area: WeakAreaItem | null;
  recent_attempts: Array<{ id: string; test_title: string; date: string; overall_band: number | string | null }>;
  readiness_score: number;
  overall_average_band?: number | string | null;
  section_averages?: Record<string, number | string | null>;
  weak_areas?: WeakAreaItem[];
  recent_scores?: ScoreTrendPoint[];
  skill_summary?: Record<string, Record<string, number | string>>;
  writing_criteria?: Record<string, number | string>;
  speaking_criteria?: Record<string, number | string>;
}

export const getAnalyticsDashboard = async () => {
  const response = await api.get<DashboardAnalytics>('/analytics/dashboard/');
  return response.data;
};

export const getScoreTrend = async () => {
  const response = await api.get<ScoreTrendPoint[]>('/analytics/score-trend/');
  return response.data;
};
