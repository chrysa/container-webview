import { apiClient } from '@/api/http/client'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { ActionResponse } from '@/types/api'

export const lifecycleService = {
  perform(projectId: string, serviceName: string, action: string): Promise<Result<ActionResponse>> {
    return apiClient.post<ActionResponse>(API_ROUTES.SERVICE_ACTION(projectId, serviceName, action))
  },
}
