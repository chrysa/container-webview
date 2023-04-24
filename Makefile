#!make
ifneq (,)
	$(error This Makefile requires GNU Make)
endif


include $(shell find makefiles/ -type f -name "*.makefile" -exec echo " {}" \;)

__project_directory=$(shell pwd)

SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | cut -d":" -f1 | tr "\n" " ")

check-defined-% :
	:$(call check_defined, $*, target-specific)

check_defined = $(strip $(foreach 1,$1, $(call __check_defined,$1,$(strip $(value 2)))))

__check_defined = $(if $(value $1),, $(error Undefined $1$(if $2, ($2))$(if $(value ), required by target $)))

help: ## display help
	@len_col_1=50; len_col_2=60; len_col_3=50; len_col_4=60; len_col_5=20; \
	echo -e "Hello to the \`$(shell basename "$$(pwd)")\` Makefile\n \
	\tmake [target] [args]\n\n"; \
	printf "| %0-*s | %0-*s | %0-*s | %0-*s | %0-*s |\n" "$${len_col_1}" "Rule"  "$${len_col_2}" "Help" "$${len_col_3}" "Usage" "$${len_col_4}" "dependencies" "$${len_col_5}" "Service" ; \
	printf "+%0-*s  +%0-*s  +%0-*s  +%0-*s  +%0-*s  +\n" "$${len_col_1}" "====" "$${len_col_2}" "====" "$${len_col_3}" "====" "$${len_col_4}" "====" "$${len_col_5}" "====" ; \
	for makefile in $(shell echo $(MAKEFILE_LIST) | sort); do \
		dir_name=$$(dirname $$makefile | rev | cut -d"/" -f1 | rev) ; \
		if [ "$$dir_name" = "." ] || [ "$$dir_name" = "makefiles" ]; then dir_name=""; fi; \
		cat $$makefile | grep -v "^#" | grep -E "^[a-zA-Z_-]+:.*?## .*$$|^[a-zA-Z_-]+:.*?$$|^\s+=> .*$$" | while read line; do \
			name=$$(echo $$line | awk  -F ':' '{print $$1}'); \
			if echo "$$line" | grep -q "=>" ; then \
				help=$$(echo "$$line" | awk -F '##' '{print $$2}' | awk -F '=>' '{print $$1}' | sed -e 's/^[[:space:]]*//'); \
				usage=$$(echo "$$line" | awk -F '=>' '{print $$2}' | sed -e 's/^[[:space:]]*//'); \
			else \
				help=$$(echo "$$line" | awk -F '##' '{print $$2}' | sed -e 's/^[[:space:]]*//'); \
				usage=""; \
			fi ; \
			deps="" ;\
			for dep in `grep -E "^$$name:" $(MAKEFILE_LIST) | awk -F ': ' '{print $$2}' | awk -F '##' '{print $$1}'`; do \
				if [[ ! "$$dep" =~ ^check-defined- ]]; then \
					deps="$${deps} $${dep}"; \
				fi ; \
			done ; \
			dependencies=$$(if [ "$$deps" ]; then echo "$$deps"; else echo ""; fi); \
			printf "| %0-*s | %0-*s | %0-*s | %0-*s | %0-*s |\n" "$${len_col_1}" "$$name" "$${len_col_2}" "$$help" "$${len_col_3}" "$$usage" "$${len_col_4}" "$$dependencies" "$${len_col_5}" "$${dir_name}" ; \
		done \
	done
