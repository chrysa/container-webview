prod-up: ## Démarrer en production (port 8080)
	@docker compose up --detach --wait

prod-down: ## Arrêter la production
	@docker compose down

dev-up: ## Démarrer en développement (Vite 5173 + API 8000)
	@docker compose --profile dev up --no-log-prefix api-dev frontend-dev

dev-api: ## Démarrer uniquement l'API en dev
	@docker compose --profile dev up --no-log-prefix api-dev

dev-front: ## Démarrer uniquement le frontend en dev
	@docker compose --profile dev up --no-log-prefix frontend-dev

shell-api: ## Shell dans le container API (dev)
	@docker compose --profile dev exec api-dev sh

shell-front: ## Shell dans le container frontend (dev)
	@docker compose --profile dev exec frontend-dev sh
