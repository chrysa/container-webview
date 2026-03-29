app-build: ## build frontend for production
	@docker compose run --rm frontend npm run build

app-dev: ## launch full stack in development mode
	@docker compose up --build

app-install: ## install all dependencies (frontend + backend)
	@docker compose run --rm frontend npm install --legacy-peer-deps

app-quality: api-quality node-lint ## run full quality checks (backend + frontend)
