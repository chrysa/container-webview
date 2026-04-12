import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import type { LoginCredentials, AuthToken } from './types';
import { saveSession } from '@/utils/auth';

export function useLogin() {
  return useMutation<AuthToken, Error, LoginCredentials>({
    mutationFn: async (credentials) => {
      const form = new URLSearchParams();
      form.append('username', credentials.username);
      form.append('password', credentials.password);
      const res = await axios.post<AuthToken>('/api/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return res.data;
    },
    onSuccess: (data) => {
      saveSession(data.access_token, data.username);
    },
  });
}
