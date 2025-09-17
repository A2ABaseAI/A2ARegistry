# A2A Python SDK Reference

Complete reference documentation for the A2A Python SDK.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Models](#models)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Installation

```bash
# Install from PyPI (when available)
pip install a2a-sdk

# Install from source
git clone https://github.com/a2areg/a2a-registry.git
cd a2a-registry/sdk/python
pip install -e .
```

## Quick Start

```python
from a2a_sdk import A2AClient, AgentBuilder

# Create and authenticate client
client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id", 
    client_secret="your-client-secret"
)
client.authenticate()

# Create and publish an agent
agent = AgentBuilder("my-agent", "Description", "1.0.0", "my-org").build()
published_agent = client.publish_agent(agent)

print(f"Published: {published_agent.id}")
```

## API Reference

### A2AClient

Main client class for interacting with the A2A Agent Registry.

#### Constructor

```python
A2AClient(
    registry_url: str = "http://localhost:8000",
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    timeout: int = 30
)
```

**Parameters:**
- `registry_url` - Base URL of the A2A registry
- `client_id` - OAuth client ID for authentication
- `client_secret` - OAuth client secret for authentication  
- `timeout` - Request timeout in seconds

#### Methods

##### authenticate()

```python
def authenticate() -> None
```

Authenticate with the registry using OAuth 2.0 client credentials flow.

**Raises:**
- `AuthenticationError` - If authentication fails

##### get_health()

```python
def get_health() -> Dict[str, Any]
```

Get registry health status.

**Returns:**
- Dictionary containing health status information

##### list_agents()

```python
def list_agents(
    page: int = 1,
    limit: int = 20, 
    public_only: bool = True
) -> Dict[str, Any]
```

List agents from the registry.

**Parameters:**
- `page` - Page number (1-based)
- `limit` - Number of agents per page
- `public_only` - Whether to only return public agents

**Returns:**
- Dictionary containing agents list and pagination info

##### get_agent()

```python
def get_agent(agent_id: str) -> Agent
```

Get a specific agent by ID.

**Parameters:**
- `agent_id` - The agent's unique identifier

**Returns:**
- `Agent` object

**Raises:**
- `NotFoundError` - If agent doesn't exist

##### get_agent_card()

```python
def get_agent_card(agent_id: str) -> AgentCard
```

Get an agent's card (detailed metadata).

**Parameters:**
- `agent_id` - The agent's unique identifier

**Returns:**
- `AgentCard` object

##### search_agents()

```python
def search_agents(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    semantic: bool = False,
    page: int = 1,
    limit: int = 20
) -> Dict[str, Any]
```

Search for agents in the registry.

**Parameters:**
- `query` - Search query string
- `filters` - Search filters (tags, capabilities, etc.)
- `semantic` - Whether to use semantic search
- `page` - Page number (1-based)
- `limit` - Number of results per page

**Returns:**
- Search results with agents and pagination info

##### publish_agent()

```python
def publish_agent(agent_data: Union[Dict[str, Any], Agent]) -> Agent
```

Publish a new agent to the registry.

**Parameters:**
- `agent_data` - Agent data as dict or Agent object

**Returns:**
- Published `Agent` object with assigned ID

**Raises:**
- `AuthenticationError` - If not authenticated
- `ValidationError` - If agent data is invalid

##### update_agent()

```python
def update_agent(
    agent_id: str, 
    agent_data: Union[Dict[str, Any], Agent]
) -> Agent
```

Update an existing agent.

**Parameters:**
- `agent_id` - The agent's unique identifier
- `agent_data` - Updated agent data as dict or Agent object

**Returns:**
- Updated `Agent` object

##### delete_agent()

```python
def delete_agent(agent_id: str) -> None
```

Delete an agent from the registry.

**Parameters:**
- `agent_id` - The agent's unique identifier

**Raises:**
- `NotFoundError` - If agent doesn't exist
- `AuthenticationError` - If not authorized

##### get_stats()

```python
def get_stats() -> Dict[str, Any]
```

Get registry statistics.

**Returns:**
- Registry statistics dictionary

### AgentPublisher

High-level publisher class for easier agent publishing and management.

#### Constructor

```python
AgentPublisher(client: A2AClient)
```

**Parameters:**
- `client` - Authenticated A2AClient instance

#### Methods

##### load_agent_from_file()

```python
def load_agent_from_file(file_path: Union[str, Path]) -> Agent
```

Load agent configuration from a file.

**Parameters:**
- `file_path` - Path to YAML or JSON configuration file

**Returns:**
- `Agent` object

**Raises:**
- `ValidationError` - If file cannot be loaded or parsed

##### validate_agent()

```python
def validate_agent(agent: Agent) -> List[str]
```

Validate an agent configuration.

**Parameters:**
- `agent` - Agent to validate

**Returns:**
- List of validation errors (empty if valid)

##### publish()

```python
def publish(agent: Agent, validate: bool = True) -> Agent
```

Publish an agent to the registry.

**Parameters:**
- `agent` - Agent to publish
- `validate` - Whether to validate before publishing

**Returns:**
- Published agent with assigned ID

##### create_sample_agent()

```python
def create_sample_agent(
    name: str,
    description: str,
    version: str = "1.0.0",
    provider: str = "my-org",
    api_url: Optional[str] = None
) -> Agent
```

Create a sample agent configuration.

**Parameters:**
- `name` - Agent name
- `description` - Agent description
- `version` - Agent version
- `provider` - Agent provider
- `api_url` - API base URL

**Returns:**
- Sample `Agent` configuration

### AgentBuilder

Fluent builder for creating Agent objects.

#### Constructor

```python
AgentBuilder(name: str, description: str, version: str, provider: str)
```

#### Methods

All methods return `self` for chaining:

```python
def with_tags(tags: List[str]) -> 'AgentBuilder'
def with_location(url: str, location_type: str = "api_endpoint") -> 'AgentBuilder'
def with_capabilities(capabilities: AgentCapabilities) -> 'AgentBuilder'
def with_auth_schemes(auth_schemes: List[AuthScheme]) -> 'AgentBuilder'
def with_tee_details(tee_details: AgentTeeDetails) -> 'AgentBuilder'
def with_skills(skills: AgentSkills) -> 'AgentBuilder'
def with_agent_card(agent_card: AgentCard) -> 'AgentBuilder'
def public(is_public: bool = True) -> 'AgentBuilder'
def active(is_active: bool = True) -> 'AgentBuilder'
def build() -> Agent
```

**Example:**

```python
agent = AgentBuilder("my-agent", "Description", "1.0.0", "my-org") \
    .with_tags(["ai", "nlp"]) \
    .with_location("https://api.example.com/agent") \
    .public(True) \
    .active(True) \
    .build()
```

## Models

### Agent

Main agent data model.

```python
@dataclass
class Agent:
    name: str
    description: str
    version: str
    provider: str
    id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_public: bool = True
    is_active: bool = True
    location_url: Optional[str] = None
    location_type: Optional[str] = None
    capabilities: Optional[AgentCapabilities] = None
    auth_schemes: List[AuthScheme] = field(default_factory=list)
    tee_details: Optional[AgentTeeDetails] = None
    skills: Optional[AgentSkills] = None
    agent_card: Optional[AgentCard] = None
    client_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### AgentCapabilities

Agent capabilities specification.

```python
@dataclass
class AgentCapabilities:
    protocols: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    max_request_size: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    a2a_version: Optional[str] = None
```

### AuthScheme

Authentication scheme specification.

```python
@dataclass
class AuthScheme:
    type: str
    description: Optional[str] = None
    required: bool = False
    header_name: Optional[str] = None
    query_param: Optional[str] = None
```

### AgentTeeDetails

Trusted Execution Environment details.

```python
@dataclass
class AgentTeeDetails:
    enabled: bool = False
    provider: Optional[str] = None
    attestation: Optional[str] = None
```

### AgentSkills

Agent skills specification with input/output schemas.

```python
@dataclass
class AgentSkills:
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
```

### AgentCard

Detailed agent metadata.

```python
@dataclass
class AgentCard:
    name: str
    description: str
    version: str
    author: str
    api_base_url: Optional[str] = None
    capabilities: Optional[AgentCapabilities] = None
    auth_schemes: List[AuthScheme] = field(default_factory=list)
    endpoints: Dict[str, str] = field(default_factory=dict)
    skills: Optional[AgentSkills] = None
```

## Examples

### Basic Agent Creation

```python
from a2a_sdk import AgentBuilder, AgentCapabilities, AuthScheme

capabilities = AgentCapabilities(
    protocols=["http"],
    supported_formats=["json"],
    max_concurrent_requests=10
)

auth_scheme = AuthScheme(
    type="api_key",
    required=True,
    header_name="X-API-Key"
)

agent = AgentBuilder("chatbot", "AI Chatbot", "1.0.0", "my-company") \
    .with_capabilities(capabilities) \
    .with_auth_schemes([auth_scheme]) \
    .with_tags(["ai", "chatbot"]) \
    .public(True) \
    .build()
```

### Publishing with High-Level API

```python
from a2a_sdk import create_quick_publisher

publisher = create_quick_publisher(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Create sample agent
agent = publisher.create_sample_agent(
    name="demo-agent",
    description="Demo agent for testing",
    provider="demo-corp"
)

# Publish with validation
published_agent = publisher.publish(agent, validate=True)
```

### Loading from Configuration File

```python
from a2a_sdk import AgentPublisher, A2AClient

client = A2AClient(...)
client.authenticate()
publisher = AgentPublisher(client)

# Load from file
agent = publisher.load_agent_from_file("agent.yaml")

# Validate
errors = publisher.validate_agent(agent)
if errors:
    print(f"Validation errors: {errors}")
else:
    # Publish
    published_agent = publisher.publish(agent)
```

### Searching and Discovery

```python
# Basic search
results = client.search_agents(query="chatbot AI")

# Advanced search with filters
results = client.search_agents(
    query="natural language processing",
    filters={
        "tags": ["nlp", "ai"],
        "provider": "openai",
        "capabilities.protocols": ["http"]
    },
    semantic=True,
    page=1,
    limit=20
)

for agent in results['agents']:
    print(f"{agent['name']} - {agent['description']}")
```

### Agent Management

```python
# List all agents
agents_response = client.list_agents(page=1, limit=50)

# Get specific agent
agent = client.get_agent("agent-id-123")

# Update agent
agent.description = "Updated description"
updated_agent = client.update_agent(agent.id, agent)

# Delete agent
client.delete_agent("agent-id-123")
```

## Error Handling

### Exception Hierarchy

```python
A2AError                    # Base exception
├── AuthenticationError     # Authentication failures
├── ValidationError         # Data validation errors  
├── NotFoundError          # Resource not found
├── RateLimitError         # Rate limit exceeded
└── ServerError            # Server-side errors
```

### Error Handling Examples

```python
from a2a_sdk import A2AClient, AuthenticationError, ValidationError, NotFoundError

client = A2AClient(...)

try:
    client.authenticate()
    agent = client.get_agent("nonexistent-id")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NotFoundError as e:
    print(f"Agent not found: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Validation Error Details

```python
from a2a_sdk import AgentPublisher

publisher = AgentPublisher(client)

# Validate agent
errors = publisher.validate_agent(agent)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Retry Logic

```python
import time
from a2a_sdk import A2AClient, RateLimitError

def publish_with_retry(client, agent, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.publish_agent(agent)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

## Context Manager Usage

```python
from a2a_sdk import A2AClient

# Use as context manager for automatic cleanup
with A2AClient(registry_url="...", client_id="...", client_secret="...") as client:
    client.authenticate()
    
    # Perform operations
    agents = client.list_agents()
    
    # Client automatically closed when exiting context
```

## Advanced Configuration

### Custom HTTP Session

```python
import requests
from a2a_sdk import A2AClient

# Create client with custom session
session = requests.Session()
session.headers.update({'User-Agent': 'MyApp/1.0'})

client = A2AClient(registry_url="...")
client.session = session
```

### Timeout Configuration

```python
# Set custom timeout
client = A2AClient(
    registry_url="...",
    timeout=60  # 60 seconds
)
```

### Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('a2a_sdk')
logger.setLevel(logging.DEBUG)
```

For more examples and advanced usage patterns, see the [examples directory](../examples/) in the repository.

## Getting Help

- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time help and discussions
- **Documentation**: Check the complete documentation and guides
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community discussions and Q&A
