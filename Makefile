#!/usr/bin/make -f
# -*- makefile -*-

SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c
.DEFAULT_GOAL := help
.LOGGING      := 0

.ONESHELL:             ;  # Recipes execute in same shell
.NOTPARALLEL:          ;  # Wait for this target to finish
.SILENT:               ;  # No need for @
.EXPORT_ALL_VARIABLES: ;  # Export variables to child processes.
.DELETE_ON_ERROR:      ;  # Delete target if recipe fails.

# Modify the block character to be `-\t` instead of `\t`
ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This version of Make does not support .RECIPEPREFIX.)
endif
.RECIPEPREFIX = -


PROJECT_DIR := $(shell pwd)
SRC_DIR     := $(PROJECT_DIR)/storyteller
BUILD_DIR   := $(PROJECT_DIR)/dist

default: $(.DEFAULT_GOAL)
all: help


define Install
	echo "🐍 Setting up virtual environment..."
	if [ ! -d "$1" ]; then
		python3 -m pip install --upgrade venv
		python3 -m venv venv
	fi
	source venv/bin/activate
	python3 -m pip install --upgrade pip wheel
	python3 -m pip install --no-compile --editable '.[developer]'
endef


.PHONY: help
help: ## List commands <default>
-	$(call Logging,./logs/$(shell date +%Y-%m-%d-%H-%M-%S).log)
-	echo -e "USAGE: make \033[36m[COMMAND]\033[0m\n"
-	echo "Available commands:"
-	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\t\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: run
run: ## Run the application
-	python -m storyteller


.PHONY: install
install:	## Setup a Virtual Environment
-	$(call Install,./venv)


PHONY: update
update: ## git pull branch
-	echo "🆕 Updating branch..."
-	git pull origin `git config --get remote.origin.url`


.PHONY: lint
lint: ## Lint the code
-	black $(SRC_DIR)
-	isort $(SRC_DIR)
-	flake8 $(SRC_DIR) --max-line-length 119


.PHONY: clean
clean: ## Remove build, test, and other Python artifacts
-	rm -rf out

