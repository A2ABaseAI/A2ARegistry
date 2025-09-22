"""Agent-related Pydantic schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class AgentAuthScheme(BaseModel):
    """Agent authentication scheme."""

    type: str = Field(
        ..., description="Authentication type (apiKey, oauth2, jwt, mTLS)"
    )
    location: Optional[str] = Field(
        None, description="Location of credentials (header, query, body)"
    )
    name: Optional[str] = Field(None, description="Parameter name for credentials")
    flow: Optional[str] = Field(None, description="OAuth2 flow type")
    token_url: Optional[HttpUrl] = Field(None, description="OAuth2 token URL")
    scopes: Optional[List[str]] = Field(None, description="OAuth2 scopes")


class AgentTeeDetails(BaseModel):
    """Trusted Execution Environment details."""

    enabled: bool = Field(False, description="Whether TEE is enabled")
    provider: Optional[str] = Field(
        None, description="TEE provider (Intel SGX, AMD SEV, etc.)"
    )
    attestation: Optional[str] = Field(None, description="Attestation requirements")
    version: Optional[str] = Field(None, description="TEE version")


class AgentCapabilities(BaseModel):
    """Agent capabilities and protocol information."""

    a2a_version: str = Field(..., description="A2A protocol version")
    supported_protocols: List[str] = Field(
        ..., description="Supported protocols (http, grpc, websocket)"
    )
    max_concurrent_requests: Optional[int] = Field(
        None, description="Maximum concurrent requests"
    )
    timeout_seconds: Optional[int] = Field(
        None, description="Default timeout in seconds"
    )
    rate_limit_per_minute: Optional[int] = Field(
        None, description="Rate limit per minute"
    )


class AgentCard(BaseModel):
    """Agent Card schema - core metadata for agent discovery."""

    # Core identification
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    version: str = Field(..., description="Agent version")
    description: str = Field(..., description="Agent description")

    # Capabilities and protocols
    capabilities: AgentCapabilities = Field(..., description="Agent capabilities")
    skills: Dict[str, Any] = Field(
        ..., description="Agent skills and input/output schemas"
    )

    # Authentication
    auth_schemes: List[AgentAuthScheme] = Field(
        ..., description="Supported authentication schemes"
    )

    # Security and execution
    tee_details: Optional[AgentTeeDetails] = Field(None, description="TEE details")

    # Metadata
    provider: str = Field(..., description="Agent provider")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    contact_url: Optional[HttpUrl] = Field(None, description="Contact URL")
    documentation_url: Optional[HttpUrl] = Field(None, description="Documentation URL")

    # Location
    location: Dict[str, Any] = Field(..., description="Agent location information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "it-agent-v2",
                "name": "IT Support Agent",
                "version": "2.1.0",
                "description": "Handles IT support queries and troubleshooting",
                "capabilities": {
                    "a2a_version": "1.0",
                    "supported_protocols": ["http", "grpc"],
                    "max_concurrent_requests": 100,
                    "timeout_seconds": 30,
                    "rate_limit_per_minute": 1000,
                },
                "skills": {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "context": {"type": "object"},
                        },
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "response": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                    },
                },
                "auth_schemes": [
                    {"type": "apiKey", "location": "header", "name": "X-API-Key"},
                    {
                        "type": "oauth2",
                        "flow": "client_credentials",
                        "token_url": "https://auth.example.com/oauth/token",
                        "scopes": ["agent:read", "agent:write"],
                    },
                ],
                "tee_details": {
                    "enabled": True,
                    "provider": "Intel SGX",
                    "attestation": "required",
                    "version": "2.0",
                },
                "provider": "Enterprise IT",
                "tags": ["support", "it", "troubleshooting"],
                "contact_url": "https://it.example.com/contact",
                "documentation_url": "https://docs.example.com/it-agent",
                "location": {
                    "url": "https://it.example.com/.well-known/agent.json",
                    "type": "agent_card",
                },
            }
        }
    )


class AgentCreate(BaseModel):
    """Schema for creating a new agent."""

    agent_card: AgentCard = Field(..., description="Agent card data")
    is_public: bool = Field(False, description="Whether agent is publicly discoverable")
    client_id: Optional[str] = Field(None, description="Client that owns this agent")


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent."""

    agent_card: Optional[AgentCard] = Field(None, description="Updated agent card data")
    is_public: Optional[bool] = Field(None, description="Updated public visibility")
    is_active: Optional[bool] = Field(None, description="Whether agent is active")


class AgentResponse(BaseModel):
    """Schema for agent response."""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    description: str = Field(..., description="Agent description")
    provider: str = Field(..., description="Agent provider")
    tags: List[str] = Field(..., description="Agent tags")
    is_public: bool = Field(..., description="Public visibility")
    is_active: bool = Field(..., description="Active status")
    location: Dict[str, Any] = Field(..., description="Agent location")
    capabilities: Optional[AgentCapabilities] = Field(
        None, description="Agent capabilities"
    )
    auth_schemes: Optional[List[AgentAuthScheme]] = Field(
        None, description="Authentication schemes"
    )
    tee_details: Optional[AgentTeeDetails] = Field(None, description="TEE details")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class AgentSearchRequest(BaseModel):
    """Schema for agent search requests (aligned with POST /agents/search)."""

    q: Optional[str] = Field(None, description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    top: int = Field(20, ge=1, le=100, description="Max results to return")
    skip: int = Field(0, ge=0, description="Number of results to skip (offset)")


class AgentSearchResponse(BaseModel):
    """Schema for agent search responses."""

    registry_version: str = Field(..., description="Registry version")
    timestamp: str = Field(..., description="Search timestamp")
    resources: List[AgentResponse] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of results")
    search_metadata: Dict[str, Any] = Field(..., description="Search metadata")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")


class PublishResponse(BaseModel):
    """Response for successful publish operation."""

    agentId: str = Field(..., description="Agent ID")
    version: str = Field(..., description="Version identifier")
    protocolVersion: str = Field(..., description="A2A protocol version")
    public: bool = Field(..., description="Whether the version is public")
    signatureValid: bool = Field(..., description="Card signature validation result")


class AgentInfoResponse(BaseModel):
    """Lightweight agent info used by GET /agents/{id}."""

    agentId: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    publisherId: str = Field(...)
    version: str = Field(...)
    protocolVersion: str = Field(...)
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
