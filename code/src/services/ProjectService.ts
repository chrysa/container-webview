import { apiClient } from './ApiClient'
import type { ProjectModel } from '../types/api'

class ProjectService {
  async listAll(): Promise<ProjectModel[]> {
    return apiClient.get<ProjectModel[]>('/api/projects')
  }

  async getById(projectId: string): Promise<ProjectModel> {
    return apiClient.get<ProjectModel>(`/api/projects/${projectId}`)
  }
}

export const projectService = new ProjectService()
