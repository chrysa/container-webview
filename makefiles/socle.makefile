# Canonical chrysa Makefile socle — umbrella targets with the exact names the
# fleet standard mandates, delegating to the repo's namespaced targets.
# See shared-standards → "Makefile targets".

install: app-install ## install all dependencies (frontend + backend)

install-dev: app-install ## install dependencies incl. dev tooling (container-baked)

lint: api-lint node-lint ## lint backend (ruff) + frontend (eslint)

format: api-format ## format backend (ruff format)

format-check: ## check formatting without writing (CI)
	@docker compose run --rm api python -m ruff format --check app/

typecheck: api-typecheck ## type-check backend (mypy)

web-typecheck: ## type-check frontend (tsc)
	@docker compose run --rm frontend npm run typecheck

web-lint: node-lint ## lint frontend (eslint)

web-build: node-build ## build frontend for production

test: api-tests node-test ## run backend + frontend unit tests

test-cov: api-tests-cov ## run backend tests with coverage

docker-test: api-tests node-test ## run the test suites in containers

e2e: ## run end-to-end tests (Playwright)
	@docker compose run --rm frontend npm run test:e2e

build: app-build docker-build ## build frontend artefact + images

dev: app-dev ## launch the full stack in development mode

clean: ## stop the stack and drop volumes + regenerable artefacts
	@docker compose down --volumes --remove-orphans
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache \) -prune -exec rm -rf {} + 2>/dev/null || true

quality-gate-baseline: ## record the current quality metrics as the baseline
	@python scripts/quality_gate.py baseline

quality-gate-verify: ## verify quality metrics against the baseline (CI gate)
	@python scripts/quality_gate.py verify

ci: lint typecheck test-cov ## the gate CI runs: lint + type-check + tested coverage
