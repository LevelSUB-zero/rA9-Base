# RA9 Makefile
# Common development and deployment tasks

.PHONY: help install install-dev test lint format clean build docs serve

# Default target
help:
	@echo "RA9 - Ultra-Deep Cognitive Engine"
	@echo "================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install RA9 in production mode"
	@echo "  install-dev  Install RA9 in development mode with all dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (black, isort, flake8, mypy)"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts and cache"
	@echo "  build        Build package"
	@echo "  docs         Generate documentation"
	@echo "  serve        Start development server"
	@echo "  setup        Complete setup (install + configure)"
	@echo "  check        Run all checks (lint + test)"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs,test]"
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=ra9 --cov-report=html --cov-report=term

test-fast:
	pytest tests/ -v -x

# Linting and formatting
lint:
	black --check ra9/ tests/
	isort --check-only ra9/ tests/
	flake8 ra9/ tests/
	mypy ra9/

format:
	black ra9/ tests/
	isort ra9/ tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	python -m build

# Documentation
docs:
	mkdocs serve

docs-build:
	mkdocs build

# Development server
serve:
	python -m ra9.cli server --debug

# Complete setup
setup: install-dev
	@echo "Setting up RA9..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please edit it with your API keys."; \
	fi
	@echo "Setup complete! Edit .env file and run 'make serve' to start."

# Run all checks
check: format lint test

# Quick start
quick-start: install
	@echo "Quick start mode - basic installation only"
	@echo "For full development setup, run: make setup"

# Docker targets (if needed)
docker-build:
	docker build -t ra9:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env ra9:latest

# Release targets
release-check: clean lint test build
	@echo "Release checks passed!"

# Development helpers
dev-install:
	pip install -e ".[dev]" --force-reinstall

dev-reset: clean dev-install
	@echo "Development environment reset complete"

# Show configuration
config:
	python -m ra9.cli config-info

# Interactive mode
interactive:
	python -m ra9.cli interactive

# Process a test query
test-query:
	python -m ra9.cli process --query "Hello, how are you?" --mode concise
