SHELL := /bin/bash
MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT_DIR := $(dir $(MKFILE_PATH))
# Set version-related variables
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null)
BUILD_DATE := $(shell date -u -Iseconds)
BRANCH_NAME := $(or ${CI_COMMIT_REF_SLUG},$(shell git rev-parse --abbrev-ref HEAD 2>/dev/null))
LATEST_TAG := $(subst v,,$(shell git describe --abbrev=0 2>/dev/null))
DEFAULT_BRANCH := $(or ${CI_DEFAULT_BRANCH},main)

# Project information
PROJECT_NAME := pas_3_alignes
VERSION := $(subst v,,$(shell git describe --always --dirty=+ 2>/dev/null))

# Python
PIPENV_VENV_IN_PROJECT := 1

# Docker

# Check that given variables are set and all have non-empty values,
# die with an error otherwise.
#
# Params:
#   1. Variable name(s) to test.
#   2. (optional) Error message to print.
check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
      $(error Undefined $1$(if $2, ($2))))

.PHONY: debug
debug:
	echo "VERSION = $(VERSION)"
	echo "GIT_COMMIT = $(GIT_COMMIT)"
	echo "BRANCH_NAME = $(BRANCH_NAME)"
	echo "LATEST_TAG = $(LATEST_TAG)"
	echo "DEFAULT_BRANCH = $(DEFAULT_BRANCH)"
	echo "TAG_NAME = $(TAG_NAME)"
	echo "DOCKER_REGISTRY = $(DOCKER_REGISTRY)"

# The help target is inspired by https://gist.github.com/prwhite/8168133
.PHONY: help
help: ## This help message
	@echo 'Usage:'
	@echo '  make [target] ...'
	@echo
	@echo 'Targets:'
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/  \\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

version:  # Print the project version
	@echo $(VERSION)

.PHONY: clean-venv
clean-venv:  ## Clean the virtual environment.
	-@rm -rf .venv || true

# Ensure Python venv exists and creates it if not. We use the .myvenv to avoid calling pipenv with no reason.
.venv/pyvenv.cfg: poetry.lock
	@mkdir -p .venv
	@poetry install
	@touch .venv/pyvenv.cfg

# Ensure Python venv exists
.PHONY: venv
venv: .venv/pyvenv.cfg

.PHONY: shell
shell: venv  ## Start a shell inside the virtual environment.
	@poetry shell

#
# Python
#

.PHONY: clean
clean:
	@rm -rf .mypy_cache .pytest_cache .ruff_cache
	@find . -name "__pycache__" | xargs rm -rf
	@rm .coverage coverage.xml tests.xml

.PHONY: fmt
fmt: venv  ## Format Python code.
	@poetry run black src tests

.PHONY: lint
lint: venv  ## Lint Python code.
	@poetry run ruff check $(ARGS) src tests

.PHONY: typecheck
typecheck: venv  ## Check typing in Python code.
	@poetry run mypy $(ARGS) src tests

.PHONY: test
test: venv  ## Run unit tests.
	@poetry run $(WRAPPER) pytest tests/unit --junitxml=tests.xml $(ARGS)

.PHONY: --coverage
--coverage:
	@poetry run coverage report; \
	poetry run coverage xml

.PHONY: coverage
coverage: WRAPPER=coverage run -m
coverage: test --coverage  ## Run unit tests and generate coverage report.

.PHONY: module-test
module-test: venv  ## Run module tests.
	@poetry run pytest tests/module --junitxml=tests.xml $(ARGS)

.PHONY: package
package:  ## Package the library
	@poetry build

.PHONY: dependency-check
dependency-check:  ## check the dependencies
	@poetry run deptry src

.PHONY: precommit
precommit: fmt lint typecheck dependency-check  ## Run all precommit checks

.PHONY: premerge
premerge: precommit test coverage module-test ## Run all premerge checks
