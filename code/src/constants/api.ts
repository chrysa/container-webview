/** URL de base de l'API (obligatoire via variable d'environnement). */
export const API_BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

export const API_TIMEOUT = 10_000

const V1 = '/api/v1' as const

/** Routes de l'API backend (versionnées `/api/v1/`). */
export const API_ROUTES = {
  HEALTH: '/health',
  AUTH_LOGIN: `${V1}/auth/login`,
  PROJECTS: `${V1}/projects`,
  PROJECT_DETAIL: (id: string) => `${V1}/projects/${id}`,
  PROJECT_METRICS: (id: string) => `${V1}/projects/${id}/metrics`,
  PROJECT_TOPOLOGY: (id: string) => `${V1}/projects/${id}/topology`,
  PROJECT_ALERTS: (id: string) => `${V1}/alerts/project/${id}`,
  SERVICE_ACTION: (projectId: string, service: string, action: string) =>
    `${V1}/projects/${projectId}/services/${service}/${action}`,
  ALERTS: `${V1}/alerts`,
  DOCS: '/api/docs',
  REDOC: '/api/redoc',
} as const
