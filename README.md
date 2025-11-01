# A2A Agent Registry

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](PRODUCTION.md)

A centralized registry service for discovering and managing AI agents in the A2A (Agent-to-Agent) ecosystem. This implementation follows the [A2A Agent Registry Proposal](https://github.com/a2aproject/A2A/discussions/741) and provides a complete solution for agent discovery, entitlements, and federation.

## 🌟 Features

- **🎨 Modern Web UI**: Beautiful, responsive React frontend with Tailwind CSS
- **🔍 Agent Discovery**: Advanced search with lexical and semantic capabilities
- **🔐 Enterprise Security**: OAuth 2.0, rate limiting, and comprehensive security headers
- **🌐 Federation**: Cross-registry peering and synchronization
- **📊 Production Ready**: Monitoring, logging, caching, and automated deployment
- **🚀 High Performance**: Redis caching, connection pooling, and horizontal scaling
- **📚 Well-Documented**: Complete API documentation and deployment guides

## Core Quick Start (no frontend)

This repository is now a core-only API service (no React UI). Use the steps below for a minimal local run:

1. Start dependencies and API
   ```bash
   docker-compose up -d db redis opensearch registry
   ```

2. Apply migrations
   ```bash
   alembic upgrade head
   ```

3. Publish an agent card by URL (Administrator/CatalogManager token required)
   ```bash
   curl -X POST "http://localhost:8000/agents/publish" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "cardUrl": "https://example.com/.well-known/agent-card.json",
       "public": true
     }'
   ```

4. Query public/entitled/search endpoints
   ```bash
   curl "http://localhost:8000/agents/public?top=20&skip=0"
   curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/agents/entitled?top=20&skip=0"
   curl -X POST -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" \
     "http://localhost:8000/agents/search" -d '{"q":"payments","top":20,"skip":0}'
   ```

Authentication: Provide an OAuth2 client-credentials JWT issued by your IdP. JWKS verification is configured via settings.

SLOs: p95 < 200 ms for cache-warm reads (local region), 99.9% availability, scale targets 10M agents / 2k RPS reads / 200 RPS writes.


## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 12+
- Redis 6+
- OpenSearch 2.x

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/A2AReg/a2a-registry.git
   cd a2a-registry
   ```

2. **Start with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

3. **Initialize sample data**
   ```bash
   python scripts/init_db.py
   ```

4. **Access the registry**
   - **Web UI**: http://localhost:3000 (React frontend)
   - **API**: http://localhost:8000 (FastAPI backend)
   - **API Docs**: http://localhost:8000/docs
   - **Health**: http://localhost:8000/health

### Manual Installation

1. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   cd ..
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start services**
   ```bash
   docker-compose up -d db redis opensearch
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend**
   ```bash
   python -m registry.main
   ```

7. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

## 🎨 Web Interface

The A2A Agent Registry includes a modern, responsive web interface built with React and Tailwind CSS:

### Key Features
- **📊 Dashboard**: Overview of registry statistics and system health
- **🤖 Agent Management**: Browse, search, and manage agents with advanced filtering
- **👥 Client Management**: OAuth client registration and entitlement management
- **🌐 Federation**: Configure peer registries and cross-registry synchronization
- **⚙️ Settings**: System configuration and user preferences
- **🔐 Authentication**: Secure OAuth 2.0 login with client credentials

### UI Components
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: Automatic theme switching based on system preferences
- **Real-time Updates**: Live data refresh and notifications
- **Advanced Search**: Semantic and lexical search with filters
- **Interactive Charts**: Visual representation of registry statistics

## 📖 Documentation

- **[Production Deployment](PRODUCTION.md)** - Enterprise deployment guide
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Security Policy](SECURITY.md)** - Security guidelines and vulnerability reporting
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Changelog](CHANGELOG.md)** - Release history and changes

## Configuration

### Environment Variables

```bash
# Application
APP_NAME="A2A Agent Registry"
APP_VERSION="1.0.0"
DEBUG=false

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/a2a_registry"

# Redis
REDIS_URL="redis://localhost:6379/0"

# OpenSearch
ELASTICSEARCH_URL="http://localhost:9200"
ELASTICSEARCH_INDEX="a2a_agents"

# Security
SECRET_KEY="your-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Registry
REGISTRY_BASE_URL="http://localhost:8000"
MAX_AGENTS_PER_CLIENT=1000
ENABLE_FEDERATION=true
```

## API Usage

### Authentication

The registry uses OAuth 2.0 Client Credentials flow for authentication:

```bash
# Get access token
curl -X POST "http://localhost:8000/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_client_id&password=your_client_secret"
```

### Agent Management

#### Register an Agent
```bash
curl -X POST "http://localhost:8000/agents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_card": {
      "id": "my-agent",
      "name": "My AI Agent",
      "version": "1.0.0",
      "description": "A sample AI agent",
      "capabilities": {
        "a2a_version": "1.0",
        "supported_protocols": ["http", "grpc"]
      },
      "skills": {
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"}
      },
      "auth_schemes": [
        {
          "type": "apiKey",
          "location": "header",
          "name": "X-API-Key"
        }
      ],
      "provider": "My Company",
      "tags": ["ai", "assistant"],
      "location": {
        "url": "https://my-agent.example.com/.well-known/agent.json",
        "type": "agent_card"
      }
    },
    "is_public": true
  }'
```

#### Search Agents
```bash
curl -X POST "http://localhost:8000/agents/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI assistant",
    "filters": {
      "provider": "My Company",
      "tags": ["ai"]
    },
    "top": 10
  }'
```

#### Get Entitled Agents
```bash
curl -X GET "http://localhost:8000/agents/entitled" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Well-Known Endpoints

#### Agent Discovery
```bash
# Get agents index
curl "http://localhost:8000/.well-known/agents/index.json"

# Get specific agent card
curl "http://localhost:8000/agents/my-agent/card"
```

## Agent Card Schema

The Agent Card is the core data structure for agent metadata:

```json
{
  "id": "agent-id",
  "name": "Agent Name",
  "version": "1.0.0",
  "description": "Agent description",
  "capabilities": {
    "a2a_version": "1.0",
    "supported_protocols": ["http", "grpc", "websocket"],
    "max_concurrent_requests": 100,
    "timeout_seconds": 30,
    "rate_limit_per_minute": 1000
  },
  "skills": {
    "input_schema": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
        "context": {"type": "object"}
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "response": {"type": "string"},
        "confidence": {"type": "number"}
      }
    }
  },
  "auth_schemes": [
    {
      "type": "apiKey",
      "location": "header",
      "name": "X-API-Key"
    },
    {
      "type": "oauth2",
      "flow": "client_credentials",
      "token_url": "https://auth.example.com/oauth/token",
      "scopes": ["agent:read", "agent:write"]
    }
  ],
  "tee_details": {
    "enabled": true,
    "provider": "Intel SGX",
    "attestation": "required",
    "version": "2.0"
  },
  "provider": "Agent Provider",
  "tags": ["ai", "assistant", "nlp"],
  "contact_url": "https://example.com/contact",
  "documentation_url": "https://docs.example.com/agent",
  "location": {
    "url": "https://agent.example.com/.well-known/agent.json",
    "type": "agent_card"
  }
}
```

## Federation

The registry supports federation with other A2A registries:

### Add a Peer Registry
```bash
curl -X POST "http://localhost:8000/peers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Partner Registry",
    "base_url": "https://partner-registry.example.com",
    "description": "Partner organization registry",
    "auth_token": "peer_auth_token",
    "sync_enabled": true,
    "sync_interval_minutes": 60
  }'
```

### Synchronize with Peers
```bash
# Sync specific peer
curl -X POST "http://localhost:8000/peers/peer-id/sync" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Sync all peers
curl -X POST "http://localhost:8000/peers/sync-all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Development

### Quality Checks
Run comprehensive quality checks using the provided scripts:

```bash
# Python script (recommended)
python quality_check.py --all

# Shell script
./quality_check.sh --all

# Makefile
make quality

# Individual checks
python quality_check.py --lint --test
make lint test

# Development commands
make backend                    # Run the backend server
make examples                   # Run all examples
make example NAME=basic_usage   # Run specific example

# Publishing commands
make publish                    # Publish SDK to PyPI
make build-sdk                  # Build SDK package
make test-sdk                   # Test SDK package locally
```

See [QUALITY_CHECKS.md](QUALITY_CHECKS.md) for detailed information.

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Architecture

### Frontend (React + TypeScript + Vite)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Query for server state management
- **Routing**: React Router for SPA navigation
- **Forms**: React Hook Form with validation
- **Notifications**: React Hot Toast for user feedback

### Backend Components

1. **API Layer**: FastAPI-based REST API with OpenAPI documentation
2. **Service Layer**: Business logic for agents, clients, search, and peering
3. **Data Layer**: SQLAlchemy ORM with PostgreSQL backend
4. **Search Layer**: OpenSearch for high-performance search
5. **Auth Layer**: OAuth 2.0 with JWT tokens
6. **Federation Layer**: Peer-to-peer synchronization
7. **Web Interface**: Modern React frontend with responsive design

### Database Schema

- **agents**: Agent metadata and cards
- **clients**: OAuth 2.0 clients
- **client_entitlements**: Agent access permissions
- **peer_registries**: Federation peers
- **peer_syncs**: Synchronization history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Apache 2.0 License - see LICENSE file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 **Report bugs** using GitHub Issues
- 💡 **Suggest features** using GitHub Discussions
- 📝 **Improve documentation**
- 🔧 **Submit pull requests**
- 🧪 **Add tests**
- 🔒 **Security improvements**

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🛡️ Security

Security is important to us. Please report security vulnerabilities privately to security@a2areg.dev.

See our [Security Policy](SECURITY.md) for more information.

## 🌍 Community

- **💬 Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) - Get help, share ideas, and connect with other developers
- **🐛 GitHub Issues**: [Report bugs and request features](https://github.com/A2AReg/a2a-registry/issues)
- **💡 GitHub Discussions**: [Community discussions](https://github.com/A2AReg/a2a-registry/discussions)
- **🤖 A2A Community**: [A2A Discussions](https://github.com/A2AReg/A2A/discussions)
- **📚 Documentation**: [Full API documentation](http://localhost:8000/docs)

## 🙏 Acknowledgments

- [A2A Project](https://github.com/a2aproject/A2A) for the original proposal
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [OpenSearch](https://opensearch.org/) for search capabilities
- All contributors and the open source community
