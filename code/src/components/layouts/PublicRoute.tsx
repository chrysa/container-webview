import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { ROUTES } from '@/constants/routes'

/** Redirige vers / si l'utilisateur est déjà authentifié (ex. page Login). */
export function PublicRoute({ children }: { readonly children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to={ROUTES.HOME} replace />
  return <>{children}</>
}
