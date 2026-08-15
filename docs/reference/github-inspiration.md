# Deep-dive — `chrysa/container-webview` (Docker Overview WebUI)

**But (1 phrase) :** Interface web (FastAPI + docker SDK sur `/var/run/docker.sock` + frontend
React/Vite) pour lister, visualiser (topologie, métriques temps réel, alertes) et piloter le cycle
de vie (start/stop/restart/pause) des projets Docker Compose, avec auth JWT/local/LDAP.

**Stack observée :** `api/app` = FastAPI 0.111, `docker==7.0.0` (`docker.from_env()`), pydantic-settings,
python-jose (JWT), python-ldap, websockets ; routers `projects/topology/metrics/alerts/logs/lifecycle/auth` ;
services (`docker_client`, `metrics_service`, `alerts_service`, `topology_service`, ...).
Frontend `code/src` = React 18 + react-query + axios + react-router + bootstrap. Licence repo = **MIT**.

Le projet appartient à une catégorie très fournie en OSS de référence (gestion/visualisation Docker),
donc de vrais équivalents existent — voici les 5 les plus exploitables. Toutes les sources retenues
sont **permissives (copiables)** : MIT / Apache-2.0 / zlib. Aucune source copyleft/restrictive dans la
sélection.

---

## docker/docker-py

- **owner/repo :** docker/docker-py
- **stars :** ~7.2k
- **activité :** actif (main, ~3 463 commits ; issues/PR ouverts)
- **licence :** **Apache-2.0** (permissive — copiable, garder l'attribution NOTICE)
- **fichier/module du pattern :** `docker/models/containers.py` → `Container.stats(stream=True, decode=True)` et `.logs(stream=True)`
- **mécanisme réel :** c'est la SDK que le projet utilise déjà (`docker.from_env()`). Le point clé non
  encore exploité : le **streaming** natif de stats/logs (générateur) plutôt qu'un snapshot ponctuel.
  `stats()` renvoie un flux JSON décodé par le daemon ; chaque item contient `cpu_stats`/`precpu_stats`,
  `memory_stats`, `networks`, `blkio_stats` — exactement les champs déjà parsés dans `metrics_service.py`.
- **snippet portable :**
  ```python
  import docker
  client = docker.from_env()
  container = client.containers.get(container_id)
  # snapshot (déjà fait) : stream=False
  # flux temps réel (à câbler sur un WebSocket) :
  for frame in container.stats(stream=True, decode=True):
      cpu = frame["cpu_stats"]; pre = frame["precpu_stats"]
      cpu_delta = cpu["cpu_usage"]["total_usage"] - pre["cpu_usage"]["total_usage"]
      sys_delta = cpu["system_cpu_usage"] - pre.get("system_cpu_usage", 0)
      ncpu = cpu.get("online_cpus") or len(cpu["cpu_usage"].get("percpu_usage") or [1])
      pct = (cpu_delta / sys_delta) * ncpu * 100.0 if sys_delta > 0 else 0.0
      yield {"cpu_percent": round(pct, 2)}
  ```
- **intégration ici :** dans un nouveau `routers/metrics.py` WebSocket (ou SSE) endpoint, itérer
  `container.stats(stream=True, decode=True)` dans un thread executor (l'appel est bloquant), et pousser
  chaque frame. `websockets` est déjà en dépendance. Réutiliser le parsing existant de `MetricsService`.
- **gotchas :** `stats(stream=True)` est **bloquant** → l'exécuter via `run_in_executor`/thread, jamais
  dans la boucle asyncio directe. `precpu_stats` est vide au 1er frame (pct=0). `system_cpu_usage` absent
  sur Windows/certains runtimes → garde le `if sys_delta > 0`.

---

## amir20/dozzle

- **owner/repo :** amir20/dozzle
- **stars :** ~14.1k
- **activité :** très actif (main, ~6 500 commits)
- **licence :** **MIT** (permissive — copiable)
- **fichier/module du pattern :** backend Go `internal/docker` + streaming logs SSE ; mais l'intérêt pour
  ce projet Python est **l'architecture** : « no persistence, live-only », socket monté en `:ro`.
- **mécanisme réel :** Dozzle ne stocke aucun log ; il ouvre un flux direct daemon→navigateur (SSE),
  négocie automatiquement la version d'API Docker (Engine 19.03+/API 1.40+), et multiplexe plusieurs
  containers. Modèle « stateless viewer » : la source de vérité reste le daemon.
- **snippet portable (équivalent Python du log-follow) :**
  ```python
  # routers/logs.py — suivre les logs d'un service en SSE
  from fastapi.responses import StreamingResponse
  def _follow(container):
      for chunk in container.logs(stream=True, follow=True, tail=200):
          yield f"data: {chunk.decode(errors='replace')}\n\n"
  # return StreamingResponse(_follow(c), media_type="text/event-stream")
  ```
- **intégration ici :** le projet a déjà un `routers/logs.py` — s'aligner sur le modèle Dozzle : SSE
  plutôt que polling, `tail` borné, backpressure gérée par le générateur. Reprendre l'idée de
  **négociation d'API auto** (`docker.from_env()` la fait déjà) et le montage socket `:ro` (déjà fait
  dans `docker-compose.yml`).
- **gotchas :** SSE derrière un proxy nécessite `X-Accel-Buffering: no` (nginx) sinon les frames sont
  bufferisés. `logs(stream=True)` bloquant → thread executor. Attention aux logs binaires : `decode(errors=...)`.

---

## louislam/dockge

- **owner/repo :** louislam/dockge
- **stars :** ~24.1k
- **activité :** actif (main)
- **licence :** **MIT** (permissive — copiable)
- **fichier/module du pattern :** gestion de stacks Compose « file-based », `/opt/stacks/<name>/compose.yaml`,
  fonction *Scan Stacks Folder* + conversion `docker run … → compose.yaml`.
- **mécanisme réel :** Dockge **ne kidnappe pas** les fichiers compose : ils restent sur disque, éditables
  et pilotables via `docker compose` normal. La découverte de projets = scan d'un dossier racine
  (un sous-dossier = une stack). Lifecycle = wrappers sur `docker compose up/down/restart`.
- **snippet portable (découverte de projets, à comparer avec `project_manager.py`) :**
  ```python
  from pathlib import Path
  import yaml
  def discover_stacks(root: Path):
      for compose in list(root.glob("*/compose.yaml")) + list(root.glob("*/docker-compose.y*ml")):
          data = yaml.safe_load(compose.read_text()) or {}
          yield {"id": compose.parent.name, "services": list((data.get("services") or {}).keys())}
  ```
- **intégration ici :** valider le `project_manager.py` contre ce modèle (dossier racine `PROJECTS_PATH`,
  un dossier = un projet). Idées à porter : *scan folder* explicite, support des deux noms de fichier
  (`compose.yaml` ET `docker-compose.yml`), et un **éditeur** de compose côté frontend (React) avec
  validation YAML avant écriture.
- **gotchas :** ne jamais réécrire/reformater le compose de l'utilisateur (perte de commentaires/anchors
  YAML avec `yaml.safe_dump`). Le montage `PROJECTS_PATH` est `:ro` ici → l'édition nécessiterait `:rw`
  (décision de sécurité explicite). Convention `/opt/stacks` de Dockge ≠ la vôtre : garder configurable.

---

## portainer/portainer

- **owner/repo :** portainer/portainer
- **stars :** ~38.3k
- **activité :** très actif (référence de la catégorie)
- **licence :** **zlib** (permissive — copiable, garder la notice ; PAS copyleft)
- **fichier/module du pattern :** modèle d'auth multi-backend (interne + LDAP + OAuth) et RBAC ;
  API REST versionnée + WebSocket exec/attach.
- **mécanisme réel :** Portainer expose un backend d'authentification pluggable (local users, LDAP/AD,
  OAuth) avec JWT, et une couche d'autorisations par ressource. Le projet ici a déjà JWT + local + LDAP
  (`auth_service.py`, `security.py`, `python-ldap`) — Portainer est la **référence de robustesse** pour ce
  volet (verrouillage compte, expiration token, rôles).
- **snippet portable (garde JWT FastAPI, déjà partiellement présent) :**
  ```python
  from datetime import datetime, timedelta, timezone
  from jose import jwt
  def make_token(sub: str, secret: str, minutes: int = 60) -> str:
      now = datetime.now(timezone.utc)
      claims = {"sub": sub, "iat": now, "exp": now + timedelta(minutes=minutes)}
      return jwt.encode(claims, secret, algorithm="HS256")
  ```
- **intégration ici :** ne rien copier de code (zlib copiable mais inutile de dupliquer) — s'inspirer du
  **modèle de rôles** et de la séparation « authentification (qui) vs autorisation (quoi) ». Ajouter, comme
  Portainer, un fallback ordonné LDAP→local et une politique d'expiration/refresh de JWT.
- **gotchas :** zlib impose de conserver la notice si on copie du code (rare ici, backend Go).
  L'API Portainer est large — s'en inspirer sélectivement, ne pas sur-scoper.

---

## getwud/whats-up-docker (WUD)

- **owner/repo :** getwud/whats-up-docker (aussi `fmartinou/whats-up-docker`)
- **stars :** ~3.7k
- **activité :** actif
- **licence :** **MIT** (permissive — copiable)
- **fichier/module du pattern :** *watchers* + *triggers* : détection d'état/mises à jour de containers et
  déclenchement d'actions (webhook, notification).
- **mécanisme réel :** WUD scanne périodiquement les containers, compare leur état/version (semver) à une
  cible, et émet des événements vers des triggers. Modèle « watcher → registry → trigger » directement
  transposable au module **alerts** de ce projet (`alerts_service.py` détecte exited/restarting/unhealthy).
- **snippet portable (détection d'anomalies, style `alerts_service`) :**
  ```python
  ANOMALOUS = {"exited", "restarting", "dead", "paused"}
  def detect_alerts(containers):
      for c in containers:
          health = (c.attrs.get("State", {}).get("Health") or {}).get("Status")
          if c.status in ANOMALOUS or health == "unhealthy":
              yield {"container": c.name, "status": c.status, "health": health}
  ```
- **intégration ici :** enrichir `alerts_service.py` avec un système de **triggers** (webhook/Notion/email)
  déclenché sur transition d'état, et un scan périodique (APScheduler/asyncio task) plutôt qu'à la demande.
  Reprendre l'idée de seuils configurables (nb de restarts avant alerte).
- **gotchas :** le scan périodique + `containers.list(all=True)` est coûteux sur beaucoup de containers →
  cache court + intervalle configurable. `State.Health` absent si pas de `HEALTHCHECK` → gérer le `None`.

---

## Synthèse

- Catégorie richement pourvue en OSS de référence → sélection de 5 pertinents, tous **permissifs (copiables)**.
- **Priorité d'intégration :** (1) streaming stats/logs via `docker-py` + WebSocket/SSE (métriques/logs
  temps réel réels, cf. mémoire « no-demo-mode, prefer realtime ») ; (2) triggers d'alertes façon WUD ;
  (3) découverte/édition de stacks façon Dockge.
- **Licences :** toutes permissives (MIT ×3, Apache-2.0, zlib). Aucune source copyleft/restrictive à
  réimplémenter. Garder les notices Apache/zlib uniquement si copie littérale de code (peu probable, back Go).
