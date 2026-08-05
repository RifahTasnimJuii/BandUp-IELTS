import api from '@/lib/api';

export interface TestCatalogItem {
  id: string;
  slug: string;
  title: string;
  module_type: 'academic' | 'general' | 'both';
  description?: string;
  is_published: boolean;
}

export function getTests() {
  return api.get<TestCatalogItem[]>('/tests/tests/').then((response) => response.data);
}

export function getTestDetail(slug: string) {
  return api.get<TestCatalogItem>(`/tests/tests/${slug}/`).then((response) => response.data);
}