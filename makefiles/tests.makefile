API_SERVICE ?= api-test

api-tests: ## run backend unit tests
	@docker compose --profile test run --rm $(API_SERVICE)

api-tests-cov: ## run backend tests with terminal coverage report
	@docker compose --profile test run --rm $(API_SERVICE) python -m pytest --cov=app --cov-report=term-missing

api-tests-html: ## run backend tests with HTML coverage report
	@docker compose --profile test run --rm $(API_SERVICE) python -m pytest --cov=app --cov-report=html --cov-report=term-missing

api-tests-xml: ## run backend tests with XML coverage report (CI)
	@docker compose --profile test run --rm $(API_SERVICE) python -m pytest --cov=app --cov-report=xml --cov-report=term-missing

api-lint: ## run ruff linter on backend code
	@docker compose run --rm api python -m ruff check app/

api-lint-fix: ## run ruff linter with auto-fix on backend code
	@docker compose run --rm api python -m ruff check --fix app/

api-format: ## run ruff formatter on backend code
	@docker compose run --rm api python -m ruff format app/

api-typecheck: ## run mypy type checking on backend code
	@docker compose run --rm api python -m mypy app/

api-quality: api-lint api-format api-typecheck api-tests ## run full quality checks (lint + format + type + tests)
