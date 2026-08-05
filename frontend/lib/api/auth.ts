import api from '@/lib/api';

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

export interface AuthResponse<TUser = any> {
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
