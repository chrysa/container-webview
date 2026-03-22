# Docker Overview WebUI — Frontend Guidelines

---
description: "Guidelines for React TypeScript frontend development in Docker Overview WebUI. STRICT: All requirements are MANDATORY. Atomic components <150 lines, zero page reloads, OOP pattern for services, STORAGE_KEYS for localStorage, React Query for server state."
applyTo: "code/src/**/*.{ts,tsx,css}"
---

---

## 🚨 FUNDAMENTAL REQUIREMENTS (READ FIRST)

**These principles are NON-NEGOTIABLE and apply to ALL code:**

### 1. ⚛️ ATOMIC COMPONENTS (MANDATORY)
- **Every component MUST be < 150 lines** (strict limit)
- **Single Responsibility Principle** — One clear purpose per component
- **Composable Architecture** — Build complex features from small, reusable atoms
- **Clear Scopes** — Presentation / Logic / Container separation

**If a component exceeds 150 lines → REFACTOR into atomic components immediately.**

### 2. 🎯 OBJECT-ORIENTED PATTERN (MANDATORY)
- **NO global functions** — All code must be in classes/objects
- **NO global variables** — Use `const` objects with `as const`
- **Services MUST use ES6 classes** with `#private` fields/methods
- **Utilities MUST be static classes** or `const` objects
- **Configuration MUST be `const` objects** (nested structure allowed)

**If you write a standalone function → WRONG! Wrap it in a class or const object.**

### 3. 🚫 ZERO PAGE RELOADS (MANDATORY)
- **NEVER** use `window.location`, `location.href`, or `location.reload()`
- **NEVER** allow forms to submit without `event.preventDefault()`
- **NEVER** set `isLoading` state during user actions (only for initial auth check)
- **ALWAYS** use React Router (`<Link>`, `<Navigate>`, `useNavigate()`) for ALL navigation
- **ALWAYS** use event-driven architecture for auth errors (emit `auth:unauthorized` event)

---

## 🚨 CRITICAL: Command Execution Policy

**ALL Node.js/npm commands MUST be executed INSIDE the Docker service.**

### ✅ ALLOWED — Use Makefile (RECOMMENDED)

```bash
make dev              # Start development server
make lint             # Run ESLint
make format           # Auto-fix linting issues
make type-check       # TypeScript validation
make test             # Run tests
make test-coverage    # Generate coverage report
make ci               # Run all checks (lint + type-check + test)
make install          # Install dependencies
```

### ✅ ALLOWED — Docker Exec (if container is already running)

```bash
docker exec docker-webui-frontend npm run lint
docker exec docker-webui-frontend npm run test
docker exec -it docker-webui-frontend bash
```

### ❌ FORBIDDEN — Never run on host machine

```bash
npm run dev           # ❌ Wrong — use: make dev
npm run test          # ❌ Wrong — use: make test
npm install           # ❌ Wrong — use: make install
npx some-tool         # ❌ Wrong — use: docker exec docker-webui-frontend npx some-tool
cd code && npm start  # ❌ Wrong — always work from project root with make
```

**Container Name:** `docker-webui-frontend` (see `docker-compose.yml`)

---

## Architecture Overview

- **Technology:** React 18 + Vite + TypeScript
- **Routing:** React Router 6 — client-side only (`<Link>`, `<Navigate>`, `useNavigate`)
- **Server State:** React Query (`@tanstack/react-query`) — for ALL API calls
- **UI State:** React Context API
- **Auth:** `useAuth` hook + `TokenManager` class using `STORAGE_KEYS`
- **Styling:** Bootstrap 5 + CSS Modules
- **Tests:** Vitest + React Testing Library

---

## Storage Keys (MANDATORY)

**CRITICAL:** Always use `STORAGE_KEYS` constants from `@/constants/config`. Never use hardcoded strings.

```typescript
import { STORAGE_KEYS } from '@/constants/config';

// ✅ Correct
localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

// ❌ Wrong — hardcoded strings are FORBIDDEN
localStorage.setItem('auth_token', token);
localStorage.setItem('authToken', token);
localStorage.getItem('token');
```

---

## Service Layer (ES6 Classes with Private Fields)

All API services MUST use ES6 classes with `#private` methods/fields.

```typescript
// ✅ CORRECT — ES6 class with private methods
class ProjectService {
  readonly #apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.#apiClient = apiClient;
  }

  async listProjects(): Promise<Project[]> {
    const response = await this.#apiClient.get<Project[]>('/projects');
    return response.data;
  }

  async startProject(projectName: string): Promise<void> {
    await this.#apiClient.post(`/projects/${projectName}/start`);
  }
}

// ❌ WRONG — standalone exported functions
export async function listProjects() { /* ... */ }
export const projectService = { list: () => { /* ... */ } };
```

---

## Component Architecture

### Component Scopes

**1. Presentational Components (30–60 lines)**
- Pure UI rendering, no business logic
- Input: Props only (data, callbacks, config)
- Output: JSX rendering

```typescript
// ✅ Clear presentational scope
interface ContainerStatusBadgeProps {
  status: string;
  name: string;
}

export function ContainerStatusBadge({ status, name }: ContainerStatusBadgeProps) {
  const variant = CONTAINER_STATUS_CONFIG.VARIANTS[status] ?? 'secondary';
  return (
    <span className={`badge bg-${variant}`} data-testid="container-status-badge">
      {name} — {status}
    </span>
  );
}
```

**2. Container Components (80–120 lines)**
- Data fetching, state management, orchestration
- Input: URL params, query strings, context
- Output: Composed presentational components

```typescript
// ✅ Clear container scope
export function ProjectCard({ projectName }: { projectName: string }) {
  const { data, isLoading, error } = useProjectDetails(projectName);

  if (isLoading) return <PlaceholderLoader />;
  if (error) return <ErrorState message={error.message} />;

  return (
    <div className="card">
      <ProjectHeader project={data} />
      <ContainerList containers={data.containers} />
    </div>
  );
}
```

**3. Logic Components / Utility Classes (static methods)**
- Pure functions, no side effects
- Input: Parameters
- Output: Computed values

```typescript
// ✅ Utility class with static methods
class ContainerStatusHelper {
  static isRunning(status: string): boolean {
    return status === 'running';
  }

  static getVariant(status: string): string {
    const variants: Record<string, string> = {
      running: 'success',
      stopped: 'secondary',
      error: 'danger',
    };
    return variants[status] ?? 'secondary';
  }
}
```

### When to Split a Component (MANDATORY CHECKLIST)

Split **IMMEDIATELY** when a component:
- ✅ **Exceeds 150 lines** (strict maximum)
- ✅ **Has 2+ distinct render sections** (extract each as atomic component)
- ✅ **Mixes calculation + rendering** (extract calculator class)
- ✅ **Has 3+ `useState` hooks** (extract to custom hook or container)
- ✅ **Contains nested conditional rendering** (> 2 levels deep)
- ✅ **Duplicates JSX patterns** (extract reusable atomic component)

---

## Authentication Flow

1. User submits login form with `event.preventDefault()`
2. Form calls `useAuth` hook's `login()` method
3. Service stores token using `STORAGE_KEYS.AUTH_TOKEN`
4. Auth context updates state (`setIsAuthenticated(true)`)
5. `PublicRoute` detects auth state change and redirects to dashboard
6. **No manual navigation** in form component
7. **No `setIsLoading(true)` during login** — causes blank screen

### Critical: `isLoading` State Rule

```typescript
// ❌ WRONG — Causes blank screen (PublicRoute shows null)
const login = async (credentials: LoginCredentials) => {
  setIsLoading(true); // ❌ FORBIDDEN during user action
  // ...
};

// ✅ CORRECT — isLoading ONLY for initial auth check
const [isLoading, setIsLoading] = useState(true); // Initial state only

useEffect(() => {
  const checkAuth = async () => {
    // Check saved token...
    setIsLoading(false); // Only set false here, on init
  };
  checkAuth();
}, []);
```

### 401 Error Handling Pattern

```typescript
// In apiClient.ts interceptor
if (response.status === 401) {
  TokenManager.removeToken();
  window.dispatchEvent(new CustomEvent('auth:unauthorized'));
}

// In useAuth.tsx
useEffect(() => {
  const handleUnauthorized = () => {
    setIsAuthenticated(false);
    // PublicRoute handles redirect automatically
  };
  window.addEventListener('auth:unauthorized', handleUnauthorized);
  return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
}, []);
```

---

## React Query (MANDATORY for Server State)

All API calls MUST go through React Query hooks. Services should let errors propagate — do NOT wrap in `try/catch` unless providing a graceful fallback.

```typescript
// ✅ Let React Query handle errors — no try/catch in service
class ProjectService {
  async listProjects(): Promise<Project[]> {
    const response = await apiClient.get<Project[]>('/projects');
    return response.data;
  }
}

// ✅ React Query hook in component
function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => projectService.listProjects(),
  });
}

// ❌ AVOID — try/catch hiding errors from React Query
async listProjects() {
  try {
    const response = await apiClient.get('/projects');
    return response.data;
  } catch (error) {
    console.error(error);
    throw error; // Useless: React Query handles this
  }
}
```

---

## Routing (React Router 6)

```typescript
// ✅ Programmatic navigation
const navigate = useNavigate();
navigate('/dashboard');

// ✅ Declarative navigation
<Link to="/projects">Projects</Link>
<Navigate to="/login" replace />

// ❌ FORBIDDEN
window.location.href = '/dashboard';
window.location.reload();
location.href = '/login';
```

Centralize all route paths in `src/constants/urls.ts`:

```typescript
// src/constants/urls.ts
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
  PROJECTS: '/projects',
  PROJECT_DETAIL: (name: string) => `/projects/${name}`,
} as const;
```

---

## TypeScript: Types and Interfaces

- All types/interfaces go in `src/types/` (no inline type declarations in components)
- Use `interface` for objects, `type` for unions/aliases
- Never use `any` — prefer `unknown` with type narrowing
- Mark props interfaces with `Props` suffix: `ContainerCardProps`

```typescript
// ✅ Correct — types in dedicated file
// src/types/project.ts
export interface Project {
  name: string;
  status: ProjectStatus;
  containers: Container[];
}

export type ProjectStatus = 'running' | 'stopped' | 'partial';

// ❌ Wrong — inline type in component file
const ProjectCard = ({ project }: { name: string; status: string }) => { /* */ };
```

---

## Configuration Constants

All configuration values, UI labels, and magic strings MUST be in `const` objects.

```typescript
// ✅ Correct — typed const object
export const CONTAINER_STATUS_CONFIG = {
  VARIANTS: {
    running: 'success',
    stopped: 'secondary',
    paused: 'warning',
    error: 'danger',
  },
  ICONS: {
    running: 'bi-play-circle-fill',
    stopped: 'bi-stop-circle',
    paused: 'bi-pause-circle',
    error: 'bi-exclamation-triangle-fill',
  },
} as const;

// ❌ Wrong — hardcoded string in component
<span className="badge bg-success">running</span>
```

---

## Testing Guidelines

- Use `data-testid` attributes for all elements referenced in tests
- Use `faker` + factories for test data; avoid hardcoded repetitive values
- Test behavior, not implementation details

```typescript
// ✅ Stable selector
<button data-testid="start-container-btn" onClick={handleStart}>Start</button>

// ❌ Fragile — relies on translated text
const btn = screen.getByText('Start container');
```

---

## File Structure

```
code/src/
├── components/           # Atomic React components (< 150 lines each)
│   ├── containers/       # Container-related components
│   ├── projects/         # Project-related components
│   ├── layout/           # Layout atoms (NavBar, Sidebar, etc.)
│   └── common/           # Shared atoms (Badge, Button, ErrorState, etc.)
├── pages/                # Route-level page components (thin containers)
├── hooks/                # Custom React hooks (useProjects, useAuth, etc.)
├── services/             # ES6 class services (API calls, token management)
├── constants/
│   ├── config.ts         # STORAGE_KEYS, ROUTES, and app-level configuration
│   └── urls.ts           # ROUTES const object (centralized route paths)
└── types/                # TypeScript interfaces and type aliases
```
