import type { Metadata } from 'next';
import AnalyticsPageClient from '@/components/analytics-page-client';

export const metadata: Metadata = {
  title: 'Analytics & Progress',
  description: 'Track your IELTS band trends, weak areas, and score improvements with BandUp analytics.',
};

export default function AnalyticsPage() {
  return <AnalyticsPageClient />;
}
