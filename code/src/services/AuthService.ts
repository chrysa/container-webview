import { apiClient } from './ApiClient'
import { STORAGE_KEYS } from '../constants/config'
import type { TokenResponse } from '../types/api'

class AuthService {
  async login(username: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    const token = await apiClient.post<TokenResponse>('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token.access_token)
    localStorage.setItem(STORAGE_KEYS.USERNAME, token.username)
    return token
  }

  logout(): void {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USERNAME)
  }

  isAuthenticated(): boolean {
    return Boolean(localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN))
  }

  getUsername(): string {
    return localStorage.getItem(STORAGE_KEYS.USERNAME) ?? ''
  }
}

export const authService = new AuthService()
