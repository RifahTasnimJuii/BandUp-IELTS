import api from '@/lib/api';
import type { User } from '@/store/useAuthStore';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse<TUser = User> {
  access: string;
  refresh: string;
  user: TUser;
}

export function loginApi(payload: LoginPayload) {
  return api.post<AuthResponse>('/auth/login/', payload).then((response) => response.data);
}

export function registerApi(payload: RegisterPayload) {
  return api.post<AuthResponse>('/auth/register/', payload).then((response) => response.data);
}
