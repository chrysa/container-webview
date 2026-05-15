prod-up: ## Start in production mode (port 8080)
	@docker compose up --detach --wait

prod-down: ## Stop production services
	@docker compose down

dev-up: ## Start development mode (Vite 5173 + API 8000)
	@docker compose --profile dev up --no-log-prefix api-dev frontend-dev

dev-api: ## Start API only in dev mode
	@docker compose --profile dev up --no-log-prefix api-dev

dev-front: ## Start frontend only in dev mode
	@docker compose --profile dev up --no-log-prefix frontend-dev

shell-api: ## Shell dans le container API (dev)
	@docker compose --profile dev exec api-dev sh

shell-front: ## Shell dans le container frontend (dev)
	@docker compose --profile dev exec frontend-dev sh
