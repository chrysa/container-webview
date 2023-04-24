ci-run-local: ## run ci pipeline locally
	$(info Make: run CI localy)
	@pip install --quiet --upgrade gitlabci-local ipython
	@gitlabci-local

pre-commit: ## run localy precommit
	@pre-commit validate-config
	@pre-commit validate-manifest
	@pre-commit install-hooks
	@pre-commit autoupdate --bleeding-edge
	@pre-commit run --all-files --hook-stage manual --verbose
