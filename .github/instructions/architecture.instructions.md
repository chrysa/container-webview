______________________________________________________________________

## applyTo: "\*\*/\*"

# Architecture — Container WebView

## Stack technique

| Couche         | Technologie                                  |
| -------------- | -------------------------------------------- |
| Backend        | Python 3.12, FastAPI, Uvicorn                |
| Frontend       | React 19, Vite 6, TypeScript strict (ES2022) |
| State          | TanStack Query v5                            |
| Routing        | React Router v7 (lazy + RequireAuth)         |
| UI             | SCSS Modules, lucide-react                   |
| Graph          | @xyflow/react (ReactFlow)                    |
| Charts         | Recharts                                     |
| HTTP           | Axios + intercepteurs Bearer/401             |
| Linting Python | ruff (format + lint)                         |
| Linting TS     | ESLint v9 flat config                        |
| Conteneurs     | Docker multi-stage, serve@14                 |
| Orchestration  | Kubernetes + Traefik IngressRoute            |
| CI/CD          | GitHub Actions → GHCR → K8s                  |

## Structure du monorepo

```
container-webview/
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/          ← fichiers de règles par domaine
│   └── workflows/             ← ci.yml, cd.yml, quality.yml
├── api/                       ← Backend FastAPI
│   ├── app/
│   │   ├── routers/           ← endpoints HTTP + WebSocket
│   │   ├── services/          ← logique métier / orchestration
│   │   ├── config.py
│   │   └── security.py        ← JWT, OAuth2
│   ├── Dockerfile
│   └── requirements.txt
├── code/                      ← Frontend React 19
│   ├── src/
│   │   ├── api/http/          ← client Axios + intercepteurs
│   │   ├── domain/            ← types.ts + queries.ts par domaine
│   │   ├── features/          ← composants liés à un domaine
│   │   ├── components/        ← UI réutilisable (layouts, loaders)
│   │   ├── pages/             ← route-level (lazy-loaded)
│   │   ├── hooks/
│   │   ├── styles/
│   │   └── utils/
│   ├── eslint.config.js
│   ├── vite.config.ts
│   └── package.json
├── k8s/                       ← Manifests Kubernetes
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml            ← exclu de kustomize, appliquer manuellement
│   ├── api/
│   ├── frontend/
│   └── ingress/               ← Traefik IngressRoute CRD
├── makefiles/                 ← Makefile modulaire
│   ├── docker.makefile
│   ├── node.makefile
│   ├── api.makefile
│   └── project.makefile
├── config-tools/              ← configs hadolint, yamllint, markdownlint…
├── Dockerfile                 ← build frontend (multi-stage)
├── docker-compose.yml         ← 4 services: api, frontend, api-dev, frontend-dev
└── Makefile                   ← point d'entrée unique
```

## Conventions de nommage

- **Fichiers Python** : `snake_case.py`
- **Fichiers TS/TSX** : `PascalCase.tsx` pour composants, `camelCase.ts` pour utils/hooks
- **SCSS Modules** : `ComponentName.module.scss` colocalié avec le composant
- **Types TS** : exportés depuis `src/domain/*/types.ts`, interfaces en `PascalCase`
- **Queries** : exportées depuis `src/domain/*/queries.ts`, préfixe `use` pour les hooks

## Règles de commit

- Toujours utiliser `pre-commit` avant de committer
- Pas de commit direct sur `main` (hook `no-commit-to-branch`)
- Format : `type(scope): description` — ex: `feat(api): add metrics endpoint`

## Variables d'environnement

| Variable        | Local (docker-compose)  | K8s (Traefik)         |
| --------------- | ----------------------- | --------------------- |
| `VITE_API_URL`  | `http://localhost:8000` | `""` (URLs relatives) |
| `SECRET_KEY`    | `.env`                  | K8s Secret            |
| `PROJECTS_PATH` | `/home/.../projects`    | K8s ConfigMap         |

## Flux réseau K8s

```
Browser → Traefik
  PathPrefix(/api)  → docker-overview-api:8000    (FastAPI)
  PathPrefix(/)     → docker-overview-frontend:3000 (serve@14)
```
