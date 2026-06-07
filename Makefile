#!make
# makefile-tier: fullstack
ifneq (,)
	$(error This Makefile requires GNU Make)
endif

include $(shell find . -type f -name "*.[Mm]akefile" -not -path "*/\.*" -exec echo " {}" \;)

.DEFAULT_GOAL := help

SHELL := /bin/bash

SERVICE ?=
PROJECTS_PATH ?= /opt/projects

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(shell find makefiles -name "*.Makefile" -o -name "*.makefile" -type f) | sort | cut -d":" -f1 | tr "\n" " ")

help: ## Afficher l'aide
	@echo "==================================================================="
	@echo " Docker Overview WebUI"
	@echo "==================================================================="
	@echo ""
	@for file in $(shell find . -type f \( -name "*.Makefile" -o -name "*.makefile" \) -not -path "*/\.*" -exec echo "{}" \; 2>/dev/null | sort); do \
		category=$$(basename $$file .makefile); \
		category=$$(basename $$category .Makefile); \
		case $$category in \
			docker)   icon="🐳" ;; \
			node)     icon="📦" ;; \
			api)      icon="⚙️ " ;; \
			project)  icon="🚀" ;; \
			*)        icon="📋" ;; \
		esac; \
		entries=$$(grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$file 2>/dev/null); \
		if [ -n "$$entries" ]; then \
			echo "$$icon $$(echo $$category | tr '[:lower:]' '[:upper:]'):"; \
			echo "$$entries" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'; \
			echo ""; \
		fi; \
	done
	@echo "Variables d'environnement :"
	@echo "  PROJECTS_PATH=$(PROJECTS_PATH)"
	@echo "  SERVICE=$(SERVICE)"
	@echo "==================================================================="

help-%: ## Show detailed help for a command
	@grep -A 3 -B 1 "^$*:" $(shell find makefiles -name "*.makefile" -o -name "*.Makefile" -type f) || echo "Commande '$*' introuvable"

# ─── Standards compliance stubs ───────────────────────────────────────────────

install: ## Install all dependencies (API + Node)
	$(MAKE) api-install node-install

dev: ## Start development environment
	$(MAKE) dev-up

test: ## Run all tests
	$(MAKE) api-tests node-test

test-cov: ## Run tests with coverage
	$(MAKE) api-tests-cov node-test-cov

lint: ## Run all linters
	$(MAKE) api-lint node-lint

format: ## Format all code
	$(MAKE) api-format

typecheck: ## Run type checks
	$(MAKE) api-typecheck

build: ## Build Docker images
	$(MAKE) docker-build

docker-up: ## Start all services (detached)
	$(MAKE) -f makefiles/docker.makefile docker-up

docker-down: ## Stop and remove containers
	$(MAKE) -f makefiles/docker.makefile docker-down

docker-test: ## Run tests inside Docker
	$(MAKE) api-tests

clean: ## Clean build artifacts
	$(MAKE) node-clean docker-clean

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# ─── CI gate ────────────────────────────────────
ci: lint typecheck test ## Run the full local gate (lint + typecheck + test)
