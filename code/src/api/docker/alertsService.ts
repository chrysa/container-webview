import { apiClient } from '@/api/http/client'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { Alert } from '@/types/api'

export const alertsService = {
  getAll(): Promise<Result<Alert[]>> {
    return apiClient.get<Alert[]>(API_ROUTES.ALERTS)
  },

  getForProject(projectId: string): Promise<Result<Alert[]>> {
    return apiClient.get<Alert[]>(API_ROUTES.PROJECT_ALERTS(projectId))
  },
}
