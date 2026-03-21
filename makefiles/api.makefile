api-shell: ## Shell dans le container API dev
	@docker compose --profile dev exec api-dev sh

api-test: ## Lancer les tests API
	@docker compose --profile dev run --rm api-dev python -m pytest -v

api-lint: ## Linter le code Python (ruff ou flake8)
	@docker compose --profile dev run --rm api-dev python -m flake8 app/ || true

api-install: ## Installer les dépendances Python
	@docker compose --profile dev run --rm api-dev pip install -r requirements.txt
