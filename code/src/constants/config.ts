export const STORAGE_KEYS = {
  AUTH_TOKEN: 'docker_overview_auth_token',
  USERNAME: 'docker_overview_username',
} as const

export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
} as const

export const API_CONFIG = {
  BASE_URL: (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000',
  TIMEOUT: 10_000,
} as const
