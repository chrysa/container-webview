import { apiClient } from '@/api/http/client'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { ServiceMetrics } from '@/types/api'

export const metricsService = {
  getProjectMetrics(projectId: string): Promise<Result<ServiceMetrics[]>> {
    return apiClient.get<ServiceMetrics[]>(API_ROUTES.PROJECT_METRICS(projectId))
  },
}
