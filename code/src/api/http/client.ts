import { API_BASE_URL } from '@/constants/api'
import { DOM_EVENTS, HTTP_HEADERS, HTTP_HEADER_VALUES, ERROR_MESSAGES } from '@/constants/app'
import { STORAGE_KEYS } from '@/constants/storage'
import { loadingStore } from '@/stores/loadingStore'
import type { Result } from '@/utils/result'

function serializeBody(body: unknown): string {
  if (body instanceof URLSearchParams) return body.toString()
  return JSON.stringify(body)
}

class ApiClient {
  readonly #baseUrl: string

  constructor(baseUrl: string) {
    this.#baseUrl = baseUrl
  }

  #getHeaders(contentType?: string): Record<string, string> {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
    const headers: Record<string, string> = {
      [HTTP_HEADERS.CONTENT_TYPE]: contentType ?? HTTP_HEADER_VALUES.JSON,
    }
    if (token) {
      headers[HTTP_HEADERS.AUTHORIZATION] = `${HTTP_HEADER_VALUES.BEARER_PREFIX} ${token}`
    }
    return headers
  }

  async #request<T>(method: string, path: string, body?: unknown, contentType?: string): Promise<Result<T>> {
    // Supporte les URLs absolues HATEOAS retournées par le backend
    const url = path.startsWith('http') ? path : `${this.#baseUrl}${path}`
    loadingStore.start()
    return fetch(url, {
      method,
      headers: this.#getHeaders(contentType),
      body: body !== undefined ? serializeBody(body) : undefined,
    })
      .then(async (res): Promise<Result<T>> => {
        loadingStore.complete()
        if (res.status === 401) {
          globalThis.dispatchEvent(new Event(DOM_EVENTS.AUTH_UNAUTHORIZED))
          return { ok: false, error: new Error(ERROR_MESSAGES.UNAUTHORIZED) }
        }
        if (!res.ok) {
          const data = (await res.json().catch(() => ({}))) as Record<string, unknown>
          const message = (data['detail'] as string | undefined) ?? ERROR_MESSAGES.HTTP_STATUS(res.status)
          return { ok: false, error: new Error(message) }
        }
        if (res.status === 204) return { ok: true, data: undefined as T }
        const data = (await res.json()) as T
        return { ok: true, data }
      })
      .catch((err: unknown): Result<T> => {
        loadingStore.complete()
        return {
          ok: false,
          error: err instanceof Error ? err : new Error(ERROR_MESSAGES.NETWORK_ERROR),
        }
      })
  }

  get<T>(path: string): Promise<Result<T>> {
    return this.#request<T>('GET', path)
  }

  post<T>(path: string, body?: unknown): Promise<Result<T>> {
    return this.#request<T>('POST', path, body)
  }

  postForm<T>(path: string, form: URLSearchParams): Promise<Result<T>> {
    return this.#request<T>('POST', path, form, HTTP_HEADER_VALUES.FORM_URLENCODED)
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
