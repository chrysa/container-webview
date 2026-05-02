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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **container-webview** (1209 symbols, 1758 relationships, 14 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/container-webview/context` | Codebase overview, check index freshness |
| `gitnexus://repo/container-webview/clusters` | All functional areas |
| `gitnexus://repo/container-webview/processes` | All execution flows |
| `gitnexus://repo/container-webview/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
