import { apiClient } from './ApiClient'
import type { ServiceMetrics } from '../types/api'

class MetricsService {
  async getProjectMetrics(projectId: string): Promise<ServiceMetrics[]> {
    return apiClient.get<ServiceMetrics[]>(`/api/projects/${projectId}/metrics`)
  }
}

export const metricsService = new MetricsService()
