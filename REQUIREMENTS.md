# REQUIREMENTS — container-webview

> Generated 2026-09-25. IMPLEMENTED is asserted only where an endpoint/router/service exists in the
> tree. Where behaviour is only claimed in prose (README/Roadmap) it is marked PLANNED or UNVERIFIED.
> Evidence pointers are file paths, not full quotes.

## Product requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-PROD-001 | List all Compose projects detected in a configured directory | IMPLEMENTED | `api/app/routers/projects.py`, `services/project_manager.py`, `GET /api/v1/projects` |
| REQ-PROD-002 | Show project detail | IMPLEMENTED | `GET /api/v1/projects/{id}` (`routers/projects.py`) |
| REQ-PROD-003 | Interactive service/network topology per project | IMPLEMENTED | `routers/topology.py`, `services/topology_service.py`, `GET .../topology` |
| REQ-PROD-004 | Real-time CPU / memory / network metrics per container | IMPLEMENTED | `routers/metrics.py`, `services/metrics_service.py` |
| REQ-PROD-005 | Alerts for anomalous containers (exited/restarting/unhealthy) | IMPLEMENTED | `routers/alerts.py`, `services/alerts_service.py` |
| REQ-PROD-006 | Service lifecycle: start/stop/restart/pause/unpause from UI | IMPLEMENTED | `routers/lifecycle.py`, `services/lifecycle_service.py` |
| REQ-PROD-007 | Authentication (JWT Bearer) with local admin fallback + optional LDAP | IMPLEMENTED | `routers/auth.py`, `security.py`, `services/auth_service.py` |
| REQ-PROD-008 | Streaming container logs over WebSocket | UNVERIFIED (route present; also listed on Roadmap as UI-side todo) | `routers/logs.py`; Roadmap in `README.md` |
| REQ-PROD-009 | Dynamic project management / create-edit services from UI | PLANNED | Roadmap `README.md` |
| REQ-PROD-010 | Export docker-compose (full / per service / dev-prod) | PLANNED | Roadmap `README.md` |
| REQ-PROD-011 | Browser notifications on state changes | PLANNED | Roadmap `README.md` |
| REQ-PROD-012 | Multi-user authentication | PLANNED | Roadmap `README.md` |
| REQ-PROD-013 | Docker Desktop extension | PLANNED | Roadmap `README.md` |

## Technical requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-TECH-001 | Backend FastAPI, thin routers + service layer (clean layering) | IMPLEMENTED | `api/app/routers/` vs `api/app/services/` split |
| REQ-TECH-002 | Config via `pydantic-settings`, env-driven, no hardcoded secrets/paths | IMPLEMENTED | `api/app/config.py`, `.env.example` |
| REQ-TECH-003 | Production secure-config guard (reject default secret / plaintext pwd) | IMPLEMENTED | `config.py` validation (`environment == production` checks) |
| REQ-TECH-004 | JWT auth; bcrypt password hash; constant-time compare | IMPLEMENTED | `security.py` (`hmac.compare_digest`, bcrypt) |
| REQ-TECH-005 | REST under `/api/v1`, OpenAPI/Swagger at `/api/docs` | IMPLEMENTED / UNVERIFIED docs path | `README.md`; `main.py` |
| REQ-TECH-006 | HATEOAS response models | IMPLEMENTED | `api/app/models/hateoas.py` |
| REQ-TECH-007 | Frontend React 18 + TypeScript (strict) + Vite; axios client | IMPLEMENTED | `code/package.json`, `code/src/` |
| REQ-TECH-008 | Typed frontend service clients per domain | IMPLEMENTED | `code/src/api/docker/*.ts` |
| REQ-TECH-009 | Backend tests pytest, coverage floor 80% (target 85%) | UNVERIFIED (not run — docs-only) | `README.md`, `CLAUDE.md`, `api/app/tests/` |
| REQ-TECH-010 | Frontend tests Vitest | UNVERIFIED (config present) | `code/package.json` (`vitest`) |
| REQ-TECH-011 | Multi-stage Dockerfile (base/dev/test/production) | IMPLEMENTED | `api/Dockerfile` (per `README.md`) |
| REQ-TECH-012 | Read-only Docker socket + read-only projects mount | IMPLEMENTED | `docker-compose.yml` (`:ro`) |
| REQ-TECH-013 | Generated context files (handover, ai-instructions, context-map, llms-full) | IMPLEMENTED | `scripts/gen_context_files.py`, generated headers |
| REQ-TECH-014 | Zero-tolerance lint/type (no `# noqa`, no `# type: ignore`) | UNVERIFIED (policy stated; one justified `# noqa: PLC0415` seen for optional ldap import) | `README.md`; `security.py` |

## Notes
- "UNVERIFIED" means the requirement is documented or scaffolded but was not executed/confirmed under
  this docs-only pass (no tests/builds were run).
- Endpoint inventory is authoritative in `README.md`; router files corroborate each family.
