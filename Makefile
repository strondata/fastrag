# Makefile for FastRAG development

.PHONY: help install install-dev test lint format clean

help:
	@echo "FastRAG Development Commands"
	@echo "----------------------------"
	@echo "install      - Install package"
	@echo "install-dev  - Install package with dev dependencies"
	@echo "test         - Run tests"
	@echo "lint         - Run linters"
	@echo "format       - Format code"
	@echo "clean        - Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=fastrag --cov-report=term-missing --cov-report=html

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ examples/
	isort src/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
