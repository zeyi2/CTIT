.PHONY: help activate test lint clean

help:
	@echo "Available targets:"
	@echo ""
	@echo "  make activate - Create venv and install dev dependencies"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Run linters/formatters"
	@echo "  make clean    - Clean development environment"

activate:
	@echo "Setting up development environment..."
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]"
	@echo "Done!"

test:
	@echo "Running tests..."
	python3 -m unittest discover -s tests -v

lint:
	@echo "Running black formatter..."
	venv/bin/black .
	@echo "Running yamllint..."
	venv/bin/yamllint -c .yamllint.yaml .github/
	@echo "Validating pyproject.toml..."
	venv/bin/validate-pyproject pyproject.toml

clean:
	rm -rf logs/
	rm -rf __pycache__/ testers/__pycache__/ tests/__pycache__/
	rm -rf *.egg-info/
