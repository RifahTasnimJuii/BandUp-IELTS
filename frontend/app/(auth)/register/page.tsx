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
import { registerApi, type RegisterPayload } from '@/lib/api/auth';
import { useAuthStore } from '@/store/useAuthStore';

const registerSchema = z.object({
  username: z.string().min(2, 'Enter a username'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  password_confirm: z.string().min(8, 'Confirm password must be at least 8 characters'),
}).refine((data) => data.password === data.password_confirm, {
  message: 'Passwords must match',
  path: ['password_confirm'],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, router]);

  const onSubmit = async (values: RegisterFormValues) => {
    setErrorMessage('');
    setIsLoading(true);

    try {
      const response = await registerApi(values as RegisterPayload);
      login(response.user, response.access, response.refresh);
      router.push('/dashboard');
    } catch (error: unknown) {
      let message = 'Unable to register. Please try again.';
      if (axios.isAxiosError(error)) {
        if (error.response) {
          message =
            (error.response.data as Record<string, any>)?.detail ||
            error.response.data?.message ||
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
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Create your account</p>
          <h1 className="text-3xl font-semibold text-slate-900">Register for BandUp IELTS</h1>
          <p className="text-sm text-slate-600">Start taking mock tests and track your IELTS progress.</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="Your display name" {...register('username')} />
              {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>}
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" {...register('email')} />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="Create a password" {...register('password')} />
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
            </div>
            <div>
              <Label htmlFor="password_confirm">Confirm Password</Label>
              <Input id="password_confirm" type="password" placeholder="Confirm your password" {...register('password_confirm')} />
              {errors.password_confirm && <p className="mt-1 text-sm text-red-600">{errors.password_confirm.message}</p>}
            </div>
          </div>

          {errorMessage && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Register'}
          </Button>

          <div className="text-center text-sm text-slate-600">
            Already registered?{' '}
            <a href="/login" className="font-medium text-slate-900 hover:text-slate-700">
              Sign in
            </a>
          </div>
        </form>
      </div>
    </main>
  );
}
