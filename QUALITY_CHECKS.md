# Quality Check Scripts

This directory contains scripts to run comprehensive quality checks on the A2A Registry codebase.

## Available Scripts

### 1. Python Script (`quality_check.py`)
A comprehensive Python script that runs all quality checks with detailed output and error handling.

### 2. Shell Script (`quality_check.sh`)
A lightweight bash script for quick quality checks.

## Usage

### Python Script
```bash
# Run all quality checks
python quality_check.py --all

# Run specific checks
python quality_check.py --lint
python quality_check.py --security
python quality_check.py --type
python quality_check.py --test

# Run multiple checks
python quality_check.py --lint --test

# Show help
python quality_check.py --help
```

### Shell Script
```bash
# Run all quality checks (default)
./quality_check.sh

# Run specific checks
./quality_check.sh --lint
./quality_check.sh --security
./quality_check.sh --type
./quality_check.sh --test

# Run multiple checks
./quality_check.sh --lint --test

# Show help
./quality_check.sh --help
```

### Makefile
```bash
# Quality checks
make quality          # Run all quality checks
make lint             # Run linting only
make security         # Run security check only
make type             # Run type checking only
make test             # Run tests only

# Development commands
make backend          # Run the backend server
make examples         # Run all examples
make example NAME=... # Run specific example by name

# Publishing commands
make publish          # Publish SDK to PyPI
make build-sdk        # Build SDK package
make test-sdk         # Test SDK package locally

# Utilities
make install-deps     # Install required dependencies
make clean            # Clean up temporary files
make help             # Show help message
```

## Development Commands

### 🚀 Backend Server
```bash
# Start the backend server
make backend
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Starts the A2A Registry API server
- Available at: http://localhost:8000
- API docs at: http://localhost:8000/docs
- Auto-reloads on code changes

### 📚 Examples
```bash
# Run all examples
make examples

# Run specific example
make example NAME=basic_usage
make example NAME=publish_example
make example NAME=multi_tenant_visibility_example
```
- Demonstrates SDK functionality
- Shows API usage patterns
- Tests multi-tenant features
- Some examples require running backend server

### 📦 SDK Publishing
```bash
# Build SDK package
make build-sdk

# Test SDK package locally
make test-sdk

# Publish to PyPI (requires PyPI credentials)
make publish
```
- Builds wheel and source distribution packages
- Tests package installation and import
- Publishes to PyPI with confirmation prompt
- Requires PyPI account and API token

## What Each Check Does

### 🔍 Linting (flake8)
- Checks code style and formatting
- Enforces PEP 8 standards
- Identifies unused imports and variables
- Checks line length and indentation
- **Target**: < 30 issues (currently ~25)

### 🔒 Security (bandit)
- Scans for common security vulnerabilities
- Checks for hardcoded passwords
- Identifies potential injection points
- **Target**: < 5 issues (currently 4)

### 📝 Type Checking (mypy)
- Validates type annotations
- Catches type mismatches
- Improves code reliability
- **Target**: < 50 issues (currently ~45)

### 🧪 Tests (pytest)
- Runs all unit and integration tests
- Validates functionality
- Ensures code quality
- **Target**: 100% pass rate (currently 190/190)

## Quality Metrics

| Check | Current Status | Target | Status |
|-------|---------------|--------|--------|
| **Linting** | ~25 issues | < 30 | ✅ |
| **Security** | 4 issues | < 5 | ✅ |
| **Type Checking** | ~45 issues | < 50 | ✅ |
| **Tests** | 190/190 passing | 100% | ✅ |

## Prerequisites

Make sure you have the required tools installed:

```bash
pip install flake8 bandit mypy pytest
```

## Integration with CI/CD

These scripts can be easily integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Quality Checks
  run: python quality_check.py --all
```

## Troubleshooting

### Virtual Environment Issues
If you get virtual environment errors:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Missing Dependencies
If tools are missing:
```bash
pip install flake8 bandit mypy pytest
```

### Permission Issues
Make sure scripts are executable:
```bash
chmod +x quality_check.py
chmod +x quality_check.sh
```

## Contributing

When adding new quality checks:
1. Update both scripts consistently
2. Add appropriate error handling
3. Update this documentation
4. Test with the current codebase
