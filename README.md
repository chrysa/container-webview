# Docker Overview WebUI

Interface web pour gérer et visualiser vos projets Docker Compose — topologie interactive, métriques en temps réel, alertes et gestion du cycle de vie des services.

---

## Table des matières

- [Docker Overview WebUI](#docker-overview-webui)
  - [Table des matières](#table-des-matières)
  - [Fonctionnalités](#fonctionnalités)
  - [Architecture](#architecture)
  - [Prérequis](#prérequis)
  - [Démarrage rapide](#démarrage-rapide)
  - [Configuration](#configuration)
  - [Endpoints API](#endpoints-api)
  - [Commandes Make](#commandes-make)
  - [Tests](#tests)
  - [Roadmap](#roadmap)

---

## Fonctionnalités

- **Vue d'ensemble** — liste tous les projets Compose détectés dans le répertoire configuré
- **Topologie** — graphe interactif des services et réseaux d'un projet
- **Métriques** — CPU, mémoire et réseau en temps réel par conteneur
- **Alertes** — détection automatique des conteneurs en anomalie (exited, restarting, unhealthy)
- **Cycle de vie** — start / stop / restart / pause / unpause depuis l'interface
- **Authentification** — JWT Bearer, fallback local + LDAP optionnel

---

## Architecture

```
docker-overview-webui/
├── api/                        # Backend FastAPI (Python 3.12)
│   ├── app/
│   │   ├── config.py           # Configuration via pydantic-settings
│   │   ├── constants.py        # Constantes (StrEnum, Final)
│   │   ├── main.py             # App FastAPI + CORS + routeurs
│   │   ├── security.py         # Service JWT
│   │   ├── routers/            # Contrôleurs HTTP (minces)
│   │   │   ├── auth.py         # POST /api/auth/login, GET /api/auth/check
│   │   │   ├── projects.py     # GET /api/projects[/{id}]
│   │   │   ├── topology.py     # GET /api/projects/{id}/topology
│   │   │   ├── lifecycle.py    # POST /api/projects/{id}/services/{svc}/{action}
│   │   │   ├── metrics.py      # GET /api/projects/{id}/metrics
│   │   │   ├── alerts.py       # GET /api/alerts[/project/{id}]
│   │   │   └── logs.py         # WebSocket /api/projects/{id}/services/{svc}/logs
│   │   ├── services/           # Logique métier
│   │   │   ├── auth_service.py
│   │   │   ├── docker_client.py
│   │   │   ├── project_manager.py
│   │   │   ├── lifecycle_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── alerts_service.py
│   │   │   └── topology_service.py
│   │   └── tests/              # pytest — services + routers
│   ├── pyproject.toml          # Dépendances + ruff + mypy + pytest + coverage
│   └── Dockerfile              # Stages: base / dev / test / production
├── code/                       # Frontend React 18 + Vite + TypeScript
│   └── src/
├── docker-compose.yml          # Stack de développement
├── Makefile                    # Cibles make
└── .env.example                # Variables d'environnement de référence
```

---

## Prérequis

- Docker ≥ 24
- Docker Compose ≥ 2.20
- Make (GNU)
- Un répertoire local contenant des sous-dossiers de projets Compose

---

## Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/chrysa/container-webview.git
cd container-webview

# 2. Copier et adapter la configuration
cp .env.example .env
# Éditer .env : SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, PROJECTS_PATH

# 3. Créer un répertoire de projets (ou pointer vers le vôtre)
mkdir -p data/projects

# 4. Lancer le stack de développement
docker compose up --build

# 5. Accéder à l'interface
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/docs
```

Identifiants par défaut si non configurés : `admin` / `admin`.

---

## Configuration

Toutes les variables sont documentées dans [.env.example](.env.example).

| Variable | Défaut | Description |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | Clé de signature JWT — **à changer en production** |
| `ADMIN_USERNAME` | `admin` | Identifiant admin local |
| `ADMIN_PASSWORD` | `admin` | Mot de passe admin local — **à changer en production** |
| `PROJECTS_PATH` | `/projects` | Chemin dans le conteneur vers les projets Compose |
| `LDAP_SERVER` | _(vide)_ | URL LDAP (`ldap://host:389`) — vide = désactivé |
| `LDAP_BASE_DN` | _(vide)_ | Base DN LDAP |
| `FRONTEND_PORT` | `3000` | Port exposé pour le frontend |
| `VITE_API_URL` | `http://localhost:8000` | URL de l'API vue depuis le navigateur |

Le volume `${PROJECTS_PATH:-./data/projects}:/projects:ro` dans `docker-compose.yml` monte votre répertoire local de projets Compose.

---

## Endpoints API

Documentation interactive disponible sur `http://localhost:8000/docs` (Swagger UI).

| Méthode | Chemin | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authentification — retourne un JWT Bearer |
| `GET` | `/api/auth/check` | Valide le token courant |
| `GET` | `/api/projects` | Liste tous les projets Compose détectés |
| `GET` | `/api/projects/{id}` | Détail d'un projet |
| `GET` | `/api/projects/{id}/topology` | Graphe de topologie du projet |
| `GET` | `/api/projects/{id}/metrics` | Métriques CPU/RAM/réseau de tous les conteneurs |
| `POST` | `/api/projects/{id}/services/{svc}/start` | Démarrer un service |
| `POST` | `/api/projects/{id}/services/{svc}/stop` | Arrêter un service |
| `POST` | `/api/projects/{id}/services/{svc}/restart` | Redémarrer un service |
| `POST` | `/api/projects/{id}/services/{svc}/pause` | Mettre en pause |
| `POST` | `/api/projects/{id}/services/{svc}/unpause` | Reprendre depuis la pause |
| `GET` | `/api/alerts` | Toutes les alertes actives |
| `GET` | `/api/alerts/project/{id}` | Alertes filtrées par projet |
| `WS` | `/api/projects/{id}/services/{svc}/logs` | Logs en streaming (WebSocket) |

---

## Commandes Make

```
make docker-build           # Rebuild les images sans cache
make docker-up              # Lance le stack (foreground)
make docker-up-detach       # Lance le stack en arrière-plan
make docker-stop            # Arrête les services

make api-tests              # Lance les tests backend
make api-tests-cov          # Tests + rapport de couverture terminal
make api-tests-html         # Tests + rapport HTML (htmlcov/)
make api-lint               # Ruff linter
make api-format             # Ruff formatter
make api-typecheck          # mypy

make pre-commit             # Lance tous les hooks pre-commit
make ci-run-local           # Lance le pipeline CI localement
```

---

## Tests

Les tests backend utilisent **pytest** avec couverture ≥ 80 %.

```bash
# Lancer tous les tests (Docker)
make api-tests

# Avec rapport de couverture
make api-tests-cov

# Avec rapport HTML
make api-tests-html
```

Structure des tests :

```
api/app/tests/
├── conftest.py                  # Fixtures partagées (fake, api_client, auth_headers…)
├── test_main.py                 # Endpoint /api (ping)
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

## Roadmap

- [ ] Gestion dynamique des projets depuis le graphe
- [ ] Création/modification de services via l'interface
- [ ] Export du docker-compose (global, par service, dev/prod)
- [ ] Accès aux logs depuis l'interface (WebSocket)
- [ ] Notifications navigateur sur changement d'état des conteneurs
- [ ] Authentification multi-utilisateurs
- [ ] Extension Docker Desktop
