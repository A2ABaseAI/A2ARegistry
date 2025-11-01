# A2A Registry TypeScript SDK

A TypeScript SDK for interacting with the A2A Agent Registry.

## Installation

```bash
npm install @a2areg/sdk
# or
yarn add @a2areg/sdk
# or
pnpm add @a2areg/sdk
```

## Usage

### Basic Setup

```typescript
import { A2ARegClient } from '@a2areg/sdk';

// Create client
const client = new A2ARegClient({
  registryUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Or with OAuth
const client = new A2ARegClient({
  registryUrl: 'http://localhost:8000',
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret'
});

// Authenticate (for OAuth)
await client.authenticate();
```

### Get Health Status

```typescript
const health = await client.getHealth();
console.log(health);
```

### List Agents

```typescript
// List public agents
const publicAgents = await client.listAgents(1, 20, true);

// List entitled agents (requires authentication)
const entitledAgents = await client.listAgents(1, 20, false);
```

### Get Agent

```typescript
const agent = await client.getAgent('agent-id');
console.log(agent.name, agent.description);
```

### Get Agent Card

```typescript
const card = await client.getAgentCard('agent-id');
console.log(card.skills);
```

### Search Agents

```typescript
const results = await client.searchAgents(
  'recipe',
  { tags: ['cooking'] },
  false, // semantic search
  1,      // page
  20      // limit
);
```

### Publish Agent

```typescript
import { agentFromDict } from '@a2areg/sdk';

const agent = agentFromDict({
  name: 'My Agent',
  description: 'A helpful agent',
  version: '1.0.0',
  provider: 'my-org',
  location_url: 'https://api.example.com/agent',
  tags: ['ai', 'assistant'],
  is_public: true
});

// Publish with validation
const published = await client.publishAgent(agent, true);
console.log('Published agent ID:', published.id);
```

### Update Agent

```typescript
const updated = await client.updateAgent('agent-id', {
  description: 'Updated description',
  version: '1.1.0'
});
```

### Delete Agent

```typescript
await client.deleteAgent('agent-id');
```

### Validate Agent

```typescript
const errors = client.validateAgent(agent);
if (errors.length > 0) {
  console.error('Validation errors:', errors);
}
```

### API Key Management

```typescript
// Generate API key
const { apiKey, keyInfo } = await client.generateApiKey(['read', 'write'], 30);

// Generate and authenticate
const { apiKey: newKey } = await client.generateApiKeyAndAuthenticate(['read', 'write']);

// Validate API key
const keyInfo = await client.validateApiKey('api-key', ['read']);

// List API keys
const keys = await client.listApiKeys(true);

// Revoke API key
await client.revokeApiKey('key-id');
```

## Error Handling

```typescript
import { A2ARegClient, AuthenticationError, ValidationError, NotFoundError } from '@a2areg/sdk';

try {
  const agent = await client.getAgent('agent-id');
} catch (error) {
  if (error instanceof NotFoundError) {
    console.error('Agent not found');
  } else if (error instanceof AuthenticationError) {
    console.error('Authentication failed');
  } else if (error instanceof ValidationError) {
    console.error('Validation failed:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Type Definitions

The SDK provides full TypeScript type definitions:

```typescript
import type { Agent, AgentCardSpec, AgentCapabilities } from '@a2areg/sdk';

function processAgent(agent: Agent): void {
  // TypeScript knows the structure of Agent
  console.log(agent.name, agent.version);
}
```

## Models

The SDK includes models for:

- `Agent` - Core agent representation
- `AgentCardSpec` - Agent card specification
- `AgentCapabilities` - Agent capabilities
- `SecurityScheme` - Authentication schemes
- `AgentSkill` - Agent skills
- `AgentInterface` - Transport interfaces
- `AgentProvider` - Provider information

## Development

```bash
# Build
npm run build

# Type check
npm run type-check

# Lint
npm run lint

# Test
npm test
```

## License

Apache-2.0

