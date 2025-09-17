# A2A Agent Publisher CLI

A command-line tool for publishing and managing agents in the A2A Agent Registry.

## Installation

### From Source

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/tools/a2a-publisher
pip install -r requirements.txt
python setup.py install
```

### Using pip (when available)

```bash
pip install a2a-publisher
```

## Quick Start

1. **Set up authentication**:
   ```bash
   export A2A_REGISTRY_URL="http://localhost:8000"
   export A2A_CLIENT_ID="your-client-id"
   export A2A_CLIENT_SECRET="your-client-secret"
   ```

2. **Initialize a new agent configuration**:
   ```bash
   a2a-publisher init
   ```

3. **Edit the generated `agent.yaml` file with your agent details**

4. **Publish your agent**:
   ```bash
   a2a-publisher publish agent.yaml
   ```

## Commands

### `init` - Initialize Agent Configuration

Create a new agent configuration file with sample values.

```bash
a2a-publisher init [--output FILE]
```

**Options:**
- `-o, --output FILE` - Output file path (default: agent.yaml)

**Example:**
```bash
a2a-publisher init --output my-agent.yaml
```

### `publish` - Publish Agent

Publish an agent to the registry from a configuration file.

```bash
a2a-publisher publish CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE` - Path to agent configuration file (YAML or JSON)

**Example:**
```bash
a2a-publisher publish agent.yaml
```

### `update` - Update Agent

Update an existing agent with new configuration.

```bash
a2a-publisher update AGENT_ID CONFIG_FILE
```

**Arguments:**
- `AGENT_ID` - ID of the agent to update
- `CONFIG_FILE` - Path to updated configuration file

**Example:**
```bash
a2a-publisher update agent-123 updated-agent.yaml
```

### `list` - List Agents

List published agents in the registry.

```bash
a2a-publisher list [--page PAGE] [--limit LIMIT]
```

**Options:**
- `--page PAGE` - Page number (default: 1)
- `--limit LIMIT` - Results per page (default: 20)

**Example:**
```bash
a2a-publisher list --page 2 --limit 10
```

### `delete` - Delete Agent

Delete an agent from the registry.

```bash
a2a-publisher delete AGENT_ID
```

**Arguments:**
- `AGENT_ID` - ID of the agent to delete

**Example:**
```bash
a2a-publisher delete agent-123
```

## Configuration

### Environment Variables

- `A2A_REGISTRY_URL` - Registry URL (default: http://localhost:8000)
- `A2A_CLIENT_ID` - OAuth client ID for authentication
- `A2A_CLIENT_SECRET` - OAuth client secret for authentication

### Command Line Options

You can also specify configuration via command line flags:

```bash
a2a-publisher --registry-url http://localhost:8000 \
              --client-id your-client-id \
              --client-secret your-client-secret \
              publish agent.yaml
```

## Agent Configuration File

The agent configuration file defines your agent's metadata, capabilities, and settings.

### Basic Structure (YAML)

```yaml
# Required fields
name: "my-agent"
description: "Description of what my agent does"
version: "1.0.0"
provider: "my-organization"

# Optional fields
tags:
  - "ai"
  - "assistant"
is_public: true
is_active: true
location_url: "https://api.my-org.com/agent"

# Capabilities
capabilities:
  protocols: ["http"]
  supported_formats: ["json"]
  max_concurrent_requests: 10

# Authentication
auth_schemes:
  - type: "api_key"
    required: true
    header_name: "X-API-Key"

# Agent card (detailed metadata)
agent_card:
  name: "my-agent"
  description: "Description of what my agent does"
  version: "1.0.0"
  author: "My Organization"
  api_base_url: "https://api.my-org.com/v1"
  endpoints:
    chat: "/chat"
    status: "/status"
```

### JSON Format

```json
{
  "name": "my-agent",
  "description": "Description of what my agent does",
  "version": "1.0.0",
  "provider": "my-organization",
  "tags": ["ai", "assistant"],
  "is_public": true,
  "is_active": true,
  "location_url": "https://api.my-org.com/agent",
  "capabilities": {
    "protocols": ["http"],
    "supported_formats": ["json"],
    "max_concurrent_requests": 10
  },
  "auth_schemes": [
    {
      "type": "api_key",
      "required": true,
      "header_name": "X-API-Key"
    }
  ],
  "agent_card": {
    "name": "my-agent",
    "description": "Description of what my agent does",
    "version": "1.0.0",
    "author": "My Organization",
    "api_base_url": "https://api.my-org.com/v1"
  }
}
```

## Examples

### Complete Workflow

```bash
# 1. Set up environment
export A2A_REGISTRY_URL="https://registry.a2areg.dev"
export A2A_CLIENT_ID="your-client-id"
export A2A_CLIENT_SECRET="your-client-secret"

# 2. Initialize configuration
a2a-publisher init --output chatbot.yaml

# 3. Edit chatbot.yaml with your agent details

# 4. Publish the agent
a2a-publisher publish chatbot.yaml

# 5. List all agents to see yours
a2a-publisher list

# 6. Update the agent
# Edit chatbot.yaml with changes
a2a-publisher update agent-123 chatbot.yaml

# 7. Clean up (if needed)
a2a-publisher delete agent-123
```

### Enterprise Agent Example

```yaml
name: "enterprise-analytics"
description: "Enterprise analytics agent with advanced security"
version: "2.1.0"
provider: "enterprise-corp"
tags:
  - "enterprise"
  - "analytics"
  - "secure"
is_public: false
is_active: true
location_url: "https://secure-api.enterprise-corp.com/analytics"

capabilities:
  protocols: ["https", "grpc"]
  supported_formats: ["json", "protobuf"]
  max_request_size: 104857600  # 100MB
  max_concurrent_requests: 100
  a2a_version: "1.0"

auth_schemes:
  - type: "oauth2"
    description: "OAuth 2.0 authentication"
    required: true
  - type: "mtls"
    description: "Mutual TLS authentication"
    required: false

tee_details:
  enabled: true
  provider: "Intel SGX"
  attestation: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

agent_card:
  name: "enterprise-analytics"
  description: "Enterprise analytics agent with advanced security"
  version: "2.1.0"
  author: "Enterprise Corp"
  api_base_url: "https://secure-api.enterprise-corp.com/v2"
  endpoints:
    analyze: "/analyze"
    report: "/report"
    health: "/health"
  skills:
    input_schema:
      type: "object"
      properties:
        data_source:
          type: "object"
          properties:
            type:
              type: "string"
              enum: ["database", "file", "api"]
        analysis_type:
          type: "string"
          enum: ["descriptive", "predictive"]
      required: ["data_source", "analysis_type"]
    output_schema:
      type: "object"
      properties:
        results:
          type: "object"
        insights:
          type: "array"
          items:
            type: "string"
      required: ["results"]
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```
Error: Authentication failed
```

**Solutions:**
- Verify your client ID and secret are correct
- Check that your client has the necessary scopes
- Ensure the registry URL is accessible

#### Validation Errors

```
Error: Agent card validation errors: Missing required field: name
```

**Solutions:**
- Check that all required fields are present in your configuration
- Validate your YAML/JSON syntax
- Review the field names and data types

#### Network Issues

```
Error: Failed to connect to registry
```

**Solutions:**
- Verify the registry URL is correct
- Check your network connection
- Ensure the registry service is running

### Debug Mode

Use the `--verbose` flag for detailed error information:

```bash
a2a-publisher --verbose publish agent.yaml
```

### Getting Help

```bash
# General help
a2a-publisher --help

# Command-specific help
a2a-publisher publish --help
```

## Development

### Running from Source

```bash
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/tools/a2a-publisher

# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py --help
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=a2a_publisher tests/
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../LICENSE) file for details.

## Support

- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time help and discussions
- **Documentation**: [docs.a2areg.dev](https://docs.a2areg.dev)
- **Issues**: [GitHub Issues](https://github.com/a2areg/a2a-registry/issues)
- **Community**: [GitHub Discussions](https://github.com/a2areg/a2a-registry/discussions)
