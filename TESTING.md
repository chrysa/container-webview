# TESTING — container-webview

> Generated 2026-09-25. Commands below are transcribed from `README.md`, `Makefile`/`makefiles/`,
> `docker-compose.yml` and `code/package.json`. They were NOT executed in this docs-only pass; treat
> them as documented, not verified. Tags: [DOC] documented, [PRESENT] artefact exists in tree.

## Backend (pytest)
- [PRESENT] Suite under `api/app/tests/` mirrors `services/` and `routers/`:
  - `tests/services/`: `test_docker_client`, `test_lifecycle_service`, `test_alerts_service`,
    `test_metrics_service`, `test_project_manager`, `test_auth_service`, `test_topology_service`.
  - `tests/routers/`: `test_auth`, `test_projects`, `test_lifecycle`, `test_metrics`, `test_alerts`,
    `test_topology`.
  - `tests/test_main.py`, shared `tests/conftest.py` (fixtures: fake docker client, api_client, auth_headers).
- [DOC] Coverage floor 80% (target 85% per CLAUDE.md/AGENTS.md). Source: `README.md`.
- [DOC] Runs in the `api-test` container (compose `test` profile), env: `SECRET_KEY=test-secret-key-for-ci`,
  `ADMIN_USERNAME=testuser`, `ADMIN_PASSWORD=testpass`, `PROJECTS_PATH=/tmp/projects`. Source: `docker-compose.yml`.

### Commands (documented)
```bash
make api-tests        # Run backend tests (Docker)
make api-tests-cov    # Tests + terminal coverage
make api-tests-html   # Tests + HTML report (htmlcov/)
make api-lint         # Ruff
make api-format       # Ruff formatter
make api-typecheck    # mypy
make pre-commit       # All pre-commit hooks
make ci-run-local     # Full CI pipeline locally
```

## Frontend (Vitest)
- [PRESENT] `code/package.json` declares `vitest` and a `test` script (`vitest`).
- UNKNOWN — no `*.test.ts(x)` / `*.spec.ts(x)` files were located under `code/src/` in this pass;
  canon expects "Vitest + Testing Library + MSW from the scaffold". See REVIEW.md (test coverage gap).

## CI
- [PRESENT] `.github/workflows/ci.yml` (10.6K) plus `cd.yml`, `release.yml`, and gate workflows.
- [DOC] CI runs on push to `develop`/`main` and PRs; SonarCloud analysis configured in CI (not via
  `sonar-project.properties`). Source: `CLAUDE.md`.
- [PRESENT] GitLab CI mirror: `.gitlab-ci.yml`.

## Not run here
No tests, linters, type-checkers or builds were executed (documentation-only task). Coverage numbers,
pass/fail state, and Vitest presence are therefore UNVERIFIED.
