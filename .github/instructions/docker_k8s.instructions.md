______________________________________________________________________

## applyTo: "{Dockerfile,api/Dockerfile,docker-compose.yml,k8s/\*\*/\*}"

# Docker & Kubernetes Guidelines

## Dockerfiles

### Frontend (`Dockerfile` racine) — multi-stage

```dockerfile
# Stage 1 — deps : npm install uniquement (cache layer optimisé)
FROM node:22-slim AS deps
WORKDIR /app
COPY code/package.json ./
RUN npm install --legacy-peer-deps

# Stage 2 — build : compile Vite (VITE_API_URL baked at build time)
FROM deps AS build
ARG VITE_API_URL=    # vide par défaut = URLs relatives pour K8s/Traefik
ENV VITE_API_URL=${VITE_API_URL}
COPY code/ .
RUN npm run build

# Stage 3 — production : serve@14 léger (pas de nginx)
FROM node:22-slim AS production
RUN npm install -g serve@14
COPY --from=build /app/dist /app/dist
EXPOSE 3000
CMD ["serve", "-s", "/app/dist", "-l", "3000"]
```

**Règles** :

- `VITE_API_URL=""` (vide) en production K8s — Traefik proxifie `/api`
- `VITE_API_URL=http://localhost:8000` en docker-compose local
- Toujours utiliser `node:22-slim`, jamais `node:latest`
- `--legacy-peer-deps` requis pour la compatibilité lucide-react / React 19

### API (`api/Dockerfile`)

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libldap2-dev libsasl2-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Règles** :

- Toujours `python:3.12-slim`, jamais `python:latest`
- `--no-install-recommends` + nettoyage `apt` dans la même layer
- `--no-cache-dir` pour pip

### hadolint

Config dans `config-tools/.hadolint.yaml`. Règles ignorées :

- `DL3008`, `DL3013`, `DL3018`, `DL3031`, `DL3033` — version pinning apt/pip (géré par requirements.txt)
- `DL4006` — set -o pipefail (géré globalement)
- `SC2086` — double quote (cas légitimes documentés)

## docker-compose.yml

4 services :

```yaml
services:
  api:          # production-like, port 8000:8000
  frontend:     # production build, port 3000:3000, VITE_API_URL=http://localhost:8000
  api-dev:      # profile: dev, hot-reload uvicorn --reload
  frontend-dev: # profile: dev, hot-reload vite dev server
```

**Règles** :

- Le socket Docker est monté en bind : `/var/run/docker.sock:/var/run/docker.sock`
- Le répertoire projets est monté depuis `.env` → `PROJECTS_PATH`
- `frontend` dépend de `api` avec healthcheck `curl -f http://localhost:8000/api`
- **NEVER** lancer docker-compose directement — utiliser `make prod-up` / `make dev-up`

## Kubernetes — `k8s/`

### Structure

```
k8s/
├── kustomization.yaml   ← point d'entrée kubectl kustomize
├── namespace.yaml
├── configmap.yaml       ← PROJECTS_PATH, ADMIN_USERNAME
├── secret.yaml          ← exclu de kustomize, appliquer manuellement
├── api/
│   ├── pvc.yaml         ← 1Gi RWX pour /projects
│   ├── deployment.yaml  ← docker.sock hostPath, PVC, probes
│   └── service.yaml     ← ClusterIP port 8000
├── frontend/
│   ├── deployment.yaml  ← 2 réplicas, runAsNonRoot
│   └── service.yaml     ← ClusterIP port 3000
└── ingress/
    ├── middleware.yaml   ← secure-headers, https-redirect
    └── ingressroute.yaml ← Traefik CRD traefik.io/v1alpha1
```

### Traefik IngressRoute — règles de priorité

```yaml
routes:
  - match: Host(`...`) && PathPrefix(`/api`)
    priority: 20          # API en priorité haute
    services: [docker-overview-api:8000]
  - match: Host(`...`)
    priority: 10          # SPA catch-all
    services: [docker-overview-frontend:3000]
```

- Les WebSocket (`/api/.../logs`) passent automatiquement via Traefik (upgrade transparent)
- TLS : configurer `certResolver` (cert-manager) ou `secretName` selon l'environnement

### Secrets K8s

```bash
# Appliquer le secret manuellement (JAMAIS via kustomize / CI)
kubectl apply -f k8s/secret.yaml
```

Le fichier `k8s/secret.yaml` est exclu de `kustomization.yaml`. Ne jamais le committer avec de vraies valeurs.

### Images en CI/CD

Les images sont stockées dans **GitHub Container Registry** :

```
ghcr.io/chrysa/container-webview/api:<SHA>
ghcr.io/chrysa/container-webview/frontend:<SHA>
```

`kustomization.yaml` contient les références `newName` / `newTag` mises à jour automatiquement par le workflow `cd.yml`.

## Makefile — commandes disponibles

| Commande            | Description                               |
| ------------------- | ----------------------------------------- |
| `make prod-up`      | Lance api + frontend en mode production   |
| `make prod-down`    | Arrête tous les services                  |
| `make dev-up`       | Lance api-dev + frontend-dev (hot-reload) |
| `make docker-build` | Build les deux images Docker              |
| `make node-build`   | Build le frontend (`npm run build`)       |
| `make node-lint`    | Lint TypeScript (`npm run lint`)          |
| `make api-lint`     | Lint Python (`ruff check api/`)           |
| `make api-install`  | Install dépendances Python                |
