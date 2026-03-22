docker-build: ## build image
	@docker compose build --pull --no-cache --compress --force-rm

docker-connect-api: ## open a shell in the api container
	@docker compose run --rm -it --entrypoint sh api

docker-stop: ## stop services
	@docker compose stop

docker-up: ## up service
	@docker compose up

docker-up-detach: ## up service and detach
	@docker compose up --detach
