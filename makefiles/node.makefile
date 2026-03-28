node-upgradable-package: ## check outdated packages
	@docker compose run --rm -it frontend npm outdated

node-install: ## install frontend dependencies
	@docker compose run --rm frontend npm install --legacy-peer-deps

node-lint: ## run eslint on frontend code
	@docker compose run --rm frontend npm run lint

node-build: ## build frontend for production
	@docker compose run --rm frontend npm run build

node-test: ## run frontend tests
	@docker compose run --rm frontend npm run test
