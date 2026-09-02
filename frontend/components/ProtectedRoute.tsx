'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/lib/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const setUser = useAuthStore((state) => state.setUser);
  const logout = useAuthStore((state) => state.logout);
  const [mounted, setMounted] = useState(false);
  const [validating, setValidating] = useState(true);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (!isAuthenticated || !accessToken) {
      setValidating(false);
      return;
    }
    api.get('/auth/me/').then((response) => setUser(response.data)).catch(() => {
      logout();
      router.replace('/login');
    }).finally(() => setValidating(false));
  }, [accessToken, isAuthenticated, logout, mounted, router, setUser]);

  useEffect(() => {
    if (mounted && !validating && !isAuthenticated) {
      router.replace('/login');
    }
  }, [mounted, isAuthenticated, router, validating]);

  if (!mounted || validating || !isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
