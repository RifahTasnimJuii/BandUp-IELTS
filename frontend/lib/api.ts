import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';
import { getAuthState } from '@/store/useAuthStore';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const authState = getAuthState();

  if (authState?.accessToken) {
    const headers = config.headers as Record<string, string> | undefined;
    config.headers = {
      ...(headers ?? {}),
      Authorization: `Bearer ${authState.accessToken}`,
    } as any;
  }

  return config;
},
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Placeholder: refresh token logic should go here.
    }
    return Promise.reject(error);
  }
);

export default api;
