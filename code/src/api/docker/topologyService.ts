import { apiClient } from '@/api/http/client'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { TopologyGraph } from '@/types/api'

export const topologyService = {
  getProjectTopology(projectId: string): Promise<Result<TopologyGraph>> {
    return apiClient.get<TopologyGraph>(API_ROUTES.PROJECT_TOPOLOGY(projectId))
  },
}
