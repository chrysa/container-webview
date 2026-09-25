# CONSTRAINTS — container-webview

> Generated 2026-09-25. Tags: [HARD] enforced by tooling/runtime, [POLICY] canon/convention,
> [ENV] environmental, [ASSUMED] inferred.

## Runtime / environment
- [HARD] Requires a reachable Docker Engine socket; compose mounts `/var/run/docker.sock:ro`. Source: `docker-compose.yml`.
- [HARD] Requires a host directory of Compose sub-projects mounted read-only at `/projects`. Source: `docker-compose.yml`, `.env.example`.
- [ENV] Prerequisites: Docker >= 24, Docker Compose >= 2.20, GNU Make. Source: `README.md`.
- [HARD] Backend Python `>=3.12`. Source: `api/pyproject.toml`. (Discrepancy with 3.14 references — see REVIEW.md C2.)
- [HARD] Pinned backend deps: fastapi 0.111.0, uvicorn 0.29.0, docker 7.0.0, bcrypt 4.2.0, python-ldap 3.4.5, pydantic-settings 2.2.1. Source: `api/pyproject.toml`.
- [HARD] Frontend: React ^18.3, Vite ^8.2, TypeScript ^5.2, axios ^1.18, Vitest ^4.1. Source: `code/package.json`.

## Configuration
- [HARD] All external endpoints/paths/secrets come from the environment (`.env`); none hardcoded. Source: `config.py`, `.env.example`.
- [HARD] Production guard: with `ENVIRONMENT=production`, startup rejects the default `SECRET_KEY`, and rejects plaintext `ADMIN_PASSWORD` unless LDAP is configured (requires `ADMIN_PASSWORD_HASH`). Source: `config.py`.
- [POLICY] `VITE_API_URL` is baked at frontend build time; leave empty when a reverse proxy fronts `/api`. Source: `.env.example`, `README.md`.

## Quality gates ([POLICY], per CLAUDE.md / README / AGENTS.md — not executed here)
- Max function length 50 lines; max file length 500 lines; complexity heuristic <= 10.
- Lint warnings: 0; mypy clean; SonarCloud rating A.
- Test coverage target 85% (floor 80%).
- Ruff "zero tolerance": no `# noqa`, no `# type: ignore` (one justified `# noqa: PLC0415` for the optional ldap import is present in `security.py`).
- `force-single-line` imports; single return point per function; 100% type annotations on public functions.

## Portability ([POLICY], chrysa canon)
- Everything machine-agnostic and portable; runs in containers; no host virtualenv; caches never touch the project tree. Source: managed standards block in `CLAUDE.md`.

## Networking
- [ASSUMED] Only publicly useful ports published (api 8000, frontend 3000 in dev). Source: `docker-compose.yml`; canon `standards/rules/containers.md`.
