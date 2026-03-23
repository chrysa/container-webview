# src/pages

Composants de page — point d'entrée de chaque route React Router. Chargés en **lazy loading** via `React.lazy()`.

## Fichiers

| Page | Route | Accès |
|---|---|---|
| `LoginPage.tsx` | `/login` | Public (redirige si déjà connecté) |
| `DashboardPage.tsx` | `/` | Protégé |
| `ProjectDetailPage.tsx` | `/projects/:id` | Protégé |

## Conventions

- Les pages orchestrent les features et composants — elles ne contiennent pas de logique d'affichage complexe.
- Les appels API se font via React Query (`useQuery`) avec les services de `@/api/docker/`.
- Résultats gérés avec `Result<T>` : vérifier `.ok` avant d'accéder à `.data`.
