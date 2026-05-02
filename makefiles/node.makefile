<<<<<<< HEAD
node-install: ## Installer les dépendances npm
	@docker compose --profile dev run --rm frontend-dev npm install
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
node-upgradable-package: ## check outdated packages
	@docker compose run --rm -it docker-overview-webui npm run outdated
=======
node-upgradable-package: ## check outdated packages
	@docker compose run --rm -it frontend npm outdated
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")

<<<<<<< HEAD
node-build: ## Compiler le frontend (production)
	@docker compose --profile dev run --rm frontend-dev npm run build

node-lint: ## Linter le code frontend
	@docker compose --profile dev run --rm frontend-dev npm run lint

node-test: ## Lancer les tests unitaires Vitest (containerisé)
	@docker compose --profile test run --rm frontend-test npm run test

node-test-cov: ## Lancer les tests Vitest avec couverture (containerisé)
	@docker compose --profile test run --rm frontend-test npm run test:coverage

node-outdated: ## Vérifier les dépendances npm obsolètes
	@docker compose --profile dev run --rm frontend-dev npm outdated

node-clean: ## Supprimer node_modules et dist
	@rm -rf code/node_modules code/dist
	@docker volume rm docker-overview-node-modules 2>/dev/null || true
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
node-dev-upgradable-package: ## check outdated packages on dev
	@docker compose run --rm -it docker-overview-webui-dev npm run outdated
=======
node-install: ## install frontend dependencies
	@docker compose run --rm frontend npm install --legacy-peer-deps
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
