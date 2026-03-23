import { useState, useEffect, useCallback, useMemo } from 'react'
import type { ReactNode } from 'react'
import { authService } from '@/api/docker/authService'
import { STORAGE_KEYS } from '@/constants/storage'
import { DOM_EVENTS } from '@/constants/app'
import { AuthContext } from './AuthContext'
import type { AuthContextType } from '@/types/auth'

export function AuthProvider({ children }: { readonly children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN))
  const [username, setUsername] = useState<string>(() => localStorage.getItem(STORAGE_KEYS.USERNAME) ?? '')

  // Écoute les 401 émis par le client HTTP : déconnexion sans rechargement de page
  useEffect(() => {
    const handleUnauthorized = () => {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USERNAME)
      setToken(null)
      setUsername('')
    }
    globalThis.addEventListener(DOM_EVENTS.AUTH_UNAUTHORIZED, handleUnauthorized)
    return () => globalThis.removeEventListener(DOM_EVENTS.AUTH_UNAUTHORIZED, handleUnauthorized)
  }, [])

  const login = useCallback(async (user: string, password: string): Promise<void> => {
    const result = await authService.login(user, password)
    if (!result.ok) throw result.error
    setToken(result.data.access_token)
    setUsername(result.data.username)
  }, [])

  const logout = useCallback((): void => {
    authService.logout()
    setToken(null)
    setUsername('')
  }, [])

  const value = useMemo<AuthContextType>(
    () => ({ token, username, isAuthenticated: Boolean(token), login, logout }),
    [token, username, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
