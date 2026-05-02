<<<<<<< HEAD
prod-up: ## Démarrer en production (port 8080)
	@docker compose up --detach --wait
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
app-build: app-install-deps ## build application
	@docker compose run --rm -it docker-overview-webui-dev npm run build
=======
app-build: ## build frontend for production
	@docker compose run --rm frontend npm run build
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

<<<<<<< HEAD
prod-down: ## Arrêter la production
	@docker compose down

dev-up: ## Démarrer en développement (Vite 5173 + API 8000)
	@docker compose --profile dev up --no-log-prefix api-dev frontend-dev

dev-api: ## Démarrer uniquement l'API en dev
	@docker compose --profile dev up --no-log-prefix api-dev

dev-front: ## Démarrer uniquement le frontend en dev
	@docker compose --profile dev up --no-log-prefix frontend-dev

shell-api: ## Shell dans le container API (dev)
	@docker compose --profile dev exec api-dev sh

shell-front: ## Shell dans le container frontend (dev)
	@docker compose --profile dev exec frontend-dev sh
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
app-install-deps: ## install proect dependencies locally
	@docker compose run --rm docker-overview-webui-dev npm run install-deps

app-dev: app-install-deps ## launch as dev
	@docker compose up --no-log-prefix docker-overview-webui-dev
=======
app-dev: ## launch full stack in development mode
	@docker compose up --build
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
