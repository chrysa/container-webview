docker-build: ## build image
	@docker compose build --pull --no-cache --compress --force-rm

docker-connect-dev: ## connect-to-dev-server
	@docker compose run --rm -it --entrypoint sh docker-overview-webui-dev

docker-stop: ## stop services
	@docker compose stop

docker-up: ## up service
	@docker compose up docker-overview-webui

docker-up-detach: ## up service and detach
	@docker compose up --detach docker-overview-webui
