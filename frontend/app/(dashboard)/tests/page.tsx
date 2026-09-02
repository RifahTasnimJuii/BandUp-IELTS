import type { Metadata } from 'next';
import TestsPageClient from '@/components/tests-page-client';

export const metadata: Metadata = {
  title: 'IELTS Mock Tests',
  description: 'Explore BandUp IELTS mock tests and choose the best practice exam for your preparation goals.',
};

export default function TestsPage() {
  return <TestsPageClient />;
}
