# Container WebView — GitHub Copilot Instructions

## 🚨 MANDATORY: Read Instructions FIRST

**Before starting ANY development task**, read the relevant instruction files in `.github/instructions/`.

### Available instruction files

- `.github/instructions/architecture.instructions.md` — Stack, structure monorepo, conventions globales
- `.github/instructions/frontend_guidelines.instructions.md` — React 19, patterns TypeScript, hooks, SCSS Modules
- `.github/instructions/backend_guidelines.instructions.md` — FastAPI, DDD, Python typing strict
- `.github/instructions/docker_k8s.instructions.md` — Dockerfile, docker-compose, manifests K8s, Traefik

**Apply pattern**: `**/*` — Ces règles s'appliquent à l'ensemble du projet.

______________________________________________________________________

## 🏗️ Architecture Overview

**Type** : Monorepo full-stack — UI de management de conteneurs Docker/Compose/Kubernetes

```
container-webview/
├── api/          # Backend FastAPI (Python 3.12)
├── code/         # Frontend React 19 + Vite + TypeScript
├── k8s/          # Manifests Kubernetes (Kustomize + Traefik)
├── makefiles/    # Makefile modulaire (docker, node, api, project)
└── config-tools/ # Configs linting (hadolint, yamllint, markdownlint…)
```

### Backend — `api/`

- **Framework** : FastAPI + Uvicorn
- **Langage** : Python 3.12, typage **strict** (`mypy`/`ruff`)
- **Architecture** : Domain-Driven Design (DDD) — domaines dans `app/`
- **Routers** : `auth`, `projects`, `topology`, `lifecycle`, `logs`, `metrics`, `alerts`
- **Services** : `docker_client` (Docker SDK), `project_manager` (YAML parsing)
- **Auth** : JWT via `python-jose`, OAuth2PasswordBearer
- **WebSocket** : streaming de logs en temps réel (`/api/projects/{id}/services/{name}/logs`)

### Frontend — `code/`

- **Framework** : React 19 + Vite 6 + TypeScript (strict ES2022)
- **Routing** : React Router v7 (lazy loading, `RequireAuth` guard)
- **State** : TanStack Query v5 (`@tanstack/react-query`)
- **UI** : SCSS Modules + lucide-react
- **Graphes** : `@xyflow/react` (ReactFlow) pour la topologie
- **Métriques** : Recharts
- **HTTP** : Axios avec intercepteurs (token Bearer auto, redirect 401)

### Infrastructure

- **Conteneurs** : Docker multi-stage (deps → build → production avec `serve@14`)
- **K8s** : Kustomize, Traefik IngressRoute CRD (`traefik.io/v1alpha1`)
- **Routing Traefik** : `PathPrefix(/api)` → FastAPI:8000, `PathPrefix(/)` → Frontend:3000
- **VITE_API_URL** : vide en K8s (URLs relatives), `http://localhost:8000` en local

______________________________________________________________________

## ⚠️ RÈGLES NON NÉGOCIABLES

### 1. Toutes les commandes passent par le Makefile

- **NEVER run** `docker compose`, `npm`, `uvicorn` directement en dehors du Makefile
- Utiliser `make prod-up`, `make dev-up`, `make node-build`, `make api-lint`, etc.

### 2. Typage strict partout

**Python** :

- Toutes les fonctions ont des annotations de type (`-> None`, `-> str`, etc.)
- Pas de `Any` sauf exception documentée
- Utiliser `ruff` pour le format et le lint

**TypeScript** :

- Pas de `any` implicite
- Interfaces dans `src/domain/*/types.ts`
- Pas de `// @ts-ignore` sans commentaire explicatif

### 3. Architecture DDD côté API

```
api/app/
├── routers/      # Couche présentation — endpoints HTTP/WS
├── services/     # Couche application — logique orchestration
├── domain/       # (à venir) — entités, value objects, repos
└── config.py / security.py
```

- Pas de logique métier dans les routers
- Les services orchestrent, les routers délèguent

### 4. Structure frontend rigoureuse

```
code/src/
├── api/http/     # client Axios + intercepteurs
├── domain/       # types.ts + queries.ts par domaine (auth, projects…)
├── features/     # composants "feature" liés à un domaine
├── components/   # composants UI réutilisables (layouts, loaders)
├── pages/        # route-level components (lazy-loaded)
├── hooks/        # useAuth, useTheme
├── styles/       # SCSS Modules + _globals, _theme, _variables
└── utils/        # auth.ts (localStorage token)
```

- Les `pages/` ne contiennent que du routing et de la composition
- La logique réseau est dans `domain/*/queries.ts` via TanStack Query
- Pas de `fetch` direct dans les composants

### 5. Sécurité

- Pas de secrets dans le code — utiliser `.env` ou K8s Secrets
- `k8s/secret.yaml` est exclu de Kustomize — appliquer manuellement
- Les tokens JWT sont stockés en `localStorage` via `utils/auth.ts`
- Les WebSocket logs passent le token via query param (seule exception au header Bearer)

______________________________________________________________________

## 🔄 Flux de développement

1. `make dev-up` — démarre API + frontend en mode watch
1. Frontend : `http://localhost:3000`, API : `http://localhost:8000`
1. Hot-reload : Vite pour le frontend, `--reload` Uvicorn pour l'API
1. Proxy Vite : `/api` → `http://api:8000` (WebSocket inclus)

## 🚀 CI/CD — GitHub Actions

- **`ci.yml`** : lint + build sur chaque push (tous les branches)
- **`cd.yml`** : build Docker + push GHCR + déploiement K8s (branch `main` uniquement)
- Images dans GitHub Container Registry : `ghcr.io/chrysa/container-webview/api:SHA`
- Déploiement via `kubectl kustomize k8s/ | kubectl apply -f -`
- Variable requise : `KUBE_CONFIG` (base64 du kubeconfig) dans les secrets GitHub

## Automation & Industrialization (NON-NEGOTIABLE)

- Projects must be **maximally automated and industrialized**.
- Every repetitive task must be covered by one of: CI/CD pipeline, Makefile target, pre-commit hook, GitHub Actions workflow, or a bot/script.
- Required automation baseline for any project:
    - **CI/CD**: automated lint, type-check, tests, build on every push/PR.
    - **Formatting**: auto-applied via pre-commit or CI (no manual `ruff`/`prettier` runs).
    - **Releases**: automated versioning and changelog generation (e.g. `cliff`, `semantic-release`).
    - **Dependency updates**: automated via Dependabot or Renovate.
    - **Secret scanning**: automated on every commit (pre-commit hook + CI step).
- When proposing or implementing a feature, always include the automation layer (tests, CI step, Makefile target) — not just the code.
- Any manual step that could be automated is considered **technical debt** and must be tracked.

## Canonical Templates & Shared Tooling

### React applications
- All new React apps **must** be bootstrapped from `Forge-Stack-Workshop/react-app-generator`.
- Never scaffold from scratch or from `create-react-app`/`vite` directly.

### Makefiles
- All project Makefiles **must** extend or be derived from `Forge-Stack-Workshop/base-makefile`.
- Do not duplicate targets that already exist in the base — inherit instead.

### Pre-commit hooks
- If a required hook is missing from `chrysa/pre-commit-tools`, **open an issue** on that repo describing the hook needed before proceeding.
- In the requesting repo, open a matching issue/PR and mark it as dependent (`Depends on chrysa/pre-commit-tools#<N>`).
- Do not implement a workaround locally — wait for the hook to land in the shared repo.

### Issue resolution automation (desired workflow)
- When a blocking issue is opened (e.g. missing hook, missing template), an agent should:
    1. Analyse the issue and propose a solution on the upstream repo.
    2. Once the solution is validated (human approval), automatically unblock the dependent issue/PR in the requesting repo.
- This workflow is aspirational — track automation gaps as issues on the relevant repos.

