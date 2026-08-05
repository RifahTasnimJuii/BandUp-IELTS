'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { Button } from '@/components/ui/button';

export function AuthenticatedNavbar() {
  const router = useRouter();
  const { user, logout } = useAuthStore((state) => ({
    user: state.user,
    logout: state.logout,
  }));

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const displayName = user?.username || user?.email?.split('@')[0] || 'Student';

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link href="/dashboard" className="text-lg font-semibold text-slate-900">
          BandUp IELTS
        </Link>

        <nav className="flex items-center gap-3 text-sm text-slate-600">
          <span className="hidden sm:inline-block">Hello, {displayName}</span>
          <Link href="/dashboard" className="rounded-full px-3 py-2 hover:bg-slate-100">
            Dashboard
          </Link>
          <Link href="/tests" className="rounded-full px-3 py-2 hover:bg-slate-100">
            Tests
          </Link>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </nav>
      </div>
    </header>
  );
}
