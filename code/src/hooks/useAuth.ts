import { useContext } from 'react'
import { AuthContext } from '@/providers/AuthContext'
import type { AuthContextType } from '@/types/auth'

const USE_AUTH_ERROR = 'useAuth doit être utilisé à l\'intérieur d\'un AuthProvider' as const

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error(USE_AUTH_ERROR)
  return ctx
}
