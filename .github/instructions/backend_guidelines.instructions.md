---
applyTo: "api/**/*"
---

# Backend Guidelines — FastAPI + Python 3.12

## Principes fondamentaux

### 1. Typage strict — zéro `Any`

- Toutes les fonctions ont des annotations de type complètes (`-> None`, `-> str`, etc.)
- Pas de `Any` sauf exception documentée avec un commentaire `# type: ignore — raison`
- `ruff` est la référence pour le format et le lint (remplace black + flake8 + isort)
- Modèles Pydantic pour toutes les entrées/sorties HTTP

### 2. Architecture — séparation des responsabilités

```
api/app/
├── routers/      # Couche présentation
│   ├── auth.py           # POST /api/auth/login, GET /api/auth/check
│   ├── projects.py       # GET /api/projects, GET /api/projects/{id}
│   ├── topology.py       # GET /api/projects/{id}/topology
│   ├── lifecycle.py      # POST /api/projects/{id}/services/{name}/{action}
│   ├── logs.py           # WS  /api/projects/{id}/services/{name}/logs
│   ├── metrics.py        # GET /api/projects/{id}/metrics
│   └── alerts.py         # GET /api/projects/{id}/alerts
├── services/     # Couche application
│   ├── docker_client.py  # Docker SDK — get_docker_client(), get_container_for_service()
│   └── project_manager.py # YAML parsing — load_project(), list_projects()
├── config.py     # Settings (pydantic-settings) — lecture .env
├── security.py   # JWT — create_access_token(), verify_token(), get_current_user()
└── main.py       # FastAPI app, CORS, include_router
```

**Règle absolue** : Pas de logique métier dans les routers. Les routers délèguent aux services.

```python
# ✅ Correct
@router.get("/projects")
async def list_projects(current_user: str = Depends(get_current_user)) -> list[Project]:
    return project_manager.list_projects()

# ❌ Interdit — logique métier dans le router
@router.get("/projects")
async def list_projects():
    path = os.environ["PROJECTS_PATH"]  # NON — dans config.py
    return [parse_yaml(f) for f in os.listdir(path)]  # NON — dans project_manager
```

### 3. Modèles Pydantic — toutes les I/O

```python
from pydantic import BaseModel

class Project(BaseModel):
    id: str
    name: str
    path: str
    services: list[str]

# Réponses typées dans les annotations du router
@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    ...
```

### 4. Sécurité

- `get_current_user` via `Depends()` sur tous les endpoints protégés
- Token JWT : `Authorization: Bearer <token>` (header standard)
- WebSocket logs : token via query param `?token=` (seule exception)
- Secrets dans `config.py` via `pydantic-settings` → lus depuis `.env` ou variables d'environnement

```python
# security.py
from app.config import get_settings

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    settings = get_settings()
    return verify_token(token, settings.SECRET_KEY)
```

### 5. Configuration — `config.py`

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    PROJECTS_PATH: str = "/projects"
    # LDAP optionnel
    LDAP_SERVER: str = ""

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 6. WebSocket — streaming de logs

- Endpoint : `WS /api/projects/{project_id}/services/{service_name}/logs`
- Auth via query param `?token=<jwt>`
- Utiliser `docker_client.get_container_for_service()` pour cibler le bon conteneur
- Envoyer les logs ligne par ligne avec `await websocket.send_text(line)`
- Gérer `WebSocketDisconnect` proprement (sans raise)

### 7. Docker SDK — `services/docker_client.py`

```python
import docker
from docker.client import DockerClient

def get_docker_client() -> DockerClient:
    return docker.from_env()

def get_container_for_service(project_id: str, service_name: str) -> docker.models.containers.Container:
    client = get_docker_client()
    # Convention docker-compose : {project}_{service}_{replica}
    containers = client.containers.list(filters={"name": f"{project_id}_{service_name}"})
    if not containers:
        raise ValueError(f"No container found for {project_id}/{service_name}")
    return containers[0]
```

### 8. CORS — `main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # dev seulement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

En production (K8s + Traefik), le frontend et l'API partagent le même domaine — CORS non nécessaire.

## Dépendances (`requirements.txt`)

```
fastapi
uvicorn[standard]
docker
pyyaml
python-jose[cryptography]
passlib[bcrypt]
python-multipart
websockets
httpx
python-ldap
pydantic-settings
```
