# Docker Overview WebUI

Web interface for managing and visualising Docker Compose projects — interactive topology, real-time metrics, alerts, and service lifecycle management.

[![CI](https://github.com/chrysa/container-webview/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/container-webview/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=chrysa_container-webview&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=chrysa_container-webview)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=chrysa_container-webview&metric=coverage)](https://sonarcloud.io/summary/new_code?id=chrysa_container-webview)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=chrysa_container-webview&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=chrysa_container-webview)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=chrysa_container-webview&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=chrysa_container-webview)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=chrysa_container-webview&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=chrysa_container-webview)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

---

## Table of Contents

- [Docker Overview WebUI](#docker-overview-webui)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [Configuration](#configuration)
  - [API Endpoints](#api-endpoints)
  - [Make Commands](#make-commands)
  - [Tests](#tests)
  - [Code Quality](#code-quality)
  - [Roadmap](#roadmap)

---

## Features

- **Overview** — lists all Compose projects detected in the configured directory
- **Topology** — interactive graph of services and networks within a project
- **Metrics** — real-time CPU, memory, and network stats per container
- **Alerts** — automatic detection of anomalous containers (exited, restarting, unhealthy)
- **Lifecycle** — start / stop / restart / pause / unpause from the UI
- **Authentication** — JWT Bearer, local fallback + optional LDAP

---

## Architecture

```
docker-overview-webui/
├── api/                        # FastAPI backend (Python 3.12)
│   ├── app/
│   │   ├── config.py           # Configuration via pydantic-settings
│   │   ├── constants.py        # Constants (StrEnum, Final)
│   │   ├── main.py             # FastAPI app + CORS + routers
│   │   ├── security.py         # JWT service
│   │   ├── routers/            # HTTP controllers (thin)
│   │   │   ├── auth.py         # POST /api/auth/login, GET /api/auth/check
│   │   │   ├── projects.py     # GET /api/projects[/{id}]
│   │   │   ├── topology.py     # GET /api/projects/{id}/topology
│   │   │   ├── lifecycle.py    # POST /api/projects/{id}/services/{svc}/{action}
│   │   │   ├── metrics.py      # GET /api/projects/{id}/metrics
│   │   │   ├── alerts.py       # GET /api/alerts[/project/{id}]
│   │   │   └── logs.py         # WebSocket /api/projects/{id}/services/{svc}/logs
│   │   ├── services/           # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── docker_client.py
│   │   │   ├── project_manager.py
│   │   │   ├── lifecycle_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── alerts_service.py
│   │   │   └── topology_service.py
│   │   └── tests/              # pytest — services + routers
│   ├── pyproject.toml          # Dependencies + ruff + mypy + pytest + coverage
│   └── Dockerfile              # Stages: base / dev / test / production
├── code/                       # React 18 + Vite + TypeScript frontend
│   └── src/
├── docker-compose.yml          # Development stack
├── Makefile                    # Make targets
└── .env.example                # Reference environment variables
```

---

## Prerequisites

- Docker ≥ 24
- Docker Compose ≥ 2.20
- Make (GNU)
- A local directory containing Compose project sub-folders

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/chrysa/container-webview.git
cd container-webview

# 2. Copy and adapt the configuration
cp .env.example .env
# Edit .env: SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, PROJECTS_PATH

# 3. Create a projects directory (or point to an existing one)
mkdir -p data/projects

# 4. Start the development stack
docker compose up --build

# 5. Open the UI
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/docs
```

Default credentials if not configured: `admin` / `admin`.

---

## Configuration

All variables are documented in [.env.example](.env.example).

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | JWT signing key — **change in production** |
| `ADMIN_USERNAME` | `admin` | Local admin username |
| `ADMIN_PASSWORD` | `admin` | Local admin password — **change in production** |
| `PROJECTS_PATH` | `/projects` | Container path to Compose projects |
| `LDAP_SERVER` | _(empty)_ | LDAP URL (`ldap://host:389`) — empty = disabled |
| `LDAP_BASE_DN` | _(empty)_ | LDAP base DN |
| `FRONTEND_PORT` | `3000` | Exposed port for the frontend |
| `VITE_API_URL` | `http://localhost:8000` | API URL as seen from the browser |

The volume `${PROJECTS_PATH:-./data/projects}:/projects:ro` in `docker-compose.yml` mounts your local Compose projects directory.

---

## API Endpoints

Interactive documentation available at `http://localhost:8000/docs` (Swagger UI).

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authentication — returns a JWT Bearer token |
| `GET` | `/api/auth/check` | Validates the current token |
| `GET` | `/api/projects` | Lists all detected Compose projects |
| `GET` | `/api/projects/{id}` | Project details |
| `GET` | `/api/projects/{id}/topology` | Project topology graph |
| `GET` | `/api/projects/{id}/metrics` | CPU/RAM/network metrics for all containers |
| `POST` | `/api/projects/{id}/services/{svc}/start` | Start a service |
| `POST` | `/api/projects/{id}/services/{svc}/stop` | Stop a service |
| `POST` | `/api/projects/{id}/services/{svc}/restart` | Restart a service |
| `POST` | `/api/projects/{id}/services/{svc}/pause` | Pause a service |
| `POST` | `/api/projects/{id}/services/{svc}/unpause` | Resume from pause |
| `GET` | `/api/alerts` | All active alerts |
| `GET` | `/api/alerts/project/{id}` | Alerts filtered by project |
| `WS` | `/api/projects/{id}/services/{svc}/logs` | Streaming logs (WebSocket) |

---

## Make Commands

```
make docker-build           # Rebuild images without cache
make docker-up              # Start the stack (foreground)
make docker-up-detach       # Start the stack in the background
make docker-stop            # Stop services

make api-tests              # Run backend tests
make api-tests-cov          # Tests + terminal coverage report
make api-tests-html         # Tests + HTML report (htmlcov/)
make api-lint               # Ruff linter
make api-format             # Ruff formatter
make api-typecheck          # mypy

make pre-commit             # Run all pre-commit hooks
make ci-run-local           # Run the CI pipeline locally
```

---

## Tests

Backend tests use **pytest** with coverage ≥ 80 %.

```bash
# Run all tests (Docker)
make api-tests

# With coverage report
make api-tests-cov

# With HTML report
make api-tests-html
```

Test structure:

```
api/app/tests/
├── conftest.py                  # Shared fixtures (fake, api_client, auth_headers…)
├── test_main.py                 # /api endpoint (ping)
├── services/
│   ├── test_docker_client.py
│   ├── test_lifecycle_service.py
│   ├── test_alerts_service.py
│   ├── test_metrics_service.py
│   ├── test_project_manager.py
│   ├── test_auth_service.py
│   └── test_topology_service.py
└── routers/
    ├── test_auth.py
    ├── test_projects.py
    ├── test_lifecycle.py
    ├── test_metrics.py
    ├── test_alerts.py
    └── test_topology.py
```

---

## Code Quality

The backend enforces **zero-tolerance** Ruff compliance:

- **Zero `# noqa`** and zero `# type: ignore` — every violation is fixed at source
- **`force-single-line` imports** — one symbol per import line
- **Single return point** — each function stores its result in a variable and returns at the end of the body
- **100 % type annotations** on public functions and methods
- **`TYPE_CHECKING`** for annotation-only imports (no runtime overhead)
- **No bare `return None` or `return`** — `-> None` functions end by fall-off

```bash
make api-lint        # Ruff linter (zero tolerance)
make api-format      # Ruff formatter
make api-typecheck   # mypy
make pre-commit      # All hooks (ruff, mypy, hadolint, prettier…)
```

---

## Roadmap

- [ ] Dynamic project management from the topology graph
- [ ] Create / edit services from the UI
- [ ] Export docker-compose (full, per service, dev/prod)
- [ ] Log access from the UI (WebSocket)
- [ ] Browser notifications on container state changes
- [ ] Multi-user authentication
- [ ] Docker Desktop extension
