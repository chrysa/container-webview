import { getToken, getUsername, clearSession, isAuthenticated } from '@/utils/auth';

export function useAuth() {
  return {
    isAuthenticated: isAuthenticated(),
    username: getUsername(),
    token: getToken(),
    logout: () => {
      clearSession();
      window.location.href = '/login';
    },
  };
}
