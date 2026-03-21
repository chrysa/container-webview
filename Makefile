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
