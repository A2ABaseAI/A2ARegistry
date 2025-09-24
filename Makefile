# Makefile for A2A Registry Development
# 
# Usage:
#   make quality          # Run all quality checks
#   make lint             # Run linting only
#   make security         # Run security check only
#   make type             # Run type checking only
#   make test             # Run tests only
#   make backend          # Run the backend server
#   make examples         # Run all examples
#   make example NAME=... # Run specific example by name
#   make publish          # Publish SDK to PyPI
#   make help             # Show help

.PHONY: help quality lint security type test clean install-deps backend examples example publish build-sdk test-sdk

# Default target
help:
	@echo "A2A Registry Development Commands"
	@echo ""
	@echo "Quality Checks:"
	@echo "  quality          Run all quality checks"
	@echo "  lint             Run linting (flake8)"
	@echo "  security         Run security analysis (bandit)"
	@echo "  type             Run type checking (mypy)"
	@echo "  test             Run tests (pytest)"
	@echo ""
	@echo "Development:"
	@echo "  backend          Run the backend server"
	@echo "  examples         Run all examples"
	@echo "  example NAME=... Run specific example by name"
	@echo ""
	@echo "SDK Publishing:"
	@echo "  sdk-build        Build SDK package"
	@echo "  sdk-check        Check SDK package"
	@echo "  sdk-publish-test Publish to Test PyPI"
	@echo "  sdk-publish      Publish to PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  install-deps     Install required dependencies"
	@echo "  clean            Clean up temporary files"
	@echo "  help             Show this help message"
	@echo ""
	@echo "Example usage:"
	@echo "  make backend"
	@echo "  make examples"
	@echo "  make example NAME=basic_usage"
	@echo "  make example NAME=publish_example"
	@echo "  make publish"

# Install required dependencies
install-deps:
	@echo "Installing quality check dependencies..."
	pip install flake8 bandit mypy pytest

# Run all quality checks
quality: lint security type test
	@echo "🎉 All quality checks completed!"

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	@source venv/bin/activate && flake8 app/ sdk/ tests/ examples/ 

# Run security analysis
security:
	@echo "🔒 Running security analysis..."
	@source venv/bin/activate && bandit -r app/ sdk/

# Run type checking
type:
	@echo "📝 Running type checking..."
	@source venv/bin/activate && mypy app/ sdk/ 

# Run tests
test:
	@echo "🧪 Running tests..."
	@source venv/bin/activate && TEST_MODE=true pytest tests/ --tb=line -q

# Run the backend server
backend:
	@echo "🚀 Starting A2A Registry backend server..."
	@echo "Server will be available at: http://localhost:8000"
	@echo "API docs will be available at: http://localhost:8000/docs"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run all examples
examples:
	@echo "📚 Running all examples..."
	@echo "Note: Some examples may fail if the backend server is not running"
	@echo ""
	@source venv/bin/activate && \
	if [ -f "examples/api/run_all_examples.py" ]; then \
		echo "Running API examples..."; \
		python examples/api/run_all_examples.py; \
	fi
	@source venv/bin/activate && \
	if [ -d "examples/python" ]; then \
		echo "Running Python SDK examples..."; \
		for example in examples/python/*.py; do \
			if [ -f "$$example" ] && [ "$$(basename $$example)" != "__init__.py" ]; then \
				echo "Running $$(basename $$example)..."; \
				python "$$example" || echo "Example $$(basename $$example) completed with warnings"; \
				echo ""; \
			fi; \
		done; \
	fi
	@echo "✅ All examples completed!"

# Run a specific example by name
example:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: Please specify example name with NAME=..."; \
		echo "Available examples:"; \
		echo "  make example NAME=basic_usage"; \
		echo "  make example NAME=publish_example"; \
		echo "  make example NAME=multi_tenant_visibility_example"; \
		echo "  make example NAME=simple_visibility_example"; \
		echo "  make example NAME=visibility_concept_example"; \
		echo "  make example NAME=run_all_examples"; \
		exit 1; \
	fi
	@echo "🎯 Running example: $(NAME)"
	@echo ""
	@source venv/bin/activate && \
	if [ -f "examples/python/$(NAME).py" ]; then \
		echo "Running Python SDK example: examples/python/$(NAME).py"; \
		python "examples/python/$(NAME).py"; \
	elif [ -f "examples/api/$(NAME).py" ]; then \
		echo "Running API example: examples/api/$(NAME).py"; \
		python "examples/api/$(NAME).py"; \
	elif [ "$(NAME)" = "run_all_examples" ] && [ -f "examples/api/run_all_examples.py" ]; then \
		echo "Running all API examples..."; \
		python "examples/api/run_all_examples.py"; \
	else \
		echo "❌ Example '$(NAME)' not found!"; \
		echo "Available examples:"; \
		echo "Python SDK examples:"; \
		ls examples/python/*.py 2>/dev/null | sed 's/.*\//  /' | sed 's/\.py$$//' || echo "  (none found)"; \
		echo "API examples:"; \
		ls examples/api/*.py 2>/dev/null | sed 's/.*\//  /' | sed 's/\.py$$//' || echo "  (none found)"; \
		exit 1; \
	fi

# Build SDK package
build-sdk:
	@echo "📦 Building A2A Registry SDK package..."
	@if [ ! -d "sdk/python" ]; then \
		echo "❌ SDK directory not found!"; \
		exit 1; \
	fi
	@cd sdk/python && \
	python -m pip install --upgrade build && \
	python -m build
	@echo "✅ SDK package built successfully!"
	@echo "📁 Package files created in sdk/python/dist/"

# Test SDK package locally
test-sdk: build-sdk
	@echo "🧪 Testing SDK package locally..."
	@cd sdk/python && \
	pip install dist/*.whl --force-reinstall && \
	python -c "import a2a_reg_sdk; print('✅ SDK imported successfully!')" && \
	pip uninstall a2a-reg-sdk -y
	@echo "✅ SDK package test completed!"

# Publish SDK to PyPI
publish: build-sdk
	@echo "🚀 Publishing A2A Registry SDK to PyPI..."
	@echo "⚠️  WARNING: This will publish to the real PyPI repository!"
	@echo "Make sure you have:"
	@echo "  1. Updated version in sdk/python/setup.py"
	@echo "  2. Created PyPI account and API token"
	@echo "  3. Set TWINE_USERNAME and TWINE_PASSWORD environment variables"
	@echo ""
	@read -p "Are you sure you want to continue? (y/N): " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "📤 Publishing to PyPI..."; \
		cd sdk/python && \
		pip install --upgrade twine && \
		twine upload dist/*; \
		echo "✅ SDK published to PyPI successfully!"; \
		echo "📦 Package available at: https://pypi.org/project/a2a-reg-sdk/"; \
	else \
		echo "❌ Publishing cancelled."; \
		exit 1; \
	fi

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	@echo "🧹 Cleaning SDK build artifacts..."
	@if [ -d "sdk/python/dist" ]; then rm -rf sdk/python/dist; fi
	@if [ -d "sdk/python/build" ]; then rm -rf sdk/python/build; fi
	@if [ -d "sdk/python/*.egg-info" ]; then rm -rf sdk/python/*.egg-info; fi

# SDK Publishing targets
sdk-build:
	@echo "🔨 Building SDK package..."
	@cd sdk/python && source ../../venv/bin/activate && rm -rf dist/ build/ *.egg-info/ && python -m build

sdk-check:
	@echo "✅ Checking SDK package..."
	@cd sdk/python && source ../../venv/bin/activate && twine check dist/*

sdk-publish-test:
	@echo "🚀 Publishing to Test PyPI..."
	@cd sdk/python && source ../../venv/bin/activate && twine upload --repository testpypi dist/*

sdk-publish:
	@echo "🚀 Publishing to PyPI..."
	@cd sdk/python && source ../../venv/bin/activate && twine upload dist/*
