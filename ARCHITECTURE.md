# ARCHITECTURE — container-webview (Docker Overview WebUI)

> Status: descriptive documentation generated from the working tree on 2026-09-25.
> Tags: FACT (verifiable in-repo), INFERENCE (reasoned from evidence), UNKNOWN (not determinable from the repo).
> Authority: the canonical rules are `standards/` + the managed block in `CLAUDE.md`. This file documents, it does not legislate.

## Purpose

FACT — Web interface to discover, monitor and control local Docker Compose projects: interactive
topology, real-time container metrics, alerts, and service lifecycle (start/stop/restart/pause/unpause).
Source: `README.md`, `CLAUDE.md`, `context-map.json`, `handover.md`.

## Components

FACT — Two deployable surfaces plus a shared standards/tooling layer.

### Backend — `api/` (FastAPI, Python)
Source: `api/app/`, `api/pyproject.toml`, `README.md` (Architecture section).

- `app/main.py` — FastAPI app, CORS, router registration.
- `app/config.py` — configuration via `pydantic-settings`; production secure-config guards.
- `app/constants.py` — `StrEnum` / `Final` constants (no magic literals).
- `app/security.py` — JWT service + auth verification (bcrypt, LDAP optional).
- `app/models/hateoas.py` — HATEOAS response models (Pydantic v2).
- `app/routers/` — thin HTTP controllers: `auth`, `projects`, `topology`, `lifecycle`, `metrics`,
  `alerts`, `logs` (WebSocket).
- `app/services/` — business logic: `auth_service`, `docker_client`, `project_manager`,
  `lifecycle_service`, `metrics_service`, `alerts_service`, `topology_service`.
- `app/tests/` — pytest suite mirroring `services/` and `routers/`.

### Frontend — `code/` (React 18 + TypeScript + Vite)
Source: `code/src/`, `code/package.json`, `code/README.md`.

- `src/api/docker/*` — typed service clients (`authService`, `projectService`, `topologyService`,
  `metricsService`, `lifecycleService`, `alertsService`) over `src/api/http/client.ts` (axios).
- `src/pages/` — `LoginPage`, `DashboardPage`, `ProjectDetailPage`.
- `src/components/` and `src/features/` — UI: alerts panel, metrics table, project card, layouts
  (header, protected/public routes), loaders, shared error/spinner. INFERENCE — `components/` and
  `features/` both contain `AlertsPanel`, `MetricsTable`, `ProjectCard`; appears to be a mid-migration
  toward a feature-folder layout (see REVIEW.md).
- `src/providers/` — `AuthProvider` + `AuthContext`; `src/hooks/useAuth.ts`.
- `src/stores/loadingStore.ts` — global loading state (INFERENCE — Zustand-style store).
- `src/constants/`, `src/types/`, `src/utils/` (`logger`, `result`).

### Shared layer
FACT — `standards/` (chrysa canon rules, on-demand), `makefiles/` (modular make includes),
`scripts/gen_context_files.py` + `scripts/quality_gate.py`, `config-tools/` and `.config/` (linter configs).

## Data flow

INFERENCE (from router/service names and compose mounts):

1. Browser → frontend service clients → backend REST under `/api/v1/*` (JWT Bearer).
2. Backend `docker_client` talks to the Docker Engine via the mounted socket
   `/var/run/docker.sock:ro` (FACT — `docker-compose.yml`).
3. Compose project directories are read from a host directory mounted read-only at `/projects`
   (FACT — `docker-compose.yml`, `.env.example`).
4. Log streaming uses a WebSocket route `/api/v1/projects/{id}/services/{svc}/logs` (FACT — `README.md`).

## Persistence

FACT — No application database is present in the repo. State derives from the live Docker Engine and
from Compose files on the mounted `/projects` volume. Auth is stateless (JWT). UNKNOWN — whether any
future persistence is planned beyond the roadmap.

## Integrations

- FACT — Docker Engine via local socket (read-only mount).
- FACT — Optional LDAP authentication (`LDAP_SERVER`, `LDAP_BASE_DN`, `LDAP_BIND_DN`,
  `LDAP_BIND_PASSWORD`); `python-ldap` imported only when enabled.
- FACT — SonarCloud + GitHub Actions CI (badges in `README.md`, `.github/workflows/`).

## Deployment

FACT — Development stack via `docker compose up --build` (`docker-compose.yml`): `api` (uvicorn
`--reload`, port 8000), `frontend` (Vite dev server, port 3000), `api-test` (test profile).
FACT — `api/Dockerfile` is multi-stage (`base` / `dev` / `test` / `production`).
INFERENCE — production deployment topology (reverse proxy, image registry, release target) is
referenced (`VITE_API_URL` proxy note, `.github/workflows/cd.yml`, `release.yml`) but not fully
specified in-repo; see UNKNOWN in DECISIONS.md.

## Runtime constraints

See CONSTRAINTS.md.
