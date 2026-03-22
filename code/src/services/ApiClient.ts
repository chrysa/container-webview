import axios from 'axios'
import type { AxiosInstance } from 'axios'
import type { AxiosRequestConfig } from 'axios'
import { API_CONFIG, STORAGE_KEYS } from '../constants/config'

class ApiClient {
  readonly #client: AxiosInstance

  constructor() {
    this.#client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
    })

    this.#client.interceptors.request.use((config) => {
      const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.#client.interceptors.response.use(
      (response) => response,
      (error: unknown) => {
        const status = (error as { response?: { status?: number } }).response?.status
        if (status === 401) {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
        return Promise.reject(error)
      },
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.#client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.#client.post<T>(url, data, config)
    return response.data
  }
}

export const apiClient = new ApiClient()
