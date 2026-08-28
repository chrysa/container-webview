docker-build: ## build all images (no cache)
	@docker compose build --pull --no-cache --compress --force-rm

docker-connect-api: ## open a shell in the api container
	@docker compose run --rm -it --entrypoint sh api

docker-stop: ## stop all services
	@docker compose stop

docker-up: ## start all services
	@docker compose up

docker-up-detach: ## start all services in background
	@docker compose up --detach

docker-down: ## stop and remove all containers
	@docker compose down

docker-logs: ## follow logs for all services
	@docker compose logs -f

docker-ps: ## list running containers
	@docker compose ps
