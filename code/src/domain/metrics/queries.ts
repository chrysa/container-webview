import { useQuery } from '@tanstack/react-query';
import { http } from '@/api/http/client';
import type { ServiceMetrics } from './types';

export function useMetrics(projectId: string) {
  return useQuery<ServiceMetrics[]>({
    queryKey: ['metrics', projectId],
    queryFn: async () => {
      const res = await http.get<ServiceMetrics[]>(`/projects/${projectId}/metrics`);
      return res.data;
    },
    enabled: Boolean(projectId),
    refetchInterval: 5_000,
  });
}
