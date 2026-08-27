install: app-install ## install all dependencies (canonical alias)

build: app-build ## build the application (canonical alias)

dev: app-dev ## run the full stack in development mode (canonical alias)

lint: api-lint node-lint ## lint backend + frontend (canonical alias)

format: api-format ## format the codebase (canonical alias)

typecheck: api-typecheck ## run static type checks (canonical alias)

test: api-tests node-test ## run backend + frontend tests (canonical alias)

test-cov: api-tests-cov ## run tests with coverage (canonical alias)

ci: lint typecheck test ## run the canonical CI pipeline locally

clean: ## remove build artifacts and caches
	@rm -rf htmlcov coverage.xml .coverage .pytest_cache .mypy_cache .ruff_cache
