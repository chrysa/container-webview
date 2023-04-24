app-build: app-install-deps ## build application
	@docker compose run --rm -it docker-overview-webui-dev npm run build

app-install-deps: ## install proect dependencies locally
	@docker compose run --rm docker-overview-webui-dev npm run install-deps

app-dev: app-install-deps ## launch as dev
	@docker compose up --no-log-prefix docker-overview-webui-dev
