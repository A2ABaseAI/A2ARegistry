# A2A Agent Publishing Guide

This guide explains how to publish and manage agents in the A2A Agent Registry using both the CLI tool and Python SDK.

## Table of Contents

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Agent Configuration](#agent-configuration)
- [Publishing Methods](#publishing-methods)
- [Management Operations](#management-operations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install the Publisher Tool

```bash
# Install from source
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/tools/a2a-publisher
pip install -r requirements.txt
python setup.py install

# Or install the SDK
cd ../../sdk/python
pip install -e .
```

### 2. Set Up Authentication

```bash
# Set environment variables
export A2A_REGISTRY_URL="http://localhost:8000"
export A2A_CLIENT_ID="your-client-id"
export A2A_CLIENT_SECRET="your-client-secret"
```

### 3. Create Your First Agent

```bash
# Initialize a new agent configuration
a2a-publisher init

# Edit the generated agent.yaml file with your agent details
# Then publish it
a2a-publisher publish agent.yaml
```

## Authentication

The A2A Registry uses OAuth 2.0 client credentials flow for authentication.

### Getting Client Credentials

1. **Register a Client**: Use the registry web UI or API to register a new OAuth client
2. **Get Credentials**: Save your client ID and secret securely
3. **Set Environment Variables**: Configure your environment for easy access

```bash
export A2A_CLIENT_ID="your-client-id-here"
export A2A_CLIENT_SECRET="your-client-secret-here"
```

### Authentication Scopes

Different operations require different scopes:

- `agent:read` - View public and entitled agents
- `agent:write` - Publish and update agents
- `agent:delete` - Delete agents
- `client:read` - View client information
- `client:write` - Manage client settings

## Agent Configuration

### Configuration File Format

Agents can be configured using YAML or JSON files. Here's a comprehensive example:

```yaml
# Basic agent information
name: "my-awesome-agent"
description: "An AI agent that provides helpful assistance"
version: "1.2.0"
provider: "my-organization"

# Tags for discovery
tags:
  - "ai"
  - "assistant"
  - "nlp"

# Visibility and status
is_public: true
is_active: true

# Agent location
location_url: "https://api.my-org.com/agent"
location_type: "api_endpoint"

# Capabilities
capabilities:
  protocols:
    - "http"
    - "websocket"
  supported_formats:
    - "json"
    - "xml"
  max_request_size: 1048576  # 1MB
  max_concurrent_requests: 10
  a2a_version: "1.0"

# Authentication schemes
auth_schemes:
  - type: "api_key"
    description: "API key authentication"
    required: true
    header_name: "X-API-Key"
  - type: "oauth2"
    description: "OAuth 2.0 authentication"
    required: false

# TEE (Trusted Execution Environment) details
tee_details:
  enabled: false
  provider: null
  attestation: null

# Agent card (detailed metadata)
agent_card:
  name: "my-awesome-agent"
  description: "An AI agent that provides helpful assistance"
  version: "1.2.0"
  author: "My Organization"
  api_base_url: "https://api.my-org.com/v1"
  
  capabilities:
    protocols: ["http", "websocket"]
    supported_formats: ["json", "xml"]
    max_request_size: 1048576
    max_concurrent_requests: 10
    a2a_version: "1.0"
  
  auth_schemes:
    - type: "api_key"
      description: "API key authentication"
      required: true
      header_name: "X-API-Key"
  
  endpoints:
    chat: "/chat"
    status: "/status"
    capabilities: "/capabilities"
  
  skills:
    input_schema:
      type: "object"
      properties:
        message:
          type: "string"
          description: "User message"
        context:
          type: "object"
          description: "Optional context"
      required: ["message"]
    
    output_schema:
      type: "object"
      properties:
        response:
          type: "string"
          description: "Agent response"
        confidence:
          type: "number"
          minimum: 0.0
          maximum: 1.0
      required: ["response", "confidence"]
    
    examples:
      - "Input: {'message': 'Hello'} -> Output: {'response': 'Hi!', 'confidence': 0.95}"
```

### Required Fields

The following fields are required for all agents:

- `name` - Unique agent name
- `description` - Agent description
- `version` - Semantic version (e.g., "1.0.0")
- `provider` - Organization or provider name
- `agent_card` - Detailed metadata object

### Optional Fields

- `tags` - Array of tags for discovery
- `is_public` - Whether the agent is publicly discoverable (default: true)
- `is_active` - Whether the agent is currently active (default: true)
- `location_url` - Agent API endpoint URL
- `location_type` - Type of location ("api_endpoint", "container", etc.)
- `capabilities` - Agent capabilities specification
- `auth_schemes` - Supported authentication methods
- `tee_details` - Trusted Execution Environment details
- `skills` - Input/output schemas and examples

## Publishing Methods

### CLI Tool

The `a2a-publisher` CLI tool provides a simple command-line interface:

```bash
# Initialize a new agent configuration
a2a-publisher init --output my-agent.yaml

# Publish an agent
a2a-publisher publish my-agent.yaml

# List published agents
a2a-publisher list

# Update an agent
a2a-publisher update <agent-id> my-agent.yaml

# Delete an agent
a2a-publisher delete <agent-id>
```

### Python SDK

Use the Python SDK for programmatic publishing:

```python
from a2a_sdk import A2AClient, AgentBuilder, AgentCapabilities, AuthScheme

# Create client
client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Authenticate
client.authenticate()

# Create agent
agent = AgentBuilder("my-agent", "Description", "1.0.0", "my-org") \
    .with_tags(["ai", "assistant"]) \
    .with_location("https://api.my-org.com/agent") \
    .public(True) \
    .build()

# Publish
published_agent = client.publish_agent(agent)
print(f"Published agent with ID: {published_agent.id}")
```

### High-Level Publisher

Use the `AgentPublisher` class for advanced features:

```python
from a2a_sdk import A2AClient, AgentPublisher

client = A2AClient(...)
client.authenticate()

publisher = AgentPublisher(client)

# Create sample agent
sample_agent = publisher.create_sample_agent(
    name="sample-agent",
    description="A sample agent",
    version="1.0.0",
    provider="my-org",
    api_url="https://api.my-org.com"
)

# Validate and publish
published_agent = publisher.publish(sample_agent, validate=True)
```

## Management Operations

### Listing Agents

```bash
# CLI
a2a-publisher list --page 1 --limit 20

# Python
agents_response = client.list_agents(page=1, limit=20)
for agent in agents_response['agents']:
    print(f"{agent['name']} - {agent['version']}")
```

### Searching Agents

```python
# Search with filters
results = client.search_agents(
    query="chatbot AI",
    filters={"tags": ["nlp"], "provider": "my-org"},
    semantic=True,
    page=1,
    limit=10
)
```

### Updating Agents

```bash
# CLI
a2a-publisher update <agent-id> updated-agent.yaml

# Python
updated_agent = client.update_agent(agent_id, updated_data)
```

### Deleting Agents

```bash
# CLI
a2a-publisher delete <agent-id>

# Python
client.delete_agent(agent_id)
```

## Best Practices

### Configuration Management

1. **Version Control**: Store agent configurations in version control
2. **Environment-Specific Configs**: Use different configs for dev/staging/prod
3. **Secrets Management**: Never store API keys in configuration files
4. **Validation**: Always validate configurations before publishing

### Agent Design

1. **Clear Naming**: Use descriptive, unique names
2. **Semantic Versioning**: Follow semantic versioning (major.minor.patch)
3. **Comprehensive Descriptions**: Provide detailed descriptions
4. **Proper Tagging**: Use relevant tags for discoverability
5. **Schema Documentation**: Define clear input/output schemas

### Security

1. **Authentication**: Always use secure authentication schemes
2. **TEE Support**: Consider Trusted Execution Environment for sensitive agents
3. **Access Control**: Use appropriate public/private visibility settings
4. **Regular Updates**: Keep agent configurations and dependencies updated

### Performance

1. **Resource Limits**: Set appropriate request size and concurrency limits
2. **Caching**: Implement caching where appropriate
3. **Monitoring**: Monitor agent performance and usage
4. **Optimization**: Regularly review and optimize agent configurations

## Troubleshooting

### Common Issues

#### Authentication Errors

```
Error: Authentication failed
```

**Solutions**:
- Verify client ID and secret are correct
- Check that the client has necessary scopes
- Ensure the registry URL is accessible
- Verify network connectivity

#### Validation Errors

```
Error: Agent card validation errors: Missing required field: name
```

**Solutions**:
- Check all required fields are present
- Validate JSON/YAML syntax
- Ensure data types match schema requirements
- Review field naming and structure

#### Publishing Conflicts

```
Error: Agent with this name already exists
```

**Solutions**:
- Use unique agent names
- Update existing agents instead of creating new ones
- Use versioning to manage agent updates
- Consider using namespaced names

#### Network Issues

```
Error: Failed to connect to registry
```

**Solutions**:
- Verify registry URL is correct and accessible
- Check firewall and proxy settings
- Ensure registry service is running
- Test connectivity with curl or ping

### Debug Mode

Enable debug logging for detailed error information:

```bash
# CLI with verbose output
a2a-publisher --verbose publish agent.yaml

# Python with logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Documentation**: Check the complete documentation at docs.a2areg.dev
2. **Examples**: Review examples in the `examples/` directory
3. **Community**: Join the community discussions on GitHub
4. **Issues**: Report bugs and feature requests on GitHub Issues

## API Reference

### CLI Commands

- `init` - Initialize new agent configuration
- `publish` - Publish agent to registry
- `update` - Update existing agent
- `list` - List published agents
- `delete` - Delete agent from registry

### Python SDK Classes

- `A2AClient` - Main registry client
- `AgentPublisher` - High-level publishing interface
- `AgentBuilder` - Fluent agent builder
- `Agent` - Agent data model
- `AgentCard` - Agent metadata model

For complete API documentation, see the [SDK Reference](SDK_REFERENCE.md).
