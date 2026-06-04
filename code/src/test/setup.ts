import '@testing-library/jest-dom';

// Node 26 ships an experimental built-in `localStorage` that stays disabled
// unless `--localstorage-file` is provided. Under Vitest it shadows jsdom's Web
// Storage, leaving the global `localStorage`/`sessionStorage` undefined. Install
// a deterministic in-memory shim so storage-backed code (e.g. auth session) is
// testable regardless of the DOM environment.
function createMemoryStorage(): Storage {
  let store = new Map<string, string>();
  return {
    get length(): number {
      return store.size;
    },
    clear(): void {
      store = new Map();
    },
    getItem(key: string): string | null {
      return store.has(key) ? (store.get(key) as string) : null;
    },
    key(index: number): string | null {
      return Array.from(store.keys())[index] ?? null;
    },
    removeItem(key: string): void {
      store.delete(key);
    },
    setItem(key: string, value: string): void {
      store.set(key, String(value));
    },
  } as Storage;
}

for (const name of ['localStorage', 'sessionStorage'] as const) {
  Object.defineProperty(globalThis, name, {
    value: createMemoryStorage(),
    configurable: true,
    writable: true,
  });
}
