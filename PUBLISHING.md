# Publishing Guide for A2A Registry SDK

This guide explains how to publish the A2A Registry SDK to PyPI using the Makefile commands.

## Prerequisites

### 1. PyPI Account
- Create an account at [PyPI](https://pypi.org/account/register/)
- Enable two-factor authentication for security

### 2. API Token
- Go to [PyPI Account Settings](https://pypi.org/manage/account/)
- Create a new API token with scope "Entire account" or "Project: a2a-reg-sdk"
- Save the token securely

### 3. Environment Variables
Set your PyPI credentials as environment variables:

```bash
# Option 1: Environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# Option 2: Use .pypirc file (alternative)
# Create ~/.pypirc with your credentials
```

## Publishing Process

### Step 1: Update Version
Before publishing, update the version in `sdk/python/setup.py`:

```python
setup(
    name="a2a-reg-sdk",
    version="1.0.1",  # Increment version number
    # ... rest of setup
)
```

### Step 2: Build Package
```bash
make build-sdk
```

This creates:
- `sdk/python/dist/a2a_reg_sdk-1.0.1-py3-none-any.whl` (wheel package)
- `sdk/python/dist/a2a_reg_sdk-1.0.1.tar.gz` (source distribution)

### Step 3: Test Package Locally
```bash
make test-sdk
```

This will:
- Install the package locally
- Test that it can be imported
- Uninstall the test package

### Step 4: Publish to PyPI
```bash
make publish
```

This will:
- Show a warning about publishing to real PyPI
- Ask for confirmation
- Upload the package using twine
- Provide the PyPI URL

## Publishing Commands

### Build SDK Package
```bash
make build-sdk
```
- Builds both wheel (.whl) and source (.tar.gz) distributions
- Uses modern Python build tools
- Creates packages in `sdk/python/dist/`

### Test SDK Package
```bash
make test-sdk
```
- Builds the package (if not already built)
- Installs it locally
- Tests import functionality
- Uninstalls the test package

### Publish to PyPI
```bash
make publish
```
- Builds the package (if not already built)
- Shows safety warnings
- Prompts for confirmation
- Uploads to PyPI using twine
- Provides success confirmation

## Package Information

### Package Name
- **PyPI Name**: `a2a-reg-sdk`
- **Import Name**: `a2a_reg_sdk`

### Installation
Once published, users can install with:
```bash
pip install a2a-reg-sdk
```

### Usage
```python
from a2a_reg_sdk import A2AClient

client = A2AClient(registry_url="https://your-registry.com")
```

## Version Management

### Semantic Versioning
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Examples
- `1.0.0` - Initial release
- `1.0.1` - Bug fix
- `1.1.0` - New feature
- `2.0.0` - Breaking change

## Troubleshooting

### Build Errors
```bash
# Clean build artifacts
make clean

# Rebuild
make build-sdk
```

### Upload Errors
- Check PyPI credentials
- Verify package name availability
- Ensure version number is unique

### Import Errors
```bash
# Test package locally
make test-sdk

# Check package contents
python -c "import a2a_reg_sdk; print(dir(a2a_reg_sdk))"
```

## Security Notes

- Never commit API tokens to version control
- Use environment variables for credentials
- Enable 2FA on PyPI account
- Test packages thoroughly before publishing

## CI/CD Integration

For automated publishing, you can integrate with GitHub Actions:

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install build twine
      - name: Build package
        run: make build-sdk
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: make publish
```

## Package Metadata

The package includes:
- **Name**: a2a-reg-sdk
- **Description**: Python SDK for the A2A Agent Registry
- **Author**: A2A Registry Team
- **License**: Apache Software License
- **Python Versions**: 3.8+
- **Dependencies**: requests, PyYAML
- **Keywords**: a2a, agents, ai, registry, sdk, python

## Support

For publishing issues:
- Check [PyPI Help](https://pypi.org/help/)
- Review [Python Packaging Guide](https://packaging.python.org/)
- Open an issue in this repository
