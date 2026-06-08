import { useQuery } from '@tanstack/react-query';
import { http } from '@/api/http/client';
import type { ConfigStatus } from './types';

/**
 * Fetch public runtime configuration flags (demo mode, LDAP availability).
 * Endpoint is unauthenticated so the demo banner and login page can read it
 * before the user signs in.
 */
export function useConfigStatus() {
  return useQuery<ConfigStatus>({
    queryKey: ['config-status'],
    queryFn: async () => {
      const res = await http.get<ConfigStatus>('/config/status');
      return res.data;
    },
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
}
