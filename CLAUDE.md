# container-webview — Claude context

## What does this project do?

Web GUI for managing Docker Compose projects and Kubernetes workloads. Two components:
- **API** (`api/`): FastAPI backend that queries the Docker daemon, parses docker-compose YAMLs, and maps service dependency graphs
- **Frontend** (`code/`): React 19 + Vite SPA with service graph visualization and lifecycle controls

Target features:
- Visualize docker-compose service dependency graph (ReactFlow)
- Start/stop/restart/remove containers
- Stream real-time logs via WebSocket
- Monitor metrics (CPU, memory) via Recharts
- Authentication via JWT

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI 0.111 + Uvicorn, Python 3.12 |
| Docker client | docker-py 7.0 |
| Auth | python-jose (JWT) — CVE-2024-33664: migrate to PyJWT |
| Config parsing | PyYAML 6, pydantic-settings |
| Frontend | React 19 + Vite 6 + TypeScript (strict) |
| State | TanStack Query v5 |
| Routing | React Router v7 (lazy loading) |
| Graph | @xyflow/react v12 (ReactFlow) |
| Charts | Recharts |
| HTTP | Axios + interceptors (Bearer auto, 401 redirect) |
| Container | Docker multi-stage (deps → build → serve@14) |
| Infra | Kubernetes + Kustomize + Traefik IngressRoute |
| CI | GitHub Actions |
| Pre-commit | pre-commit hooks (ruff, eslint, prettier, hadolint…) |
| Versioning | GitVersion (Mainline) + git-cliff (CHANGELOG) |

## Repository structure

```
api/
  app/            FastAPI application
    routers/      auth, projects, topology, lifecycle, logs, metrics, alerts
    services/     docker_client, project_manager, auth_service…
    config.py     pydantic-settings
    security.py   JWT / SecurityService
  pyproject.toml  project deps
  Dockerfile      multi-stage (deps / dev / test / production)
code/
  src/
    api/http/     Axios client + interceptors
    domain/       types.ts + queries.ts per domain
    features/     domain-bound components
    components/   reusable UI (layouts, loaders)
    pages/        route-level components (lazy)
    hooks/        useAuth, useTheme
    styles/       SCSS Modules (_globals, _theme, _variables)
    utils/        auth.ts (localStorage token)
k8s/              Kustomize manifests + Traefik IngressRoute
makefiles/        Modular Makefile (docker, node, api, tests, tools)
config-tools/     Shared linting configs (hadolint, yamllint, markdownlint…)
.github/
  workflows/      ci.yml, cd.yml, release.yml, quality.yml
  instructions/   architecture, frontend, backend, docker_k8s guidelines
```

## Development workflow

```bash
make dev-up       # docker-compose up (api + frontend hot-reload)
make prod-up      # production stack
make dev-down     # stop containers
make api-lint     # ruff check + format
make node-build   # vite build
make pre-commit   # run all pre-commit hooks
```

API standalone:
```bash
cd api && uvicorn app.main:app --reload --port 8000
```

Frontend standalone:
```bash
cd code && npm run dev   # Vite dev server (port 3000)
npm run build            # TypeScript check + Vite bundle
npm run lint             # ESLint v9
```

## Key conventions

- **DDD**: domain logic in `api/app/services/`, routers only delegate
- **Strict typing**: mypy/ruff on Python, no `any` in TypeScript
- **Network**: TanStack Query for all HTTP calls, no direct `fetch` in components
- **JWT**: stored in `localStorage` via `utils/auth.ts`
- **WebSocket logs**: token passed as query param (exception to Bearer header rule)
- **Vite proxy**: `/api` → `http://api:8000` (WebSocket included)
- **K8s routing**: `PathPrefix(/api)` → FastAPI:8000, `PathPrefix(/)` → Frontend:3000

## Environment variables

From `.env.example`:
- `MAINTAINER_NAME`, `MAINTAINER_MAIL`
- `FQDN`, `CONTAINER_WEBVIEW_PREFIX_URL`
- `JWT_SECRET_KEY` — API auth secret
- `VITE_API_URL` — empty in K8s (relative URLs), `http://localhost:8000` locally

## Known issues / pending migrations

- `python-jose` CVE-2024-33664 → migrate to `PyJWT` or `authlib`
- Docker socket security: use read-only mount, consider rootless Docker
