node-install: ## Installer les dépendances npm
	@docker compose --profile dev run --rm frontend-dev npm install

node-build: ## Compiler le frontend (production)
	@docker compose --profile dev run --rm frontend-dev npm run build

node-lint: ## Linter le code frontend
	@docker compose --profile dev run --rm frontend-dev npm run lint

node-outdated: ## Vérifier les dépendances npm obsolètes
	@docker compose --profile dev run --rm frontend-dev npm outdated

node-clean: ## Supprimer node_modules et dist
	@rm -rf code/node_modules code/dist
	@docker volume rm docker-overview-node-modules 2>/dev/null || true
