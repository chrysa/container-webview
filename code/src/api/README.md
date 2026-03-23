# src/api

Couche d'accès aux données. Contient le client HTTP et les services d'appel API organisés par domaine.

## Structure

```
api/
├── http/
│   └── client.ts        # Client HTTP fetch natif avec Result<T>, gestion 401, LoadingStore
└── docker/
    ├── authService.ts   # Login / logout / statut d'authentification
    ├── projectService.ts
    ├── metricsService.ts
    ├── alertsService.ts
    ├── lifecycleService.ts
    └── topologyService.ts
```

## Conventions

- Toutes les fonctions retournent `Promise<Result<T>>` — **pas de throw**, pas d'Axios.
- Les URLs absolues HATEOAS retournées par le backend sont supportées nativement (`path.startsWith('http')`).
- Les tokens JWT sont lus depuis `localStorage` via `STORAGE_KEYS`.
- Les erreurs 401 émettent `DOM_EVENTS.AUTH_UNAUTHORIZED` sur `window` → `AuthProvider` déconnecte sans rechargement.
