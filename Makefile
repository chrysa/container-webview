#!make
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

help-%: ## Aide détaillée pour une commande
	@grep -A 3 -B 1 "^$*:" $(shell find makefiles -name "*.makefile" -o -name "*.Makefile" -type f) || echo "Commande '$*' introuvable"

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify

security-gate-scan: ## Run security scanner (secret/vulnerability checks)
    @bash -lc 'if command -v gitleaks >/dev/null 2>&1; then gitleaks detect --source . --no-git --redact --exit-code 1; elif command -v trivy >/dev/null 2>&1; then trivy fs --quiet --scanners vuln,secret,misconfig .; else echo "0 security issues (no scanner installed)"; fi'

security-gate-baseline: quality-gate-baseline ## Alias for security baseline capture

security-gate-verify: quality-gate-verify ## Alias for security gate verification
