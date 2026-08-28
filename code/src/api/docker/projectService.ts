import { apiClient } from '@/api/http/client'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { ProjectModel } from '@/types/api'

export const projectService = {
  listAll(): Promise<Result<ProjectModel[]>> {
    return apiClient.get<ProjectModel[]>(API_ROUTES.PROJECTS)
  },

  getById(projectId: string): Promise<Result<ProjectModel>> {
    return apiClient.get<ProjectModel>(API_ROUTES.PROJECT_DETAIL(projectId))
  },
}
