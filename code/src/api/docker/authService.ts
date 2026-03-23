import { apiClient } from '@/api/http/client'
import { STORAGE_KEYS } from '@/constants/storage'
import { API_ROUTES } from '@/constants/api'
import type { Result } from '@/utils/result'
import type { TokenResponse } from '@/types/api'

export const authService = {
  async login(username: string, password: string): Promise<Result<TokenResponse>> {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    const result = await apiClient.postForm<TokenResponse>(API_ROUTES.AUTH_LOGIN, form)
    if (result.ok) {
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, result.data.access_token)
      localStorage.setItem(STORAGE_KEYS.USERNAME, result.data.username)
    }
    return result
  },

  logout(): void {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USERNAME)
  },

  getToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
  },

  isAuthenticated(): boolean {
    return Boolean(localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN))
  },

  getUsername(): string {
    return localStorage.getItem(STORAGE_KEYS.USERNAME) ?? ''
  },
}
