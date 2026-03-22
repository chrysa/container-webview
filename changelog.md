# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [Unreleased]

### Changed

- Conformité ruff/mypy complète (zéro `# noqa`, zéro `# type: ignore`) :
  - Tous les imports multi-symboles (`from x import a, b`) éclatés en lignes séparées (`force-single-line`)
  - Suppression de tous les `return` vides et `return None` — patron *single return point* avec variable résultat
  - `auth_service` : suppression du `# type: ignore[import]` ; `pyproject.toml` couvre déjà `ignore_missing_imports`
  - `project_manager` : annotations de type sur tous les paramètres `raw` (ANN001) ; types de retour précisés
  - `alerts_service` / `metrics_service` : bloc `TYPE_CHECKING` + annotation `container: Container`
  - Tests : déplacement de tous les imports hors des méthodes de test ; suppression des imports inutilisés
  - Tests : correction des noms de champs Pydantic (`ServiceMetrics`, `Alert`) ; ajout des champs requis manquants

### Added

- Backend FastAPI complet avec architecture service-class
  - `ProjectManager` : découverte et parsing des projets Compose
  - `DockerClientService` : abstraction du SDK Docker
  - `LifecycleService` : start / stop / restart / pause / unpause
  - `MetricsService` : métriques CPU/RAM/réseau en temps réel
  - `AlertsService` : détection des anomalies de conteneurs
  - `TopologyService` : génération du graphe de topologie
  - `AuthService` : authentification locale + LDAP
- Routeurs HTTP FastAPI (contrôleurs minces)
  - `auth`, `projects`, `topology`, `lifecycle`, `metrics`, `alerts`, `logs`
- JWT Bearer authentication via `python-jose`
- Infrastructure de tests : pytest 8.2 + pytest-asyncio + coverage ≥ 80 %
  - Tests unitaires pour tous les services
  - Tests d'intégration pour tous les routeurs
- Migration vers `pyproject.toml` (dépendances, ruff, mypy, pytest, coverage)
- Configuration `pre-commit` complète :
  - ruff (lint + format), mypy, hadolint, prettier, eslint, yamllint, markdownlint, gitleaks
- Stage `test` dans le Dockerfile + service `api-test` dans docker-compose.yml
- `makefiles/tests.makefile` : cibles `api-tests`, `api-tests-cov`, `api-lint`, `api-format`, `api-typecheck`
- Fichiers de config linters : `.config/.hadolint.yaml`, `.config/.yamllint.yaml`, `.config/.markdownlint.yaml`

### Changed

- `requirements.txt` remplacé par `pyproject.toml`
- README entièrement réécrit avec architecture, endpoints, config et guide de démarrage rapide

## [0.0.2] - 2023-05-10

### Added

- docker embed

## [0.0.1] - 2023-05-10

- initial release

<!-- Links -->

<!-- Versions -->

[0.0.1]: https://github.com/chrysa/container-webview/releases/tag/v0.0.1
[0.0.2]: https://github.com/chrysa/container-webview/compare/v0.0.1...v0.0.2
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html
[unreleased]: https://github.com/chrysa/container-webview/compare/v0.0.2...HEAD
