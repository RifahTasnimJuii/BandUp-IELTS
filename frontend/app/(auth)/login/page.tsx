'use client';

import axios from 'axios';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { loginApi, type LoginPayload } from '@/lib/api/auth';
import { useAuthStore } from '@/store/useAuthStore';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, router]);

  const onSubmit = async (values: LoginFormValues) => {
    setErrorMessage('');
    setIsLoading(true);

    try {
      const response = await loginApi(values as LoginPayload);
      login(response.user, response.access, response.refresh);
      router.push('/dashboard');
    } catch (error: unknown) {
      let message = 'Unable to login. Please try again.';
      if (axios.isAxiosError(error)) {
        if (error.response) {
          const responseData = error.response.data as Record<string, unknown> | undefined;
          message =
            (typeof responseData?.detail === 'string' ? responseData.detail : '') ||
            (typeof responseData?.message === 'string' ? responseData.message : '') ||
            `Request failed with status ${error.response.status}`;
        } else {
          message = error.message || 'Network Error';
        }
      }
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-900/5">
        <div className="space-y-3 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Welcome back</p>
          <h1 className="text-3xl font-semibold text-slate-900">Sign in to BandUp IELTS</h1>
          <p className="text-sm text-slate-600">Access your dashboard, continue tests, and start new mock exams.</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" {...register('email')} />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="Enter your password" {...register('password')} />
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
            </div>
          </div>

          {errorMessage && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </Button>

          <div className="text-center text-sm text-slate-600">
            Don&apos;t have an account?{' '}
            <a href="/register" className="font-medium text-slate-900 hover:text-slate-700">
              Register
            </a>
          </div>
        </form>
      </div>
    </main>
  );
}
