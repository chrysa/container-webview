node-upgradable-package: ## check outdated packages
	@docker compose run --rm -it frontend npm outdated

node-install: ## install frontend dependencies
	@docker compose run --rm frontend npm install --legacy-peer-deps
