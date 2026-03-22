import { apiClient } from './ApiClient'
import type { Alert } from '../types/api'

class AlertsService {
  async getAll(): Promise<Alert[]> {
    return apiClient.get<Alert[]>('/api/alerts')
  }
}

export const alertsService = new AlertsService()
