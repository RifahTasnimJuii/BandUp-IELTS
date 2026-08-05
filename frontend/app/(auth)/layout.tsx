import './auth.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'BandUp IELTS | Auth',
  description: 'Sign in or register to access BandUp IELTS',
};

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return <section className="min-h-screen bg-slate-50">{children}</section>;
}
