# Docker Overview WebUI — Copilot Instructions

## ⚠️ MANDATORY WORKFLOW

**BEFORE ANY TASK:**

1. **Read `.github/instructions/`** — Check for specific technical guidelines
2. **Apply relevant patterns** — Use instruction files that match your task
3. **Follow project standards** — Ensure compliance with established rules

---

## Role and Responsibilities

You are GitHub Copilot, an AI assistant for the **Docker Overview WebUI** project.

- **Backend**: FastAPI + Python 3.12+, service-class architecture, JWT auth, Docker SDK
- **Frontend**: React 18 + Vite + TypeScript + React Router + React Query + Bootstrap 5

Always apply the engineering rules from the instruction files in `.github/instructions/`. Those guidelines are authoritative for this project.

---

## Project Structure

```
docker-overview-webui/
├── api/                  # FastAPI backend
│   ├── app/
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── constants.py       # StrEnum + Final constants
│   │   ├── main.py            # FastAPI app + CORS + routers
│   │   ├── security.py        # JWT token service
│   │   ├── routers/           # HTTP route handlers (thin controllers)
│   │   └── services/          # Business logic (docker_client, project_manager,
│   │                          #   auth_service, lifecycle_service, metrics_service,
│   │                          #   alerts_service, topology_service)
│   └── Dockerfile
├── code/                 # React/Vite frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       └── constants/
├── docker-compose.yml
└── .github/
    └── instructions/     # ← Technical guidelines (read before any task)
```

---

## Key Principles

- **Security first**: no hardcoded secrets, validate all inputs, OWASP Top 10
- **Readability > cleverness**: explicit variable names, docstrings, type hints
- **Service layer**: business logic in service classes; routers are thin controllers
- **No HTTP coupling in services**: services raise `ValueError`; routers translate to `HTTPException`
- **Composition over inheritance**

---

## Docker and Build System Rules

- **All commands via Docker Compose**: use `docker compose up --build`
- **Never run Python locally**: all execution inside containers
- **Make targets** for common tasks (see `Makefile`)

---

## Instructions Management

For every task, check `.github/instructions/` and apply relevant files:

| File | Covers | Applies to |
|------|--------|-----------|
| `python_guidelines.instructions.md` | Python code quality, architecture, patterns | `api/**/*.py` |
| `ruff_compliance.instructions.md` | Ruff linting rules | `api/**/*.py` |
| `typing.instructions.md` | Type hint requirements | `api/**/*.py` |
| `tests.instructions.md` | pytest patterns, mocking, factories | `api/**/tests/**/*.py` |
| `frontend_guidelines.instructions.md` | React/TypeScript architecture | `code/src/**` |

---

All contributors and automation must comply with these rules.
