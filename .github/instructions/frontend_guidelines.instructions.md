______________________________________________________________________

## applyTo: "code/\*\*/\*"

# Frontend Guidelines — React 19 + Vite + TypeScript

## Principes fondamentaux

### 1. Typage strict — zéro `any`

- Tous les types dans `src/domain/*/types.ts`
- Interfaces en `PascalCase`, exportées nommément
- Pas de `any`, pas de `// @ts-ignore` sans commentaire explicatif
- `tsconfig.app.json` : mode strict activé, ES2022, bundler moduleResolution

### 2. Structure des fichiers

```
src/
├── api/http/
│   ├── client.ts          # axios.create() + baseURL = VITE_API_URL + "/api"
│   └── interceptors.ts    # inject Bearer token, redirect /login sur 401
├── domain/<domaine>/
│   ├── types.ts           # interfaces TypeScript du domaine
│   └── queries.ts         # hooks TanStack Query (useQuery, useMutation)
├── features/<domaine>/
│   ├── ComponentName.tsx
│   └── ComponentName.module.scss
├── components/
│   ├── layouts/           # Layout, Header, Sidebar
│   └── loaders/           # GlobalLoader
├── pages/
│   └── PageName.tsx       # lazy-loaded, composition seulement
├── hooks/
│   ├── useAuth.ts         # état d'authentification JWT
│   └── useTheme.ts        # dark/light, persiste en localStorage
├── styles/
│   ├── _reset.scss
│   ├── _theme.scss        # variables CSS custom properties
│   ├── _variables.scss
│   ├── _mixins.scss
│   ├── _globals.scss
│   └── index.scss
└── utils/
    └── auth.ts            # getToken, saveSession, clearSession (localStorage)
```

### 3. Pages — uniquement routing et composition

```tsx
// ✅ Correct
const ProjectsPage = () => (
  <Layout>
    <ProjectsList />
  </Layout>
);

// ❌ Interdit — pas de logique réseau dans les pages
const ProjectsPage = () => {
  const { data } = axios.get("/api/projects"); // NON
};
```

### 4. Logique réseau — uniquement dans `domain/*/queries.ts`

```ts
// src/domain/projects/queries.ts
export const useProjects = () =>
  useQuery({ queryKey: ["projects"], queryFn: () => http.get<Project[]>("/projects") });
```

### 5. Navigation — React Router uniquement

- Utiliser `<Link>`, `<Navigate>`, `useNavigate()`
- **Jamais** `window.location`, `location.href`, `location.reload()`

### 6. SCSS Modules

- Un fichier `.module.scss` par composant, colocalié
- Noms de classes en `camelCase` dans le module
- Variables globales depuis `src/styles/_variables.scss` via `@use`

```scss
// ✅ Correct
@use "@/styles/variables" as *;
.container { padding: $spacing-md; }

// ❌ Interdit — pas de styles inline dans le JSX
<div style={{ padding: "16px" }} />
```

### 7. Gestion des erreurs

- Intercepteur Axios gère les 401 → redirect `/login` + `clearSession()`
- Les erreurs de query sont gérées via `error` de TanStack Query
- Pas de `try/catch` dans les composants

### 8. Authentification

- Token JWT stocké via `utils/auth.ts` → `localStorage`
- `RequireAuth` guard dans `App.tsx` protège toutes les routes privées
- WebSocket logs : token passé via query param `?token=` (seule exception)

## Composants disponibles

| Composant         | Chemin                                | Usage                                        |
| ----------------- | ------------------------------------- | -------------------------------------------- |
| `Layout`          | `components/layouts/Layout.tsx`       | Wrapper général (Header + Sidebar + contenu) |
| `Header`          | `components/layouts/Header.tsx`       | Barre du haut, toggle thème                  |
| `Sidebar`         | `components/layouts/Sidebar.tsx`      | Nav latérale, collapsible                    |
| `GlobalLoader`    | `components/loaders/GlobalLoader.tsx` | Spinner pendant chargement initial           |
| `TopologyGraph`   | `features/topology/TopologyGraph.tsx` | ReactFlow — visualisation des services       |
| `ServicesTable`   | `features/services/ServicesTable.tsx` | Table services + actions lifecycle           |
| `LogsPanel`       | `features/logs/LogsPanel.tsx`         | Stream WebSocket natif                       |
| `MetricsCharts`   | `features/metrics/MetricsCharts.tsx`  | CPU/RAM/net/IO via Recharts                  |
| `AlertsDashboard` | `features/alerts/AlertsDashboard.tsx` | Alertes conteneurs                           |
| `LoginForm`       | `features/auth/LoginForm.tsx`         | Formulaire de connexion                      |

## Domaines disponibles

| Domaine     | Types                                           | Queries                                       |
| ----------- | ----------------------------------------------- | --------------------------------------------- |
| `auth`      | `LoginRequest`, `TokenResponse`                 | `useLogin`                                    |
| `projects`  | `Project`, `ServiceInfo`                        | `useProjects`, `useProject`                   |
| `topology`  | `TopologyGraph`, `TopologyNode`, `TopologyEdge` | `useTopology`                                 |
| `metrics`   | `ServiceMetrics`, `MetricPoint`                 | `useMetrics`                                  |
| `alerts`    | `Alert`                                         | `useAlerts`                                   |
| `lifecycle` | —                                               | `useServiceAction` (start/stop/restart/pause) |

## API Constants — No Hardcoded URLs in Services (MANDATORY)

**NEVER hardcode API path strings inside service methods or components.** All API endpoint paths must be declared in `src/constants/config.ts` and referenced by name.

```typescript
// ✅ CORRECT — paths declared as constants
export const API_ROUTES = {
  AUTH_LOGIN: '/api/auth/login',
  PROJECTS: '/api/projects',
  PROJECT_DETAIL: (id: string) => `/api/projects/${id}`,
  PROJECT_METRICS: (id: string) => `/api/projects/${id}/metrics`,
  PROJECT_TOPOLOGY: (id: string) => `/api/projects/${id}/topology`,
  SERVICE_ACTION: (projectId: string, service: string, action: string) =>
    `/api/projects/${projectId}/services/${service}/${action}`,
  ALERTS: '/api/alerts',
} as const

// ✅ Service uses constant
class ProjectService {
  async getById(id: string): Promise<ProjectModel> {
    return apiClient.get<ProjectModel>(API_ROUTES.PROJECT_DETAIL(id))
  }
}

// ❌ FORBIDDEN — hardcoded string in service
class ProjectService {
  async getById(id: string): Promise<ProjectModel> {
    return apiClient.get<ProjectModel>(`/api/projects/${id}`)  // ← FORBIDDEN
  }
}
```

---

## HATEOAS — Discoverable Links from API (MANDATORY)

When the backend returns HATEOAS `_links`, **always use the URLs provided by the API** rather than constructing them client-side. This decouples the frontend from API route changes.

### Backend response pattern

```json
{
  "id": "my-project",
  "name": "My Project",
  "_links": {
    "self":     { "href": "/api/projects/my-project" },
    "metrics":  { "href": "/api/projects/my-project/metrics" },
    "topology": { "href": "/api/projects/my-project/topology" },
    "alerts":   { "href": "/api/projects/my-project/alerts" }
  }
}
```

### Frontend usage pattern

```typescript
// src/types/api.ts — link envelope
export interface HateoasLink {
  href: string
}

export interface WithLinks {
  _links?: Record<string, HateoasLink>
}

export interface ProjectModel extends WithLinks {
  id: string
  name: string
  // ...
}

// ✅ CORRECT — use href from _links when available, fall back to constant
class MetricsService {
  async getMetrics(project: ProjectModel): Promise<ServiceMetrics[]> {
    const url = project._links?.metrics?.href ?? API_ROUTES.PROJECT_METRICS(project.id)
    return apiClient.get<ServiceMetrics[]>(url)
  }
}

// ❌ FORBIDDEN — ignore _links and construct URL manually
class MetricsService {
  async getMetrics(project: ProjectModel): Promise<ServiceMetrics[]> {
    return apiClient.get<ServiceMetrics[]>(`/api/projects/${project.id}/metrics`)
  }
}
```

---

## TypeScript: Types and Interfaces

## Loading States (NON-NEGOTIABLE)

- Every waiting state > **200 ms** must be materialised without layout shift (CLS = 0).
- Hierarchy: **skeleton → progress bar → spinner**. Never a full-screen spinner on a page with known structure.
- Use `React.lazy()` + `<Suspense fallback={<Skeleton />}>` for all routes, charts, modals, editors.
- Skeletons: `<Skeleton />` from shadcn/ui, shaped like the content. Add `aria-busy="true"`, respect `prefers-reduced-motion`.
- Show skeleton on `isPending`. **Never hide existing content** during background refetch (`isFetching`).
- Progress bar: determinate (`<Progress value={n} />`) when a real % exists. Top-of-page indeterminate for route transitions only.
- Images: always `loading="lazy" decoding="async"` + explicit `width`/`height` or `aspect-ratio` to prevent CLS.
