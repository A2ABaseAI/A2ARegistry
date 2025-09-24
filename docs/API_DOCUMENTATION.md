# A2A Agent Registry API Documentation

Complete REST API documentation for the A2A Agent Registry.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Common Response Formats](#common-response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [WebSocket API](#websocket-api)
- [SDKs](#sdks)

## Overview

The A2A Agent Registry provides a RESTful API for managing and discovering AI agents. The API supports:

- Agent registration and management
- Agent discovery and search
- Authentication and authorization
- Real-time notifications via WebSocket
- Comprehensive metadata management

## Authentication

The API uses OAuth 2.0 with the client credentials flow for authentication.

### Getting Access Tokens

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "agent:read agent:write"
}
```

### Using Access Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Scopes

- `agent:read` - Read access to public and entitled agents
- `agent:write` - Create and update agents
- `agent:delete` - Delete agents
- `client:read` - Read client information
- `client:write` - Manage client settings
- `admin` - Administrative access

## Base URL

```
http://localhost:8000  # Development
https://api.a2areg.dev # Production
```

## Common Response Formats

### Success Response

```json
{
  "id": "agent-123",
  "name": "my-agent",
  "version": "1.0.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Paginated Response

```json
{
  "agents": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8
}
```

### Error Response

```json
{
  "error": "Validation error",
  "detail": "Agent name is required",
  "status_code": 422,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-123"
}
```

## Error Handling

### HTTP Status Codes

- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 422,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-123",
  "errors": [
    {
      "field": "name",
      "message": "This field is required"
    }
  ]
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Public endpoints**: 100 requests per minute
- **Authenticated endpoints**: 1000 requests per minute
- **Admin endpoints**: 10000 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
```

## Endpoints

### Health Check

#### Get Health Status

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1642248600,
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5
    },
    "redis": {
      "status": "healthy", 
      "response_time_ms": 2
    },
    "elasticsearch": {
      "status": "healthy",
      "response_time_ms": 12
    }
  },
  "metrics": {
    "total_agents": 1250,
    "active_agents": 1180,
    "public_agents": 850
  },
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 60.1
  }
}
```

### Statistics

#### Get Registry Statistics

```http
GET /stats
```

**Response:**
```json
{
  "agents": {
    "total": 1250,
    "public": 850,
    "private": 400,
    "active": 1180,
    "inactive": 70
  },
  "clients": {
    "total": 150,
    "active": 140
  },
  "peer_registries": {
    "total": 5,
    "connected": 4
  }
}
```

### Agents

#### List Public Agents

```http
GET /agents/public?page=1&limit=20
```

**Response:**
```json
{
  "agents": [
    {
      "id": "agent-123",
      "name": "chatbot-assistant",
      "description": "AI chatbot for customer support",
      "version": "1.2.0",
      "provider": "ai-corp",
      "tags": ["ai", "chatbot", "support"],
      "is_public": true,
      "is_active": true,
      "location": {
        "url": "https://api.ai-corp.com/chatbot",
        "type": "api_endpoint"
      },
      "capabilities": {
        "protocols": ["http", "websocket"],
        "supported_formats": ["json"],
        "max_concurrent_requests": 100
      },
      "auth_schemes": [
        {
          "type": "api_key",
          "required": true,
          "header_name": "X-API-Key"
        }
      ],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-16T14:20:00Z"
    }
  ],
  "total": 850,
  "page": 1,
  "limit": 20,
  "total_pages": 43
}
```

#### Get Agent by ID

```http
GET /agents/{agent_id}
```

**Response:**
```json
{
  "id": "agent-123",
  "name": "chatbot-assistant",
  "description": "AI chatbot for customer support",
  "version": "1.2.0",
  "provider": "ai-corp",
  "tags": ["ai", "chatbot", "support"],
  "is_public": true,
  "is_active": true,
  "location": {
    "url": "https://api.ai-corp.com/chatbot",
    "type": "api_endpoint"
  },
  "capabilities": {
    "protocols": ["http", "websocket"],
    "supported_formats": ["json"],
    "max_concurrent_requests": 100,
    "a2a_version": "1.0"
  },
  "auth_schemes": [
    {
      "type": "api_key",
      "description": "API key authentication",
      "required": true,
      "header_name": "X-API-Key"
    }
  ],
  "tee_details": {
    "enabled": false
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z"
}
```

#### Get Agent Card

```http
GET /agents/{agent_id}/card
```

**Response:**
```json
{
  "name": "chatbot-assistant",
  "description": "AI chatbot for customer support",
  "version": "1.2.0",
  "author": "AI Corp",
  "api_base_url": "https://api.ai-corp.com/v1",
  "capabilities": {
    "protocols": ["http", "websocket"],
    "supported_formats": ["json"],
    "max_request_size": 1048576,
    "max_concurrent_requests": 100,
    "a2a_version": "1.0"
  },
  "auth_schemes": [
    {
      "type": "api_key",
      "description": "API key authentication",
      "required": true,
      "header_name": "X-API-Key"
    }
  ],
  "endpoints": {
    "chat": "/chat",
    "status": "/status",
    "capabilities": "/capabilities"
  },
  "skills": {
    "input_schema": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string",
          "description": "User message"
        }
      },
      "required": ["message"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "response": {
          "type": "string"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      },
      "required": ["response", "confidence"]
    },
    "examples": [
      "Input: {'message': 'Hello'} -> Output: {'response': 'Hi!', 'confidence': 0.95}"
    ]
  }
}
```

#### Create Agent

```http
POST /agents
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "my-new-agent",
  "description": "A new AI agent",
  "version": "1.0.0",
  "provider": "my-company",
  "tags": ["ai", "assistant"],
  "is_public": true,
  "is_active": true,
  "location_url": "https://api.my-company.com/agent",
  "location_type": "api_endpoint",
  "capabilities": {
    "protocols": ["http"],
    "supported_formats": ["json"],
    "max_concurrent_requests": 50
  },
  "auth_schemes": [
    {
      "type": "api_key",
      "required": true,
      "header_name": "X-API-Key"
    }
  ],
  "agent_card": {
    "name": "my-new-agent",
    "description": "A new AI agent",
    "version": "1.0.0",
    "author": "My Company",
    "api_base_url": "https://api.my-company.com/v1"
  }
}
```

**Response:**
```json
{
  "id": "agent-456",
  "name": "my-new-agent",
  "description": "A new AI agent",
  "version": "1.0.0",
  "provider": "my-company",
  "tags": ["ai", "assistant"],
  "is_public": true,
  "is_active": true,
  "created_at": "2024-01-17T09:15:00Z",
  "updated_at": "2024-01-17T09:15:00Z"
}
```

#### Update Agent

```http
PUT /agents/{agent_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "Updated description",
  "version": "1.1.0",
  "tags": ["ai", "assistant", "updated"]
}
```

#### Delete Agent

```http
DELETE /agents/{agent_id}
Authorization: Bearer {token}
```

**Response:** `204 No Content`

#### Search Agents

```http
POST /agents/search
Content-Type: application/json

{
  "query": "chatbot AI assistant",
  "filters": {
    "tags": ["ai", "chatbot"],
    "provider": "ai-corp",
    "capabilities.protocols": ["http"]
  },
  "semantic": true,
  "page": 1,
  "limit": 20
}
```

**Response:**
```json
{
  "agents": [...],
  "total": 25,
  "page": 1,
  "limit": 20,
  "total_pages": 2,
  "query_info": {
    "semantic_search": true,
    "query_time_ms": 45,
    "filters_applied": ["tags", "provider"]
  }
}
```

### Clients

#### List Clients

```http
GET /clients
Authorization: Bearer {token}
```

#### Get Client

```http
GET /clients/{client_id}
Authorization: Bearer {token}
```

#### Create Client

```http
POST /clients
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Application",
  "description": "Application for managing AI agents",
  "redirect_uris": ["https://myapp.com/callback"],
  "scopes": ["agent:read", "agent:write"]
}
```

#### Update Client

```http
PUT /clients/{client_id}
Authorization: Bearer {token}
```

#### Delete Client

```http
DELETE /clients/{client_id}
Authorization: Bearer {token}
```

### Peer Registries

#### List Peer Registries

```http
GET /peering/registries
Authorization: Bearer {token}
```

#### Add Peer Registry

```http
POST /peering/registries
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Partner Registry",
  "base_url": "https://registry.partner.com",
  "description": "Partner organization's agent registry",
  "auth_token": "secret-token",
  "sync_interval": 3600
}
```

#### Sync Peer Registry

```http
POST /peering/registries/{registry_id}/sync
Authorization: Bearer {token}
```

### Well-Known Endpoints

#### Agent Index

```http
GET /.well-known/agents/index.json
```

**Response:**
```json
{
  "registry_info": {
    "name": "A2A Agent Registry",
    "version": "1.0.0",
    "base_url": "https://api.a2areg.dev"
  },
  "agents": [
    {
      "id": "agent-123",
      "name": "chatbot-assistant",
      "version": "1.2.0",
      "location": "https://api.ai-corp.com/chatbot"
    }
  ],
  "pagination": {
    "total": 850,
    "page": 1,
    "limit": 100
  }
}
```

#### Registry Agent Card

```http
GET /.well-known/agent.json
```

**Response:**
```json
{
  "name": "A2A Agent Registry",
  "description": "Centralized registry for A2A agents",
  "version": "1.0.0",
  "author": "A2A Registry Team",
  "api_base_url": "https://api.a2areg.dev",
  "capabilities": {
    "protocols": ["http", "websocket"],
    "supported_formats": ["json"],
    "max_concurrent_requests": 10000
  },
  "endpoints": {
    "agents": "/agents",
    "search": "/agents/search",
    "health": "/health",
    "stats": "/stats"
  }
}
```

## WebSocket API

The registry provides real-time notifications via WebSocket.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Authentication

Send authentication message after connection:

```json
{
  "type": "auth",
  "token": "your-jwt-token"
}
```

### Subscription

Subscribe to events:

```json
{
  "type": "subscribe",
  "events": ["agent.created", "agent.updated", "agent.deleted"]
}
```

### Event Messages

```json
{
  "type": "event",
  "event": "agent.created",
  "data": {
    "agent_id": "agent-123",
    "name": "new-agent",
    "provider": "ai-corp"
  },
  "timestamp": "2024-01-17T10:30:00Z"
}
```

### Available Events

- `agent.created` - New agent published
- `agent.updated` - Agent updated
- `agent.deleted` - Agent deleted
- `client.created` - New client registered
- `registry.sync` - Peer registry sync completed

## SDKs

### Python SDK

```bash
pip install a2a-reg-sdk
```

```python
from a2a_reg_sdk import A2AClient

client = A2AClient(
    registry_url="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

client.authenticate()
agents = client.list_agents()
```

### JavaScript SDK

```bash
npm install @a2areg/sdk
```

```javascript
import { A2AClient } from '@a2areg/sdk';

const client = new A2AClient({
  registryUrl: 'http://localhost:8000',
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret'
});

await client.authenticate();
const agents = await client.listAgents();
```

### CLI Tool

```bash
pip install a2a-publisher
```

```bash
# Initialize agent config
a2a-publisher init

# Publish agent
a2a-publisher publish agent.yaml

# List agents
a2a-publisher list
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

```http
GET /openapi.json
```

Interactive API documentation is available at:

```http
GET /docs
```

## Examples

### Complete Agent Lifecycle

```bash
# 1. Get access token
curl -X POST http://localhost:8000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET"

# 2. Create agent
curl -X POST http://localhost:8000/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-agent", "description": "Test", "version": "1.0.0", "provider": "test"}'

# 3. List agents
curl http://localhost:8000/agents/public

# 4. Update agent
curl -X PUT http://localhost:8000/agents/AGENT_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'

# 5. Delete agent
curl -X DELETE http://localhost:8000/agents/AGENT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Examples

```bash
# Basic search
curl -X POST http://localhost:8000/agents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "chatbot"}'

# Advanced search with filters
curl -X POST http://localhost:8000/agents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI assistant",
    "filters": {
      "tags": ["ai", "nlp"],
      "provider": "openai"
    },
    "semantic": true
  }'
```

For more examples and detailed usage, see the [SDK documentation](SDK_REFERENCE.md) and [examples directory](../examples/).

## Getting Help

- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time help and API discussions
- **API Documentation**: Interactive API docs at `/docs` endpoint
- **GitHub Issues**: Report API bugs and request new features
- **GitHub Discussions**: Community discussions and API usage questions
