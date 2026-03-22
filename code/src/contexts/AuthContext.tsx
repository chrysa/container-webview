import { createContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { authService } from '../services/AuthService'

interface AuthState {
  isAuthenticated: boolean
  username: string
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthState>({
  isAuthenticated: false,
  username: '',
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated())
  const [username, setUsername] = useState(authService.getUsername())

  useEffect(() => {
    const handleUnauthorized = () => {
      setIsAuthenticated(false)
      setUsername('')
    }
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const login = async (user: string, password: string) => {
    const tokenResponse = await authService.login(user, password)
    setIsAuthenticated(true)
    setUsername(tokenResponse.username)
  }

  const logout = () => {
    authService.logout()
    setIsAuthenticated(false)
    setUsername('')
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
