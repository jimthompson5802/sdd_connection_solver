# Makefile for sdd_connection_solver
# Usage: `make <target>`
# Run `make help` to see all available targets and descriptions.

# -----------------------------
# Configuration
# -----------------------------
SHELL := /bin/bash

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Python / venv
PY ?= python3
VENV_DIR ?= .venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip
PYTHON := $(VENV_BIN)/python
UVICORN := $(VENV_BIN)/uvicorn

# Node
NPM ?= npm

# Helper to detect package-lock for reproducible install
PKG_LOCK := $(FRONTEND_DIR)/package-lock.json

# Default target
.DEFAULT_GOAL := help

# Don't try to build files named like targets
.PHONY: help setup install install-backend install-frontend build-frontend dev-frontend run-backend dev-backend test-backend lint-backend format-backend type-backend clean clean-frontend clean-backend

# -----------------------------
# Help
# -----------------------------
# Each target has a description after `##`. `make help` parses and prints them.
help: ## Show this help listing
	@echo "\nProject utility targets:\n"
	@awk 'BEGIN {FS = ":.*##"; printf "%-28s %s\n", "Target", "Description"} \
	/^[a-zA-Z0-9_.-]+:.*?##/ { printf "%-28s %s\n", $$1, $$2 } \
	END {print ""}' $(MAKEFILE_LIST)

# -----------------------------
# Python environment and backend deps
# -----------------------------
setup: ## Create Python virtual environment and upgrade pip
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PY) -m venv "$(VENV_DIR)"; \
	fi
	@"$(PIP)" install --upgrade pip wheel setuptools

install-backend: setup ## Install backend dependencies into venv
	@echo "Installing backend dependencies..."
	@if [ -f "$(BACKEND_DIR)/requirements.txt" ]; then \
		"$(PIP)" install -r "$(BACKEND_DIR)/requirements.txt"; \
	fi
	@if [ -f "$(BACKEND_DIR)/pyproject.toml" ]; then \
		cd "$(BACKEND_DIR)" && ../"$(PIP)" install -e .; \
	fi

run-backend: ## Run backend locally with autoreload (FastAPI/Uvicorn)
	@echo "Starting backend at http://127.0.0.1:8000 ..."
	@"$(UVICORN)" $(BACKEND_DIR).run:app --reload --host 0.0.0.0 --port 8000

dev-backend: ## Run backend in dev mode (alias of run-backend)
	@$(MAKE) run-backend

# -----------------------------
# Frontend deps and build
# -----------------------------
install-frontend: ## Install frontend dependencies with npm (uses ci if lockfile present)
	@echo "Installing frontend dependencies..."
	@if [ -f "$(PKG_LOCK)" ]; then \
		cd "$(FRONTEND_DIR)" && $(NPM) ci; \
	else \
		cd "$(FRONTEND_DIR)" && $(NPM) install; \
	fi

build-frontend: ## Build frontend production bundle
	@cd "$(FRONTEND_DIR)" && $(NPM) run build

dev-frontend: ## Start frontend dev server (Webpack dev server)
	@cd "$(FRONTEND_DIR)" && $(NPM) run dev

# -----------------------------
# Repo-wide convenience targets
# -----------------------------
install: ## Install ALL dependencies (backend + frontend)
	@$(MAKE) install-backend
	@$(MAKE) install-frontend

# -----------------------------
# Quality: tests, lint, format, type-check
# -----------------------------
test-backend: ## Run backend tests (pytest)
	@"$(VENV_BIN)/pytest" -q -x -s -vv "$(BACKEND_DIR)"

lint-backend: ## Lint backend (flake8)
	@"$(VENV_BIN)/flake8" "$(BACKEND_DIR)"

format-backend: ## Format backend (black + isort)
	@"$(VENV_BIN)/black" "$(BACKEND_DIR)"
	@"$(VENV_BIN)/isort" "$(BACKEND_DIR)"

type-backend: ## Type-check backend (mypy)
	@"$(VENV_BIN)/mypy" "$(BACKEND_DIR)"

# -----------------------------
# Cleaning
# -----------------------------
clean-frontend: ## Clean frontend build artifacts
	@cd "$(FRONTEND_DIR)" && $(NPM) run clean || true

clean-backend: ## Clean backend caches and build artifacts
	@find "$(BACKEND_DIR)" -type d -name "__pycache__" -prune -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache build dist *.egg-info

clean: clean-frontend clean-backend ## Clean all build artifacts and caches
	@echo "Clean complete."
