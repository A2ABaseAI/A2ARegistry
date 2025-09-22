# A2A Registry API Examples

This directory contains comprehensive functional examples for interacting with the A2A Registry API endpoints. These examples demonstrate real-world usage patterns, error handling, and best practices.

## Overview

The A2A Registry provides several API endpoints for agent management and discovery:

- **Authentication API** (`/auth/*`) - Built-in user registration, login, and token management
- **Agent API** (`/agents/*`) - Publishing, retrieving, and managing agents
- **Search API** (`/agents/search`) - Advanced search and filtering capabilities
- **Well-Known API** (`/.well-known/agents/*`) - Standard discovery endpoints

## Examples

### 1. Built-in Authentication (`auth_api_examples.py`)

Demonstrates the A2A Registry's built-in authentication system:

- **User Management**
  - User registration with validation
  - User login with email/username
  - Password change functionality
  - User profile management
  
- **Token Management**
  - Access token generation
  - Refresh token functionality
  - Token validation and verification
  - Session management
  
- **Security Features**
  - Password hashing and validation
  - Role-based access control (RBAC)
  - Multi-tenant support
  - Secure logout and session invalidation

**Key Features:**
- Complete user lifecycle management
- Secure token-based authentication
- Production-ready security patterns
- Comprehensive error handling
- Integration with other API endpoints

### 2. JWT Token Creation (`jwt_token_examples.py` & `simple_jwt_example.py`)

Demonstrates how clients can create JWT tokens for external authentication:

- **Token Creation**
  - RSA key pair generation
  - JWT token creation with proper claims
  - JWKS (JSON Web Key Set) generation
  - Token validation and verification
  
- **Authentication Patterns**
  - Role-based access control (RBAC)
  - Multi-tenant token creation
  - Token refresh patterns
  - Production security practices
  
- **Integration**
  - API authentication testing
  - Error handling scenarios
  - Token lifecycle management

**Key Features:**
- Complete RSA key pair generation
- Proper JWT claim structure for A2A Registry
- JWKS endpoint creation for token validation
- Comprehensive error handling and validation
- Production-ready security patterns

### 3. Agent API Examples (`agent_api_examples.py`)

Demonstrates comprehensive agent management functionality:

- **Publishing Agents**
  - Publishing by card data (JSON payload)
  - Publishing by card URL (remote fetching)
  - Public vs private agent publishing
  
- **Retrieving Agents**
  - Getting public agents (no authentication required)
  - Getting entitled agents (authentication required)
  - Getting individual agent details
  - Getting agent cards
  
- **Error Handling**
  - Invalid card data validation
  - Non-existent agent handling
  - Authentication failures
  - Network error handling

**Key Features:**
- Production-ready error handling with try/catch blocks
- Comprehensive input validation
- Detailed logging and debugging information
- Graceful degradation on failures
- Security-first approach for private agents

### 4. Search API Examples (`search_api_examples.py`)

Demonstrates advanced search and filtering capabilities:

- **Basic Search**
  - Simple text queries
  - Empty/None query handling
  - Search result processing
  
- **Advanced Filtering**
  - Protocol version filtering
  - Publisher filtering
  - Capability-based filtering
  - Multiple filter combinations
  - Skill-based filtering
  
- **Pagination**
  - First/second page navigation
  - Large page size handling
  - Pagination validation
  
- **Combined Operations**
  - Text search + filters + pagination
  - Complex multi-criteria searches
  - Performance testing and caching

**Key Features:**
- Flexible search parameters
- Comprehensive filter support
- Efficient pagination handling
- Performance optimization examples
- Cache behavior testing

### 5. Well-Known API Examples (`well_known_api_examples.py`)

Demonstrates standard discovery endpoint usage:

- **Agents Index**
  - Getting the registry index
  - Pagination through results
  - Registry metadata access
  
- **Agent Cards**
  - Retrieving individual agent cards
  - Public vs private access patterns
  - Authentication requirements
  
- **Standards Compliance**
  - Well-known endpoint structure validation
  - Agent card format validation
  - Required field verification
  
- **Access Control**
  - Public agent access (no auth)
  - Private agent access (with auth)
  - Authentication error handling

**Key Features:**
- Standards-compliant endpoint usage
- Proper authentication handling
- Structure validation
- Access control demonstration

## Requirements

### System Requirements
- Python 3.7+
- A2A Registry server running (default: `http://localhost:8000`)
- `httpx` library for HTTP requests

### Installation
```bash
pip install -r requirements.txt
```

Or install individual dependencies:
```bash
pip install httpx PyJWT cryptography
```

### Environment Variables
- `A2A_REGISTRY_URL` - Registry server URL (default: `http://localhost:8000`)
- `A2A_TOKEN` - JWT token for authenticated endpoints (optional)

## Usage

### Basic Usage
```bash
# Run authentication examples first (recommended)
python auth_api_examples.py

# Run other API examples
python agent_api_examples.py
python search_api_examples.py
python well_known_api_examples.py

# Run all examples in sequence
python run_all_examples.py
```

### With Built-in Authentication
```bash
# The examples will automatically register users and get tokens
# No manual token creation needed for most examples
python auth_api_examples.py
```

### With External JWT Tokens
```bash
# For external JWT token usage
python simple_jwt_example.py
export A2A_TOKEN="your-jwt-token"
python agent_api_examples.py
```

### With Environment Variables
```bash
export A2A_REGISTRY_URL="https://your-registry.com"
export A2A_TOKEN="your-jwt-token"  # Optional for built-in auth

python auth_api_examples.py
```

### Individual Examples
Each example file can be run independently and includes:
- Connection testing
- Comprehensive error handling
- Detailed output with success/failure indicators
- Performance measurements
- Best practice demonstrations

## API Endpoints Covered

### Authentication API (`/auth/*`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login and token generation
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile
- `POST /auth/change-password` - Change user password
- `POST /auth/logout` - Logout and invalidate session

### Agent API (`/agents/*`)
- `POST /agents/publish` - Publish agents
- `GET /agents/public` - Get public agents
- `GET /agents/entitled` - Get entitled agents (auth required)
- `GET /agents/{agent_id}` - Get agent details
- `GET /agents/{agent_id}/card` - Get agent card

### Search API (`/agents/search`)
- `POST /agents/search` - Advanced agent search

### Well-Known API (`/.well-known/agents/*`)
- `GET /.well-known/agents/index.json` - Agents index
- `GET /.well-known/agents/{agent_id}/card` - Agent card

## Error Handling Patterns

All examples demonstrate production-ready error handling:

1. **HTTP Error Handling**
   - Status code checking
   - Error message extraction
   - Appropriate error responses

2. **Network Error Handling**
   - Connection timeouts
   - Network failures
   - Retry logic (where applicable)

3. **Validation Error Handling**
   - Input parameter validation
   - Response format validation
   - Data structure verification

4. **Authentication Error Handling**
   - Token validation
   - Access denied scenarios
   - Permission checking

## Best Practices Demonstrated

### Security
- Secure authentication handling
- Private agent access control
- Input validation and sanitization
- Error message security (no sensitive data exposure)

### Performance
- Efficient pagination
- Caching behavior testing
- Connection pooling
- Timeout handling

### Reliability
- Comprehensive error handling
- Graceful degradation
- Fallback mechanisms
- Retry strategies

### Maintainability
- Clean code structure
- Comprehensive logging
- Clear error messages
- Modular design

## Sample Output

Each example provides detailed output showing:
- ✓ Success indicators for successful operations
- ✗ Error indicators for failed operations
- ℹ Information indicators for expected behaviors
- Detailed error messages and debugging information
- Performance metrics and timing information

## Integration Examples

These examples can be used as:
- **Learning resources** for understanding the API
- **Integration templates** for your applications
- **Testing utilities** for API validation
- **Documentation** for API usage patterns

## Contributing

When adding new examples:
1. Follow the established patterns for error handling
2. Include comprehensive input validation
3. Provide detailed output and logging
4. Test with both success and failure scenarios
5. Document any new dependencies or requirements

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure A2A Registry server is running
   - Check the `A2A_REGISTRY_URL` environment variable
   - Verify network connectivity

2. **Authentication Errors**
   - Verify JWT token is valid and not expired
   - Check token permissions for required endpoints
   - Ensure proper token format in `A2A_TOKEN`

3. **Validation Errors**
   - Check agent card data format
   - Verify required fields are present
   - Ensure data types are correct

4. **Permission Errors**
   - Verify access to private agents
   - Check tenant permissions
   - Ensure proper authentication

For additional help, check the A2A Registry documentation or contact the development team.
