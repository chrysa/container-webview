docker-build: ## Build all images (production)
	@docker compose build --pull --no-cache

docker-build-dev: ## Build development images
	@docker compose --profile dev build --pull

docker-stop: ## Stop all services
	@docker compose --profile dev stop

docker-down: ## Stop and remove containers
	@docker compose --profile dev down

docker-ps: ## List running containers
	@docker compose --profile dev ps

docker-logs: ## Tail service logs (usage: make docker-logs SERVICE=api)
	@docker compose logs --follow --tail=100 $(SERVICE)

docker-clean: ## Remove images and orphan volumes
	@docker compose down --volumes --remove-orphans
	@docker image prune -f
