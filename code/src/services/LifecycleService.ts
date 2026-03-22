import { apiClient } from './ApiClient'
import type { ActionResponse } from '../types/api'

class LifecycleService {
  async perform(projectId: string, serviceName: string, action: string): Promise<ActionResponse> {
    return apiClient.post<ActionResponse>(
      `/api/projects/${projectId}/services/${serviceName}/${action}`,
    )
  }
}

export const lifecycleService = new LifecycleService()
