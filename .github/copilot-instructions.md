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

<!-- chrysa:standards-copilot:start · generated · DO NOT EDIT -->
## chrysa standards (generated)

> The same rules as `CLAUDE.md`, for GitHub Copilot. Detail loads on demand from `standards/rules/<domain>.md`; the canon is `standards/STANDARDS.chrysa.md`.

### Governance, language & compliance · `standards/rules/governance.md`
- Normative annexes
- Language
- Compliance targets
- Governance — strategic pillars & ADR format

### Cross-cutting stack · `standards/rules/stack.md`
- Cross-cutting stack (settled ADRs — do not relitigate)

### SCM — branches, commits & pull requests · `standards/rules/scm.md`
- Commits
- Branches
- Branch model — `main` is production, `develop` is the workspace
- Merge
- One PR per issue
- Issues and PRs are type-driven

### Architecture, decoupling & portability · `standards/rules/architecture.md`
- Repo provenance — every code repo depends on `project-init`
- Every repo declares its profile and DDD level
- Projects talk through versioned contracts only
- Everything is machine-agnostic and portable — no rule, repo, or script is bound to one machine
- Every external server the service talks to is addressed through the environment — never hardcoded
- Every tracked file and folder must earn its place — a repo holds only what is useful to it now
- The repository architecture is legible to an agent — optimised for Claude, not only for humans
- Deferred work is a governed job, not a fire-and-forget

### Testing · `standards/rules/testing.md`
- Tests: pytest only
- Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later

### Frontend & web semantics · `standards/rules/frontend.md`
- TypeScript is strict by contract
- The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden
- React is a presentation layer, not the domain
- The frontend says when the backend is unreachable or unstable
- The frontend is reactive and real-time by default
- UI state survives reload & focus
- Everything is semantic — the markup, the data, and the URLs
- URL-addressable frontend navigation — mandatory

### APIs, contracts & real-time · `standards/rules/api.md`
- A real-time backend has channel contracts and never blocks
- APIs, SDKs & public contracts follow the `STD-API-001` contract

### Accessibility · `standards/rules/accessibility.md`
- Dark mode
- Every site is usable by the majority of disabilities — not only the screen-reader case

### Documentation & session state · `standards/rules/docs.md`
- Notion logging
- Documentation and Notion are maintained in lockstep with the code — a change that leaves them stale is unfinished
- Session lifecycle (primer + memory + hindsight)

### AI agents & features · `standards/rules/agents.md`
- Agent actions are governed
- An AI feature is evaluated, not just shipped
- An agent writes only where the owner owns

### Security, identity & sessions · `standards/rules/security.md`
- Per-person data implies a user account — no exceptions dressed up as simplicity
- Identity goes through the cluster SSO first
- A session is secured and it expires
- Every form is a hostile input surface — validate on the server, always

### Code quality & anti-patterns · `standards/rules/code-quality.md`
- No hardcoded constants
- No literal HTTP status codes — use the constants the framework already ships
- No code duplication — the second occurrence is an extraction order
- Raised errors are typed
- Failures are contained, and observable
- Prefer a lookup table to a state machine
- Decompose into small, independently unit-testable methods
- Code is read far more often than it is written — optimise for the reader, and standardise the form
- Avoid lambdas and anonymous constructs — a named function is the default
- Basic optimisations and known anti-patterns are caught in review and in CI
- A cache is a correctness contract, not a sprinkle of speed
- Quality gates
- Error handling pattern (all automations)

### Backend Python · `standards/rules/backend-python.md`
- Python packaging — `pyproject.toml` is the single source of truth
- Python is written object-oriented, one class per file
- Import the item, not the module — `from x import y; y()`
- Functions and methods are called with named arguments — positional call sites are the exception, not the rule

### Data, persistence & migrations · `standards/rules/data.md`
- Data, persistence & migrations follow the `STD-DATA-001` contract

### Observability & operations · `standards/rules/observability.md`
- Observability & production readiness follow the `STD-OPS-001` contract
- The container is versioned separately from the application it hosts, and an admin can see what is actually deployed
- Observability — error-tracking → GitHub issues (norm)

### Containers & compose · `standards/rules/containers.md`
- Everything runs in a container — the only exception is the slice of a repo genuinely bound to the host OS
- External dependencies are installed in containers, never on the host
- No virtualenv in a repo — ever
- Tool caches & deps never touch the project tree
- Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory
- App containers ship the app only — the platform layer is the owner's responsibility
- Only a publicly useful port is published — everything else stays on the container network
- A compose file is minimal — declare only what the stack needs, default the rest
- Dev stage must hot-reload
- Local dev runs the code in-container, live, in debug mode — never the production server
- `.dockerignore` mandatory & exhaustive
- Container-runtime policy

### Product surfaces · `standards/rules/product.md`
- Setup wizard & config panel
- A game is DRM-free and fully playable solo offline
- Every product that is operated ships a management backoffice
- If a user can supply a file, the product accepts an upload
- A floating assistant where it earns its place — never as decoration

### Design system · `standards/rules/design.md`
- Design system

### Developer loop & tooling · `standards/rules/dev-loop.md`
- Makefile targets
- Shared skills (load on demand from shared-standards/.claude/skills/)

### CI/CD, pre-commit & release · `standards/rules/ci-cd.md`
- Release & changelog config (canonical)
- GitHub Actions (reuse first · custom actions centralised · thin workflows)
- Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)
<!-- chrysa:standards-copilot:end -->
