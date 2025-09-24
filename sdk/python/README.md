# A2A Python SDK

A Python SDK for interacting with the A2A Agent Registry. This SDK provides easy-to-use classes and methods for agent registration, discovery, and management.

## Installation

### From PyPI

```bash
pip install a2a-reg-sdk
```

### From Source

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/sdk/python
pip install -e .
```

## Quick Start

```python
from a2a_reg_sdk import A2AClient, AgentBuilder

# Create and authenticate client
client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Authenticate
client.authenticate()

# Create a simple agent
agent = AgentBuilder("my-agent", "My AI Agent", "1.0.0", "my-org") \
    .with_tags(["ai", "assistant"]) \
    .with_location("https://api.my-org.com/agent") \
    .public(True) \
    .build()

# Publish the agent
published_agent = client.publish_agent(agent)
print(f"Published agent: {published_agent.id}")

# List agents
agents_response = client.list_agents()
print(f"Found {len(agents_response['agents'])} agents")

# Clean up
client.delete_agent(published_agent.id)
client.close()
```

## Features

- **Easy Authentication** - OAuth 2.0 client credentials flow
- **Agent Management** - Create, read, update, delete agents
- **Search & Discovery** - Powerful search with filters and semantic search
- **High-Level API** - Simplified publishing with validation
- **Type Safety** - Full type hints and data classes
- **Error Handling** - Comprehensive exception hierarchy
- **Context Managers** - Automatic resource cleanup

## Core Classes

### A2AClient

Main client for interacting with the registry.

```python
from a2a_reg_sdk import A2AClient

client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret",
    timeout=30
)

# Authenticate
client.authenticate()

# Use client methods
agents = client.list_agents()
agent = client.get_agent("agent-id")
```

### AgentBuilder

Fluent builder for creating agents.

```python
from a2a_reg_sdk import AgentBuilder, AgentCapabilities, AuthScheme

capabilities = AgentCapabilities(
    protocols=["http", "websocket"],
    supported_formats=["json"],
    max_concurrent_requests=50
)

auth_scheme = AuthScheme(
    type="api_key",
    required=True,
    header_name="X-API-Key"
)

agent = AgentBuilder("chatbot", "AI Chatbot", "1.0.0", "ai-corp") \
    .with_capabilities(capabilities) \
    .with_auth_schemes([auth_scheme]) \
    .with_tags(["ai", "chatbot", "nlp"]) \
    .with_location("https://api.ai-corp.com/chatbot") \
    .public(True) \
    .active(True) \
    .build()
```

### AgentPublisher

High-level interface for publishing with validation.

```python
from a2a_reg_sdk import A2AClient, AgentPublisher

client = A2AClient(...)
client.authenticate()

publisher = AgentPublisher(client)

# Create sample agent
sample_agent = publisher.create_sample_agent(
    name="demo-agent",
    description="Demo agent for testing",
    provider="demo-corp",
    api_url="https://api.demo-corp.com"
)

# Publish with validation
published_agent = publisher.publish(sample_agent, validate=True)

# Load from file
file_agent = publisher.load_agent_from_file("agent.yaml")
published_file_agent = publisher.publish(file_agent)
```

## Data Models

### Agent

Main agent data model with comprehensive metadata.

```python
from a2a_reg_sdk import Agent, AgentCapabilities, AuthScheme

agent = Agent(
    name="my-agent",
    description="My AI agent",
    version="1.0.0",
    provider="my-org",
    tags=["ai", "assistant"],
    is_public=True,
    is_active=True,
    location_url="https://api.my-org.com/agent",
    capabilities=AgentCapabilities(...),
    auth_schemes=[AuthScheme(...)]
)
```

### AgentCapabilities

Defines what the agent can do.

```python
from a2a_reg_sdk import AgentCapabilities

capabilities = AgentCapabilities(
    protocols=["http", "websocket", "grpc"],
    supported_formats=["json", "xml", "protobuf"],
    max_request_size=10485760,  # 10MB
    max_concurrent_requests=100,
    a2a_version="1.0"
)
```

### AuthScheme

Authentication methods supported by the agent.

```python
from a2a_reg_sdk import AuthScheme

# API Key authentication
api_key_auth = AuthScheme(
    type="api_key",
    description="API key in header",
    required=True,
    header_name="X-API-Key"
)

# OAuth 2.0 authentication
oauth_auth = AuthScheme(
    type="oauth2",
    description="OAuth 2.0 bearer token",
    required=False,
    header_name="Authorization"
)
```

## Examples

### Basic Agent Management

```python
from a2a_reg_sdk import A2AClient

# Create client
with A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
) as client:
    # Authenticate
    client.authenticate()
    
    # List all public agents
    response = client.list_agents(page=1, limit=50)
    print(f"Total agents: {response['total']}")
    
    for agent in response['agents']:
        print(f"- {agent['name']} v{agent['version']} by {agent['provider']}")
    
    # Get specific agent
    if response['agents']:
        agent_id = response['agents'][0]['id']
        agent_details = client.get_agent(agent_id)
        print(f"Agent details: {agent_details.name}")
        
        # Get agent card
        agent_card = client.get_agent_card(agent_id)
        print(f"API Base URL: {agent_card.api_base_url}")
```

### Advanced Search

```python
from a2a_reg_sdk import A2AClient

client = A2AClient(...)
client.authenticate()

# Basic text search
results = client.search_agents(
    query="chatbot AI assistant",
    page=1,
    limit=20
)

# Advanced search with filters
results = client.search_agents(
    query="natural language processing",
    filters={
        "tags": ["nlp", "ai"],
        "provider": "openai",
        "capabilities.protocols": ["http", "websocket"],
        "is_active": True
    },
    semantic=True,
    page=1,
    limit=10
)

print(f"Found {len(results['agents'])} matching agents")
for agent in results['agents']:
    print(f"- {agent['name']}: {agent['description']}")
```

### Publishing from Configuration

```python
from a2a_reg_sdk import AgentPublisher, A2AClient
import yaml

# Load configuration from file
with open("my-agent.yaml", "r") as f:
    agent_config = yaml.safe_load(f)

# Create client and publisher
client = A2AClient(...)
client.authenticate()
publisher = AgentPublisher(client)

# Load agent from file
agent = publisher.load_agent_from_file("my-agent.yaml")

# Validate
errors = publisher.validate_agent(agent)
if errors:
    print(f"Validation errors: {errors}")
else:
    # Publish
    published_agent = publisher.publish(agent, validate=True)
    print(f"Published: {published_agent.id}")
```

### Complex Agent with TEE

```python
from a2a_reg_sdk import (
    AgentBuilder, AgentCapabilities, AuthScheme, 
    AgentTeeDetails, AgentSkills, AgentCard
)

# Define capabilities
capabilities = AgentCapabilities(
    protocols=["https", "grpc"],
    supported_formats=["json", "protobuf"],
    max_request_size=104857600,  # 100MB
    max_concurrent_requests=200,
    a2a_version="1.0"
)

# Multiple auth schemes
auth_schemes = [
    AuthScheme(type="oauth2", required=True),
    AuthScheme(type="mtls", required=False),
    AuthScheme(type="jwt", required=False, header_name="Authorization")
]

# TEE details for secure execution
tee_details = AgentTeeDetails(
    enabled=True,
    provider="Intel SGX",
    attestation="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
)

# Skills definition
skills = AgentSkills(
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "context": {"type": "object"}
        },
        "required": ["query"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "response": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        },
        "required": ["response", "confidence"]
    },
    examples=[
        "Query: 'Analyze sales data' -> Response: 'Sales increased 15%', Confidence: 0.92"
    ]
)

# Agent card
agent_card = AgentCard(
    name="enterprise-ai",
    description="Enterprise AI agent with secure processing",
    version="2.0.0",
    author="Enterprise Corp",
    api_base_url="https://secure-api.enterprise.com/v2",
    capabilities=capabilities,
    auth_schemes=auth_schemes,
    endpoints={
        "analyze": "/analyze",
        "report": "/report",
        "health": "/health"
    },
    skills=skills
)

# Build complete agent
agent = AgentBuilder("enterprise-ai", "Enterprise AI Agent", "2.0.0", "enterprise-corp") \
    .with_tags(["enterprise", "ai", "secure", "analytics"]) \
    .with_location("https://secure-api.enterprise.com/v2/agent", "api_endpoint") \
    .with_capabilities(capabilities) \
    .with_auth_schemes(auth_schemes) \
    .with_tee_details(tee_details) \
    .with_skills(skills) \
    .with_agent_card(agent_card) \
    .public(False) \
    .active(True) \
    .build()

# Publish
client = A2AClient(...)
client.authenticate()
published_agent = client.publish_agent(agent)
```

### Error Handling

```python
from a2a_reg_sdk import (
    A2AClient, AuthenticationError, ValidationError, 
    NotFoundError, RateLimitError
)

client = A2AClient(...)

try:
    # Authenticate
    client.authenticate()
    
    # Try to get non-existent agent
    agent = client.get_agent("non-existent-id")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NotFoundError as e:
    print(f"Agent not found: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Batch Operations

```python
from a2a_reg_sdk import A2AClient, AgentPublisher

client = A2AClient(...)
client.authenticate()
publisher = AgentPublisher(client)

# Publish multiple agents
agent_configs = ["agent1.yaml", "agent2.yaml", "agent3.yaml"]
published_agents = []

for config_file in agent_configs:
    try:
        agent = publisher.load_agent_from_file(config_file)
        published_agent = publisher.publish(agent, validate=True)
        published_agents.append(published_agent)
        print(f"✓ Published {published_agent.name}")
    except Exception as e:
        print(f"✗ Failed to publish {config_file}: {e}")

print(f"Successfully published {len(published_agents)} agents")
```

## Configuration

### Environment Variables

```bash
export A2A_REGISTRY_URL="http://localhost:8000"
export A2A_CLIENT_ID="your-client-id"
export A2A_CLIENT_SECRET="your-client-secret"
```

### Configuration File

Create a `~/.a2a/config.yaml`:

```yaml
registry_url: "http://localhost:8000"
client_id: "your-client-id"
client_secret: "your-client-secret"
timeout: 30
```

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=a2a_reg_sdk

# Run specific test
pytest tests/test_client.py::test_authentication
```

## Documentation

- **API Reference**: Complete class and method documentation
- **Examples**: Comprehensive examples in the `examples/` directory
- **Agent Publishing Guide**: Step-by-step publishing guide
- **Best Practices**: Recommendations for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../LICENSE) file for details.

## Support

- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time help and discussions
- **Documentation**: [docs.a2areg.dev](https://docs.a2areg.dev)
- **Issues**: [GitHub Issues](https://github.com/a2areg/a2a-registry/issues)
- **Community**: [GitHub Discussions](https://github.com/a2areg/a2a-registry/discussions)
- **Examples**: [examples/python/](../../examples/python/)

## Changelog

### v1.0.0

- Initial release
- Basic agent management (CRUD operations)
- Search and discovery
- High-level publishing API
- Comprehensive data models
- Full type hints
- Context manager support
