import { useQuery } from '@tanstack/react-query';
import { http } from '@/api/http/client';
import type { TopologyGraph } from './types';

export function useTopology(projectId: string) {
  return useQuery<TopologyGraph>({
    queryKey: ['topology', projectId],
    queryFn: async () => {
      const res = await http.get<TopologyGraph>(`/projects/${projectId}/topology`);
      return res.data;
    },
    enabled: Boolean(projectId),
    refetchInterval: 10_000,
  });
}
