api-shell: ## Open shell in API dev container
	@docker compose --profile dev exec api-dev sh

api-test: ## Run API tests
	@docker compose --profile dev run --rm api-dev python -m pytest -v

api-lint: ## Lint Python code (ruff or flake8)
	@docker compose --profile dev run --rm api-dev python -m flake8 app/ || true

api-install: ## Install Python dependencies
	@docker compose --profile dev run --rm api-dev pip install -r requirements.txt
