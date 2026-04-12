import { useMutation, useQueryClient } from '@tanstack/react-query';
import { http } from '@/api/http/client';

interface ActionResponse {
  service: string;
  action: string;
  status: string;
}

export function useServiceAction(projectId: string) {
  const qc = useQueryClient();
  return useMutation<ActionResponse, Error, { service: string; action: string }>({
    mutationFn: async ({ service, action }) => {
      const res = await http.post<ActionResponse>(`/projects/${projectId}/services/${service}/${action}`);
      return res.data;
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['topology', projectId] });
      void qc.invalidateQueries({ queryKey: ['metrics', projectId] });
    },
  });
}
