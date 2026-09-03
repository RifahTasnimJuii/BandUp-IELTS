import './globals.css';
import type { Metadata } from 'next';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  metadataBase: new URL('https://bandup.example.com'),
  title: {
    default: 'BandUp IELTS | Mock Tests & AI Feedback',
    template: '%s | BandUp IELTS',
  },
  description: 'BandUp IELTS helps students practise with realistic mock tests, feedback, and performance analytics.',
  keywords: ['IELTS', 'mock test', 'BandUp IELTS', 'feedback', 'speaking practice', 'writing practice'],
  openGraph: {
    title: 'BandUp IELTS | Mock Tests & AI Feedback',
    description: 'Prepare smarter with realistic IELTS mock tests and AI-powered progress analysis.',
    url: 'https://bandup.example.com',
    siteName: 'BandUp IELTS',
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
    title: 'BandUp IELTS | Mock Tests & AI Feedback',
    description: 'Practice IELTS with realistic mock tests and guided performance analytics.',
  },
  alternates: {
    canonical: '/',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
