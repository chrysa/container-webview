# Architecture

## Purpose

Docker Overview WebUI — a web interface for managing and visualising Docker Compose
projects. It provides an overview of detected Compose projects, an interactive service/network
topology graph, real-time CPU/memory/network metrics, automatic alerts (exited, restarting,
unhealthy containers), service lifecycle control (start/stop/restart/pause/unpause), and
streaming container logs. Authentication is JWT Bearer with a local admin fallback and optional
LDAP.

## Stack

- **Backend:** Python 3.12, FastAPI 0.111, Uvicorn (standard) 0.29, pydantic-settings 2.2,
  `docker` SDK 7.0, `python-jose[cryptography]` 3.4 (JWT), `python-ldap` 3.4.
- **Frontend:** React 18.3, TypeScript 5.2, Vite 8, `@tanstack/react-query` 5, `react-router-dom`
  6, `axios` 1.18.
- **Tooling:** Ruff + mypy + pytest (coverage) for the backend; ESLint + `tsc` for the frontend;
  pre-commit hooks; hadolint; Docker / Docker Compose; GNU Make; GitHub Actions CI + SonarCloud.

## Layout

```
container-webview/
├── api/                  # FastAPI backend (Python 3.12)
│   ├── app/
│   │   ├── config.py     # Configuration via pydantic-settings
│   │   ├── constants.py  # Constants (StrEnum, Final)
│   │   ├── main.py       # FastAPI app + CORS + routers
│   │   ├── security.py   # JWT service
│   │   ├── routers/      # Thin HTTP controllers (auth, projects, topology,
│   │   │                 #   lifecycle, metrics, alerts, logs)
│   │   ├── services/     # Business logic (auth, docker_client, project_manager,
│   │   │                 #   lifecycle, metrics, alerts, topology)
│   │   └── tests/        # pytest — services + routers
│   ├── pyproject.toml    # Deps + ruff + mypy + pytest + coverage
│   └── Dockerfile        # Stages: base / dev / test / production
├── code/                 # React 18 + Vite + TypeScript frontend
│   └── src/
├── config-tools/         # Configuration tooling
├── scripts/              # Helper scripts
├── makefiles/            # Included Make fragments (docker, node, project, tests, tools)
├── docker-compose.yml    # Development stack
├── Makefile              # Aggregates the makefiles/ fragments
└── .env.example          # Reference environment variables
```

## Entrypoints

- **Backend API:** `api/app/main.py` — FastAPI app; served by Uvicorn. Swagger UI at
  `/api/docs`, API base `/api/v1`. Key routes: `POST /api/v1/auth/login`,
  `GET /api/v1/auth/check`, `GET /api/v1/projects[/{id}]`,
  `GET /api/v1/projects/{id}/topology`, `GET /api/v1/projects/{id}/metrics`,
  `POST /api/v1/projects/{id}/services/{svc}/{start|stop|restart|pause|unpause}`,
  `GET /api/v1/alerts[/project/{id}]`, and WebSocket
  `/api/v1/projects/{id}/services/{svc}/logs`.
- **Frontend:** `code/index.html` + Vite dev server (`vite --host 0.0.0.0 --port 3000`).
- **Orchestration:** `docker-compose.yml` brings up the full dev stack.

## Data / External deps

- **Docker Engine / Compose** — the backend talks to the host Docker daemon via the `docker`
  Python SDK to read projects, metrics, alerts, and to drive service lifecycle and log streams.
- **Compose projects directory** — mounted read-only into the API container at `/projects`
  (`${PROJECTS_PATH:-./data/projects}:/projects:ro`).
- **LDAP** (optional) — external directory for authentication when `LDAP_SERVER` / `LDAP_BASE_DN`
  are set; empty means disabled.
- **Configuration** (see `.env.example`): `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`,
  `PROJECTS_PATH`, `LDAP_SERVER`, `LDAP_BASE_DN`, `FRONTEND_PORT`, `VITE_API_URL`.
- No application database is present in the repo (N/A — not present in repo).

## Build & test

```bash
# Copy and adapt configuration
cp .env.example .env

# Start the development stack (build + run)
docker compose up --build
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/api/docs

# Make targets (real, from README)
make docker-build          # Rebuild images without cache
make docker-up             # Start the stack (foreground)
make docker-up-detach      # Start the stack in the background
make docker-stop           # Stop services

make api-tests             # Run backend tests (pytest)
make api-tests-cov         # Tests + terminal coverage report
make api-tests-html        # Tests + HTML report (htmlcov/)
make api-lint              # Ruff linter
make api-format            # Ruff formatter
make api-typecheck         # mypy

make pre-commit            # Run all pre-commit hooks
make ci-run-local          # Run the CI pipeline locally
```

- Backend tests: **pytest** with coverage target ≥ 80 %, under `api/app/tests/`
  (`services/` and `routers/`).
- Frontend scripts (`code/package.json`): `pnpm dev`, `pnpm build` (`tsc -b && vite build`),
  `pnpm preview`, `pnpm lint` (ESLint), `pnpm type-check` (`tsc --noEmit`).
