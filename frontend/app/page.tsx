'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';

export default function HomeRedirectPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    } else {
      router.replace('/login');
    }
    setIsReady(true);
  }, [isAuthenticated, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="rounded-3xl border border-slate-200 bg-white px-8 py-10 text-center shadow-sm shadow-slate-900/5">
        <p className="text-sm text-slate-500">Redirecting...</p>
        <div className="mt-6 inline-flex h-12 w-12 items-center justify-center rounded-full border border-slate-200">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-slate-300 border-t-slate-900" />
        </div>
        <p className="mt-4 text-sm text-slate-600">Preparing your experience.</p>
      </div>
    </div>
  );
}
