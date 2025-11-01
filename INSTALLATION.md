# Installation Guide

This guide covers different ways to install and use the A2A Registry components.

## 🐍 Python SDK Installation

### From PyPI (Recommended)

The easiest way to install the A2A Registry Python SDK:

```bash
pip install a2a-reg-sdk
```

### From Source

If you want to install from the latest source code:

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/sdk/python
pip install -e .
```

### Development Installation

For development with all dependencies:

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/sdk/python
pip install -e ".[dev]"
```

## 🚀 Registry Server Installation

### Using Docker (Recommended)

The easiest way to run the registry server:

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry
docker-compose up -d
```

### Manual Installation

For development or production deployment:

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run the server
uvicorn registry.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Development Setup

### Full Development Environment

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
make install-deps

# Run quality checks
make quality

# Start the backend
make backend
```

### SDK Development

```bash
cd sdk/python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Build package
make sdk-build

# Check package
make sdk-check
```

## 📦 Publishing SDK to PyPI

### Prerequisites

1. Create a PyPI account at [pypi.org](https://pypi.org)
2. Generate an API token
3. Configure credentials:

```bash
# Using keyring (recommended)
python -m keyring set https://upload.pypi.org/legacy/ __token__

# Or using .pypirc file
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-your-api-token-here
EOF
```

### Publishing Process

```bash
# Build the package
make sdk-build

# Check the package
make sdk-check

# Test on Test PyPI first
make sdk-publish-test

# Publish to real PyPI
make sdk-publish
```

## 🧪 Testing Installation

### Test SDK Installation

```python
from a2a_reg_sdk import A2AClient

# Test basic import
client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="test-client",
    client_secret="test-secret"
)
print("✅ SDK installed successfully!")
```

### Test Registry Server

```bash
# Check if server is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're using the correct package name `a2a_reg_sdk`
2. **Connection Error**: Ensure the registry server is running on the correct port
3. **Authentication Error**: Check your client credentials and registry URL

### Getting Help

- **Documentation**: [docs.a2areg.dev](https://docs.a2areg.dev)
- **Issues**: [GitHub Issues](https://github.com/a2areg/a2a-registry/issues)
- **Discord**: [Community Chat](https://discord.gg/rpe5nMSumw)

## 📋 Requirements

- Python 3.9+
- pip 21.0+
- Docker (for containerized deployment)
- PostgreSQL (for production)
- Redis (for caching)
- OpenSearch/Elasticsearch (for search)

## 🎯 Quick Start Examples

### Basic SDK Usage

```python
from a2a_reg_sdk import A2AClient, AgentBuilder

# Create client
client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Authenticate
client.authenticate()

# Create and publish agent
agent = AgentBuilder("my-agent", "My AI Agent", "1.0.0", "my-org") \
    .with_tags(["ai", "assistant"]) \
    .with_location("https://api.my-org.com/agent") \
    .public(True) \
    .build()

published_agent = client.publish_agent(agent)
print(f"Published: {published_agent.id}")
```

### Running Examples

```bash
# Run all examples
make examples

# Run specific example
make example NAME=basic_usage
make example NAME=publish_example
make example NAME=multi_tenant_visibility_example
```
