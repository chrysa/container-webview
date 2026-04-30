docker-build: ## Construire toutes les images (production)
	@docker compose build --pull --no-cache

<<<<<<< HEAD
docker-build-dev: ## Construire les images de développement
	@docker compose --profile dev build --pull
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
docker-connect-dev: ## connect-to-dev-server
	@docker compose run --rm -it --entrypoint sh docker-overview-webui-dev
=======
docker-connect-api: ## open a shell in the api container
	@docker compose run --rm -it --entrypoint sh api
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

docker-stop: ## Arrêter tous les services
	@docker compose --profile dev stop

<<<<<<< HEAD
docker-down: ## Arrêter et supprimer les containers
	@docker compose --profile dev down
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
docker-up: ## up service
	@docker compose up docker-overview-webui
=======
docker-up: ## up service
	@docker compose up
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

<<<<<<< HEAD
docker-ps: ## Lister les containers
	@docker compose --profile dev ps

docker-logs: ## Voir les logs (usage: make docker-logs SERVICE=api)
	@docker compose logs --follow --tail=100 $(SERVICE)

docker-clean: ## Supprimer images + volumes orphelins
	@docker compose down --volumes --remove-orphans
	@docker image prune -f
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
docker-up-detach: ## up service and detach
	@docker compose up --detach docker-overview-webui
=======
docker-up-detach: ## up service and detach
	@docker compose up --detach
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
