docker-build: ## Construire toutes les images (production)
	@docker compose build --pull --no-cache

docker-build-dev: ## Construire les images de développement
	@docker compose --profile dev build --pull

docker-stop: ## Arrêter tous les services
	@docker compose --profile dev stop

docker-down: ## Arrêter et supprimer les containers
	@docker compose --profile dev down

docker-ps: ## Lister les containers
	@docker compose --profile dev ps

docker-logs: ## Voir les logs (usage: make docker-logs SERVICE=api)
	@docker compose logs --follow --tail=100 $(SERVICE)

docker-clean: ## Supprimer images + volumes orphelins
	@docker compose down --volumes --remove-orphans
	@docker image prune -f
