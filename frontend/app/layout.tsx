import './globals.css';
import type { Metadata } from 'next';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  metadataBase: new URL('https://bandup.example.com'),
  title: {
    default: 'BandUp | IELTS Mock Tests & AI Feedback',
    template: '%s | BandUp',
  },
  description: 'BandUp helps students practice IELTS with realistic mock tests, AI feedback, and performance analytics to improve their band score.',
  keywords: ['IELTS', 'mock test', 'BandUp', 'AI feedback', 'speaking practice', 'writing practice'],
  openGraph: {
    title: 'BandUp | IELTS Mock Tests & AI Feedback',
    description: 'Prepare smarter with realistic IELTS mock tests and AI-powered progress analysis.',
    url: 'https://bandup.example.com',
    siteName: 'BandUp',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'BandUp IELTS preparation platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BandUp | IELTS Mock Tests & AI Feedback',
    description: 'Practice IELTS with realistic mock tests and guided performance analytics.',
  },
  alternates: {
    canonical: '/',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased dark:bg-slate-950 dark:text-slate-50">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
