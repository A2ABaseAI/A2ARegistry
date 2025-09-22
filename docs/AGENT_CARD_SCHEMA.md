# Agent Card Schema Documentation

## Overview

The A2A Registry now uses a standardized Agent Card schema that follows the [A2A Protocol specification](https://a2a-protocol.org/dev/specification/#355-extension-method-naming). This ensures full compliance with the A2A Protocol and interoperability across different implementations.

## Schema Structure

The Agent Card schema is defined in `app/schemas/agent_card_spec.py` and follows the A2A Protocol specification (Section 5.5 - AgentCard Object Structure):

```typescript
interface AgentCard {
  // Core identification fields
  name: string;                    // Human-readable name for the Agent
  description: string;             // Human-readable description of the Agent's function
  url: string;                    // URL address where the Agent is hosted
  version: string;                 // Version of the Agent
  
  // A2A Protocol objects (Section 5.5)
  provider?: AgentProvider;       // Section 5.5.1 - Service provider information
  capabilities: AgentCapabilities; // Section 5.5.2 - Optional capabilities supported
  securitySchemes: SecurityScheme[]; // Section 5.5.3 - Authentication requirements
  skills: AgentSkill[];           // Section 5.5.4 - Collection of capability units
  interface: AgentInterface;       // Section 5.5.5 - Transport and interaction capabilities
  
  // Optional fields
  documentationUrl?: string;      // URL for the Agent's documentation
  signature?: AgentCardSignature;  // Section 5.5.6 - Digital signature information
}

// A2A Protocol Object Definitions
interface AgentProvider {
  organization: string;           // Organization name
  url: string;                    // Organization URL
}

interface AgentCapabilities {
  streaming?: boolean;            // If the Agent supports Server-Sent Events (SSE)
  pushNotifications?: boolean;    // If the Agent can push update notifications to the client
  stateTransitionHistory?: boolean; // If the Agent exposes task state change history
  supportsAuthenticatedExtendedCard?: boolean; // If the Agent supports authenticated extended card retrieval
}

interface SecurityScheme {
  type: string;                   // Authentication type (apiKey, oauth2, jwt, mTLS)
  location?: string;              // Location of credentials (header, query, body)
  name?: string;                  // Parameter name for credentials
  flow?: string;                  // OAuth2 flow type
  tokenUrl?: string;              // OAuth2 token URL
  scopes?: string[];              // OAuth2 scopes
  credentials?: string;           // Credentials for the client to use for private Cards
}

interface AgentSkill {
  id: string;                     // Unique identifier for the skill
  name: string;                   // Human-readable name for the skill
  description: string;            // Skill description
  tags: string[];                 // Tags describing the skill's capability category
  examples?: string[];            // Example scenarios or prompts the skill can execute
  inputModes?: string[];          // Input MIME types supported by the skill
  outputModes?: string[];         // Output MIME types supported by the skill
}

interface AgentInterface {
  preferredTransport: string;     // Preferred transport protocol (jsonrpc, grpc, http)
  additionalInterfaces?: Array<{  // Additional transport interfaces supported
    transport: string;
    url: string;
  }>;
  defaultInputModes: string[];    // Supported input MIME types
  defaultOutputModes: string[];  // Supported output MIME types
}

interface AgentCardSignature {
  algorithm?: string;             // Signature algorithm used
  signature?: string;             // Digital signature value
  jwksUrl?: string;               // JWKS URL for signature verification
}
```

## Required Fields

The following fields are **required** for all Agent Cards:

### Core Identification
- `name`: Human-readable name for the Agent
- `description`: Human-readable description of the Agent's function
- `url`: URL address where the Agent is hosted
- `version`: Version of the Agent

### A2A Protocol Objects
- `capabilities`: AgentCapabilities object containing capability flags
- `securitySchemes`: Array of SecurityScheme objects for authentication
- `skills`: Array of AgentSkill objects representing capability units
- `interface`: AgentInterface object for transport and interaction capabilities

## Optional Fields

The following fields are **optional**:

- `provider`: AgentProvider object with service provider information
- `documentationUrl`: URL for the Agent's documentation
- `signature`: AgentCardSignature object for digital signature information

## Field Details

### AgentCapabilities

The `capabilities` object supports the following boolean flags:

- `streaming`: Whether the Agent supports Server-Sent Events (SSE)
- `pushNotifications`: Whether the Agent can push update notifications to the client
- `stateTransitionHistory`: Whether the Agent exposes task state change history
- `supportsAuthenticatedExtendedCard`: Whether the Agent supports authenticated extended card retrieval

### SecuritySchemes

The `securitySchemes` array contains SecurityScheme objects with:

**Required fields:**
- `type`: Authentication type (`apiKey`, `oauth2`, `jwt`, `mTLS`)

**Optional fields:**
- `location`: Location of credentials (`header`, `query`, `body`)
- `name`: Parameter name for credentials
- `flow`: OAuth2 flow type (`client_credentials`, `authorization_code`, etc.)
- `tokenUrl`: OAuth2 token URL
- `scopes`: Array of OAuth2 scopes
- `credentials`: Credentials for private Cards

### AgentInterface

The `interface` object contains:

**Required fields:**
- `preferredTransport`: Preferred transport protocol (`jsonrpc`, `grpc`, `http`)
- `defaultInputModes`: Array of supported input MIME types
- `defaultOutputModes`: Array of supported output MIME types

**Optional fields:**
- `additionalInterfaces`: Array of additional transport interfaces with `transport` and `url` properties

### AgentSkills

Each skill in the `skills` array must have:

- `id`: Unique identifier for the skill
- `name`: Human-readable name for the skill
- `description`: Skill description
- `tags`: Array of tags describing the skill's capability category

Optional skill fields:

- `examples`: Array of example scenarios or prompts
- `inputModes`: Array of input MIME types (if different from default)
- `outputModes`: Array of output MIME types (if different from default)

### AgentCardSignature

The optional `signature` object contains:

- `algorithm`: Signature algorithm used (e.g., `RS256`, `ES256`)
- `signature`: Digital signature value
- `jwksUrl`: JWKS URL for signature verification

## Example Agent Cards

### Recipe Agent

```json
{
  "name": "Recipe Agent",
  "description": "An AI agent that helps users find and create recipes based on available ingredients and dietary preferences",
  "url": "https://recipe-agent.example.com",
  "version": "1.0.0",
  "provider": {
    "organization": "Culinary AI Solutions",
    "url": "https://culinary-ai.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true,
    "supportsAuthenticatedExtendedCard": false
  },
  "securitySchemes": [
    {
      "type": "apiKey",
      "location": "header",
      "name": "X-API-Key",
      "credentials": "api_key_for_private_recipes"
    },
    {
      "type": "oauth2",
      "flow": "client_credentials",
      "tokenUrl": "https://culinary-ai.com/oauth/token",
      "scopes": ["read", "write"]
    }
  ],
  "skills": [
    {
      "id": "find_recipe",
      "name": "Find Recipe",
      "description": "Find recipes based on ingredients and dietary preferences",
      "tags": ["cooking", "recipe", "food"],
      "examples": [
        "I need a recipe for bread",
        "Find vegetarian pasta recipes",
        "What can I make with chicken and rice?"
      ],
      "inputModes": ["text/plain"],
      "outputModes": ["application/json"]
    }
  ],
  "interface": {
    "preferredTransport": "jsonrpc",
    "additionalInterfaces": [
      {
        "transport": "http",
        "url": "https://recipe-agent.example.com/api"
      }
    ],
    "defaultInputModes": ["text/plain", "application/json"],
    "defaultOutputModes": ["text/plain", "application/json"]
  },
  "documentationUrl": "https://recipe-agent.example.com/docs",
  "signature": {
    "algorithm": "RS256",
    "jwksUrl": "https://recipe-agent.example.com/.well-known/jwks.json"
  }
}
```

### Customer Support Agent

```json
{
  "name": "Customer Support Agent",
  "description": "Intelligent customer support agent that handles inquiries, provides solutions, and escalates complex issues",
  "url": "https://support-agent.company.com",
  "version": "2.1.0",
  "provider": {
    "organization": "Enterprise Solutions Inc",
    "url": "https://enterprise-solutions.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true,
    "supportsAuthenticatedExtendedCard": true
  },
  "securitySchemes": [
    {
      "type": "oauth2",
      "flow": "client_credentials",
      "tokenUrl": "https://enterprise-solutions.com/oauth/token",
      "scopes": ["support", "tickets", "analytics"]
    },
    {
      "type": "jwt",
      "location": "header",
      "name": "Authorization",
      "credentials": "jwt_token_for_authenticated_users"
    }
  ],
  "skills": [
    {
      "id": "ticket_creation",
      "name": "Create Support Ticket",
      "description": "Create and manage customer support tickets",
      "tags": ["support", "ticket", "customer-service"],
      "examples": [
        "I need help with my account",
        "Create a ticket for billing issue",
        "Report a bug in the application"
      ],
      "inputModes": ["text/plain", "multipart/form-data"],
      "outputModes": ["application/json"]
    }
  ],
  "interface": {
    "preferredTransport": "jsonrpc",
    "additionalInterfaces": [
      {
        "transport": "http",
        "url": "https://support-agent.company.com/api"
      },
      {
        "transport": "grpc",
        "url": "https://support-agent.company.com:443"
      }
    ],
    "defaultInputModes": ["text/plain", "application/json", "multipart/form-data"],
    "defaultOutputModes": ["text/plain", "application/json"]
  },
  "documentationUrl": "https://support-agent.company.com/docs"
}
```

## Validation

The schema is validated using Pydantic v2, which ensures:

- All required fields are present
- Field types are correct
- URLs are valid
- Arrays contain the expected data types

## Migration from Legacy Schema

If you have existing agent cards using the legacy schema, you'll need to update them to match the new A2A Protocol structure:

### Major Changes Required

1. **Remove deprecated fields**: `protocolVersion`, `authSchemes`, `extensions`, `jwks`, `jwks_uri`

2. **Restructure authentication**: 
   - **Old**: `authentication: { schemes: [...], credentials: "..." }`
   - **New**: `securitySchemes: [{ type: "apiKey", location: "header", name: "X-API-Key", credentials: "..." }]`

3. **Restructure transport and I/O modes**:
   - **Old**: `defaultInputModes: [...]`, `defaultOutputModes: [...]`
   - **New**: `interface: { preferredTransport: "jsonrpc", defaultInputModes: [...], defaultOutputModes: [...] }`

4. **Add required A2A Protocol fields**:
   - `capabilities`: Must include at least one capability flag
   - `securitySchemes`: Array of security scheme objects
   - `interface`: Transport and interaction capabilities

5. **Update skill structure**: Ensure all skills have required `tags` field

6. **Add optional A2A Protocol fields**:
   - `signature`: For digital signature support
   - `interface.additionalInterfaces`: For multiple transport support

### Migration Example

**Before (Legacy Schema):**
```json
{
  "name": "My Agent",
  "description": "A test agent",
  "url": "https://my-agent.com",
  "authentication": {
    "schemes": ["Bearer"],
    "credentials": "api_key"
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": []
}
```

**After (A2A Protocol Schema):**
```json
{
  "name": "My Agent",
  "description": "A test agent",
  "url": "https://my-agent.com",
  "version": "1.0.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "securitySchemes": [
    {
      "type": "apiKey",
      "location": "header",
      "name": "Authorization",
      "credentials": "api_key"
    }
  ],
  "skills": [],
  "interface": {
    "preferredTransport": "jsonrpc",
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"]
  }
}
```

## Testing

The schema is thoroughly tested with:

- Valid data validation
- Invalid data rejection
- Serialization/deserialization
- Field type validation
- Optional field handling

Run the tests with:

```bash
python -m pytest tests/test_schemas.py -v
```

## Files

- **Schema Definition**: `app/schemas/agent_card_spec.py` - A2A Protocol-compliant Pydantic models
- **Example Cards**: 
  - `examples/configs/recipe-agent.json` - Simple recipe agent with JSON-RPC transport
  - `examples/configs/customer-support-agent.json` - Support agent with multiple transports
  - `examples/configs/enterprise-agent.json` - Enterprise agent with gRPC and advanced security
- **Tests**: `tests/test_schemas.py` - Comprehensive schema validation tests
- **Documentation**: `docs/AGENT_CARD_SCHEMA.md` - This documentation file

## A2A Protocol Compliance

This schema implementation is fully compliant with the [A2A Protocol specification](https://a2a-protocol.org/dev/specification/#355-extension-method-naming), specifically:

- **Section 5.5.1**: AgentProvider Object
- **Section 5.5.2**: AgentCapabilities Object  
- **Section 5.5.3**: SecurityScheme Object
- **Section 5.5.4**: AgentSkill Object
- **Section 5.5.5**: AgentInterface Object
- **Section 5.5.6**: AgentCardSignature Object

This ensures interoperability with other A2A Protocol-compliant agents and clients in the ecosystem.
