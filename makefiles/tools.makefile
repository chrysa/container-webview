pre-commit-install: ## install pre-commit hooks
	@pre-commit install
	@pre-commit install --hook-type commit-msg

pre-commit-run: ## run all pre-commit hooks on all files
	@pre-commit validate-config
	@pre-commit validate-manifest
	@pre-commit run --all-files --hook-stage manual --verbose

pre-commit-update: ## update all pre-commit hooks to latest versions
	@pre-commit autoupdate

pre-commit: pre-commit-install pre-commit-run ## install hooks and run on all files

changelog-generate: ## generate changelog from yaml files
	@pre-commit run generate-changelog --hook-stage manual --all-files
