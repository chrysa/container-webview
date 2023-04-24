node-upgradable-package: ## check outdated packages
	@docker compose run --rm -it docker-overview-webui npm run outdated

node-dev-upgradable-package: ## check outdated packages on dev
	@docker compose run --rm -it docker-overview-webui-dev npm run outdated
