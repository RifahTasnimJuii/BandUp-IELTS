import api from '@/lib/api';

export type CriteriaScoreMap = Record<string, number | string>;

export interface AttemptObjectiveReviewItem {
  id?: string | number;
  question_number?: number | string;
  question_label?: string;
  user_answer?: string | null;
  correct_answer?: string | null;
  is_correct?: boolean;
}

export interface AttemptResult {
  attempt_id?: string;
  overall_band?: number | string | null;
  is_review_allowed?: boolean;
  section_scores?: Record<string, number | string | null>;
  objective_review?: AttemptObjectiveReviewItem[];
  writing_feedback?: {
    status?: string;
    band_score?: number | string | null;
    criteria_scores?: CriteriaScoreMap;
    strengths?: string[] | string;
    weaknesses?: string[] | string;
    improvement_suggestions?: string[] | string;
    feedback?: string;
  } | null;
  speaking_feedback?: {
    status?: string;
    band_score?: number | string | null;
    criteria_scores?: CriteriaScoreMap;
    strengths?: string[] | string;
    weaknesses?: string[] | string;
    improvement_suggestions?: string[] | string;
    feedback?: string;
  } | null;
  status?: string;
}

export const getAttemptResults = async (attemptId: string) => {
  const response = await api.get<AttemptResult>(`/results/${attemptId}/`);
  return response.data;
};
