/**
 * @deprecated Importer directement depuis les fichiers spécialisés :
 *   - STORAGE_KEYS  → @/constants/storage
 *   - ROUTES        → @/constants/routes
 *   - API_ROUTES    → @/constants/api
 *   - API_CONFIG    → @/constants/api (API_BASE_URL, API_TIMEOUT)
 */
export { STORAGE_KEYS } from './storage'
export { ROUTES } from './routes'
export { API_BASE_URL, API_TIMEOUT, API_ROUTES } from './api'

/** @deprecated Utiliser API_BASE_URL et API_TIMEOUT séparément. */
export const API_CONFIG = {
  BASE_URL: (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000',
  TIMEOUT: 10_000,
} as const
