# src/hooks

Hooks React personnalisés partagés entre plusieurs composants ou pages.

## Fichiers

| Hook | Rôle |
|---|---|
| `useAuth.ts` | Accès au contexte d'authentification (`AuthContext`) |

## Conventions

- Un hook par fichier.
- Les hooks ne font pas d'appels API directement — ils utilisent les services de `@/api/docker/` via React Query.
- `useAuth` lance une erreur explicite si utilisé hors d'un `AuthProvider`.
