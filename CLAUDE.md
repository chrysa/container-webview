# container-webview — Claude context

## What does this project do?

Web GUI for managing Docker Compose projects. Two components:
- **API** (`api/`): FastAPI backend that queries the Docker daemon, parses docker-compose YAMLs, and maps service dependency graphs
- **Frontend** (`code/`): React 18 SPA that renders the graph and provides service controls

Target features (in progress):
- Visualize docker-compose service dependency graph
- Create/update services from the GUI
- Start/stop/restart containers
- Export docker-compose YAML

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI 0.111 + Uvicorn, Python 3.12+ |
| Docker client | docker-py 7.0 |
| Auth | python-jose (JWT) |
| Config parsing | PyYAML 6 |
| Frontend | React 18 + Create React App |
| Container | Docker multi-stage, Traefik |
| CI | GitHub Actions |
| Pre-commit | pre-commit hooks |
| Versioning | GitVersion |

## Repository structure

```
api/
  app/            FastAPI application (routers, models, services)
  pyproject.toml  Project metadata (name: docker-overview-api)
  Dockerfile
code/
  src/            React components
  public/
  package.json    (name: docker-overview)
config-tools/     Shared CI/config helpers
makefiles/        Modular Makefile includes
scripts/          Helper scripts
docker-compose.yml
Makefile
GitVersion.yml
.pre-commit-config.yaml
```

## Development workflow

```bash
make dev          # docker-compose up in dev mode
make up           # production up
make down         # stop containers
make logs         # show logs
make pre-commit   # run pre-commit hooks
make scan         # Trivy vulnerability scan
```

API standalone:
```bash
cd api && uvicorn app.main:app --reload --port 8000
```

Frontend standalone:
```bash
cd code && npm start   # CRA dev server (port 3000)
npm run build
```

## Key conventions

- FastAPI routers in `api/app/routers/`
- JWT auth via python-jose — `python-jose[cryptography]` dependency
- Docker socket access: container must bind-mount `/var/run/docker.sock`
- API base URL: `http://api:8000` from within Docker network
- React app uses `REACT_APP_API_URL` env var to locate the API

## Environment variables

From `.env.example`:
- `MAINTAINER_NAME`, `MAINTAINER_MAIL`
- `FQDN`, `CONTAINER_WEBVIEW_PREFIX_URL`
- `CONTAINER_WEBVIEW_CONTAINER_VERSION`
- `JWT_SECRET_KEY` — for API auth

## Notes / known issues

- CRA (`react-scripts`) is deprecated — should migrate to Vite
- `package.json` has suspicious dependencies: `build`, `run`, `start`, `npm` as runtime deps — likely misconfigured, should be devDependencies
- python-jose has known CVE (CVE-2024-33664) — consider migrating to `PyJWT` or `authlib`
- SonarCloud not configured
- The graph visualization library is not yet selected (D3.js, vis-network, or React Flow)
