import { useQuery } from '@tanstack/react-query';
import { http } from '@/api/http/client';
import type { Project } from './types';

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const res = await http.get<Project[]>('/projects');
      return res.data;
    },
    refetchInterval: 30_000,
  });
}

export function useProject(id: string) {
  return useQuery<Project>({
    queryKey: ['projects', id],
    queryFn: async () => {
      const res = await http.get<Project>(`/projects/${id}`);
      return res.data;
    },
    enabled: Boolean(id),
    refetchInterval: 15_000,
  });
}
