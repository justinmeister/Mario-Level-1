# Makefile for Super Mario Bros Level 1
# Provides shortcuts for common development tasks

.PHONY: help install run test lint typecheck format clean build venv docs

# Default target
help:
	@echo "Super Mario Bros Level 1 - Development Commands"
	@echo ""
	@echo "  install     - Install dependencies"
	@echo "  run         - Run the game"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run flake8 linter"
	@echo "  typecheck   - Run mypy type checker"
	@echo "  format      - Format code with black and isort"
	@echo "  clean       - Remove build artifacts and cache"
	@echo "  build       - Build executable with PyInstaller"
	@echo "  venv        - Create virtual environment"
	@echo "  precommit   - Install pre-commit hooks"
	@echo ""

# Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Create virtual environment
venv:
	$(PYTHON) -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: .venv\\Scripts\\activate"
	@echo "  Unix: source .venv/bin/activate"

# Run the game
run:
	$(PYTHON) Mario.py

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v --cov=data --cov-report=term-missing

# Run tests with HTML coverage report
test-html:
	$(PYTHON) -m pytest tests/ -v --cov=data --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Run linter
lint:
	$(PYTHON) -m flake8 data/ tests/ --max-line-length=120 --ignore=E501,W503

# Run type checker
typecheck:
	$(PYTHON) -m mypy data/ tests/ --ignore-missing-imports

# Format code
format:
	$(PYTHON) -m black data/ tests/ --line-length 120
	$(PYTHON) -m isort data/ tests/ --profile black

# Check formatting (without modifying)
format-check:
	$(PYTHON) -m black data/ tests/ --line-length 120 --check
	$(PYTHON) -m isort data/ tests/ --profile black --check

# Install pre-commit hooks
precommit:
	$(PYTHON) -m pre_commit install

# Run pre-commit checks
precommit-run:
	$(PYTHON) -m pre_commit run --all-files

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf saves/*.sav
	rm -rf screenshots/*.png
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete!"

# Build executable
build:
	$(PYTHON) -m pip install pyinstaller
	$(PYTHON) -m PyInstaller --onefile --name Mario Mario.py
	@echo "Build complete! Executable in dist/"

# Quick validation (for CI)
validate: lint typecheck test
	@echo "All checks passed!"
