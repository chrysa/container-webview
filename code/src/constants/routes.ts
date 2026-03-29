/** Toutes les routes frontend, centralisées. */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/',
  PROJECT_DETAIL: '/projects/:id',
  projectDetail: (id: string) => `/projects/${id}`,
} as const
