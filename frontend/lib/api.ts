import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    
    let accessToken: string | null = null;
    try {
      const raw = localStorage.getItem('bandup-auth');
      if (raw) {
        const parsed = JSON.parse(raw);
        accessToken = parsed?.state?.accessToken ?? null;
      }
    } catch {
      accessToken = null;
    }

    console.log('🔍', config.method?.toUpperCase(), config.url, '| token:', !!accessToken);

    if (accessToken) {
      config.headers.set('Authorization', `Bearer ${accessToken}`);
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
