type LoadingListener = (isLoading: boolean) => void

class LoadingStore {
  readonly #listeners: Set<LoadingListener> = new Set()
  #activeRequests = 0

  subscribe(listener: LoadingListener): () => void {
    this.#listeners.add(listener)
    return () => this.#listeners.delete(listener)
  }

  #notify(): void {
    const isLoading = this.#activeRequests > 0
    this.#listeners.forEach((listener) => listener(isLoading))
  }

  start(): void {
    this.#activeRequests++
    this.#notify()
  }

  complete(): void {
    this.#activeRequests = Math.max(0, this.#activeRequests - 1)
    this.#notify()
  }

  reset(): void {
    this.#activeRequests = 0
    this.#notify()
  }
}

export const loadingStore = new LoadingStore()
