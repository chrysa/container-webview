app-build: ## build frontend for production
	@docker compose run --rm frontend npm run build

app-dev: ## launch full stack in development mode
	@docker compose up --build
