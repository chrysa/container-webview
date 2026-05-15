node-install: ## Install npm dependencies
	@docker compose --profile dev run --rm frontend-dev npm install

node-build: ## Build frontend for production
	@docker compose --profile dev run --rm frontend-dev npm run build

node-lint: ## Lint frontend code
	@docker compose --profile dev run --rm frontend-dev npm run lint

node-test: ## Run Vitest unit tests (containerised)
	@docker compose --profile test run --rm frontend-test npm run test

node-test-cov: ## Run Vitest tests with coverage (containerised)
	@docker compose --profile test run --rm frontend-test npm run test:coverage

node-outdated: ## Check for outdated npm dependencies
	@docker compose --profile dev run --rm frontend-dev npm outdated

node-clean: ## Remove node_modules and dist
	@rm -rf code/node_modules code/dist
	@docker volume rm docker-overview-node-modules 2>/dev/null || true
