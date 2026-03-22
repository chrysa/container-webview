import { apiClient } from './ApiClient'
import type { TopologyGraph } from '../types/api'

class TopologyService {
  async getProjectTopology(projectId: string): Promise<TopologyGraph> {
    return apiClient.get<TopologyGraph>(`/api/projects/${projectId}/topology`)
  }
}

export const topologyService = new TopologyService()
