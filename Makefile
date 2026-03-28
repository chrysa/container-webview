#!make
ifneq (,)
	$(error This Makefile requires GNU Make)
endif

include $(shell find . -type f -name "*.[Mm]akefile" -not -path "*/\.*" -exec echo " {}" \;)

__project_directory=$(shell pwd)

SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(shell find . -type f -name "*.[Mm]akefile" -not -path "*/\.*") | sort | cut -d":" -f1 | tr "\n" " ")

check-defined-% :
	@:$(call check_defined, $*, target-specific)

check_defined = $(strip $(foreach 1,$1, $(call __check_defined,$1,$(strip $(value 2)))))

__check_defined = $(if $(value $1),, $(error Undefined $1$(if $2, ($2))$(if $(value ), required by target $)))

help: ## Display this help message
	@echo "==================================================================="
	@echo "$(shell basename "$$(pwd)") Development Environment"
	@echo "==================================================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@for file in $(shell find . -type f -name "*.[Mm]akefile" -not -path "*/\.*" 2>/dev/null | sort); do \
		category=$$(basename $$file .makefile); \
		category=$$(echo $$category | sed 's/\.Makefile//'); \
		case $$category in \
			docker)    icon="🐳" ;; \
			node)      icon="📦" ;; \
			project)   icon="🚀" ;; \
			tests)     icon="🧪" ;; \
			tools)     icon="🔧" ;; \
			*)         icon="📌" ;; \
		esac; \
		echo ""; \
		echo "$$icon $$(echo $$category | tr '[:lower:]' '[:upper:]'):"; \
		grep -E '^[a-zA-Z_-]+(\([^)]*\))?:.*?## .*$$' $$file 2>/dev/null | sort | \
			awk 'BEGIN {FS = ":.*?## "}; { \
				cmd = $$1; \
				desc = $$2; \
				if (match(cmd, /\([^)]+\)/)) { \
					args = substr(cmd, RSTART+1, RLENGTH-2); \
					gsub(/\([^)]+\)/, "", cmd); \
					printf "  \033[36m%-30s\033[0m \033[33m%-15s\033[0m %s\n", cmd, args, desc; \
				} else { \
					printf "  \033[36m%-30s\033[0m \033[33m%-15s\033[0m %s\n", cmd, "", desc; \
				} \
			}'; \
	done
	@echo ""
	@echo "==================================================================="

help-%: ## Show detailed help for a specific command
	@echo "Showing help for: $*"
	@grep -A 5 -B 2 "^$*:" $(shell find . -name "*.[Mm]akefile" -not -path "*/\.*" -type f) 2>/dev/null || echo "Command '$*' not found"
