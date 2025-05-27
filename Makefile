.PHONY: install test lint format typecheck docs clean

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
FLAKE8 = flake8
MYPY = mypy
BLACK = black
ISORT = isort --profile black
SPHINX_BUILD = sphinx-build

# Directories
SRC = noocrush
TESTS = tests
DOCS = docs

install:
	@echo "Installing NooCrush in development mode..."
	$(PIP) install -e .
	$(PIP) install -r requirements-dev.txt

install-dev: install
	@echo "Installing development dependencies..."
	pre-commit install

test:
	@echo "Running tests..."
	$(PYTEST) -v --cov=$(SRC) --cov-report=term-missing $(TESTS)

lint:
	@echo "Linting code..."
	$(FLAKE8) $(SRC)
	$(FLAKE8) $(TESTS)

format:
	@echo "Formatting code..."
	$(BLACK) $(SRC) $(TESTS) setup.py
	$(ISORT) $(SRC) $(TESTS) setup.py

typecheck:
	@echo "Type checking..."
	$(MYPY) $(SRC) $(TESTS)

docs:
	@echo "Building documentation..."
	$(SPHINX_BUILD) -b html $(DOCS) $(DOCS)/_build/html

clean:
	@echo "Cleaning up..."
	rm -rf `find . -type d -name __pycache__`
	rm -rf `find . -type d -name .mypy_cache`
	rm -rf `find . -type d -name .pytest_cache`
	rm -rf `find . -type d -name .coverage`
	rm -rf `find . -type d -name htmlcov`
	rm -rf `find . -type d -name build`
	rm -rf `find . -type d -name dist`
	rm -rf `find . -type d -name *.egg-info`
	rm -rf $(DOCS)/_build

all: install-dev lint typecheck test docs

help:
	@echo "Available targets:"
	@echo "  install     - Install the package in development mode"
	@echo "  install-dev - Install development dependencies and set up pre-commit"
	@echo "  test        - Run tests"
	@echo "  lint        - Check code style with flake8"
	@echo "  format      - Format code with Black and isort"
	@echo "  typecheck   - Run static type checking with mypy"
	@echo "  docs        - Build documentation"
	@echo "  clean       - Remove build artifacts and caches"
	@echo "  all         - Run all checks (install, lint, typecheck, test, docs)"
