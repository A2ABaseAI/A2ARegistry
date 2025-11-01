"""A2A Agent Card spec models following A2A Protocol specification (pydantic v2).

This module implements the Agent Card schema as defined in the A2A Protocol specification,
Section 5.5 - AgentCard Object Structure. For more details, see:
https://a2a-protocol.org/dev/specification/#355-extension-method-naming
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class AgentProvider(BaseModel):
    """Agent Provider Object - Service provider information for the Agent."""

    organization: str = Field(..., description="Organization name")
    url: HttpUrl = Field(..., description="Organization URL")


class AgentCapabilities(BaseModel):
    """Agent Capabilities Object - Optional capabilities supported by the Agent.
    
    Section 5.5.2 of the A2A Protocol specification defines these capability flags
    that indicate what optional features the Agent supports.
    """

    streaming: Optional[bool] = Field(None, description="If the Agent supports Server-Sent Events (SSE) for streaming responses")
    pushNotifications: Optional[bool] = Field(None, description="If the Agent can push update notifications to the client")
    stateTransitionHistory: Optional[bool] = Field(None, description="If the Agent exposes task state change history")
    supportsAuthenticatedExtendedCard: Optional[bool] = Field(None, description="If the Agent supports authenticated extended card retrieval")


class SecurityScheme(BaseModel):
    """Security Scheme Object - Authentication requirements for the Agent.
    
    Section 5.5.3 of the A2A Protocol specification. Defines how clients should
    authenticate when interacting with the Agent.
    """

    type: str = Field(..., description="Authentication type. Valid values: apiKey, oauth2, jwt, mTLS")
    location: Optional[str] = Field(None, description="Location of credentials in the request. Valid values: header, query, body")
    name: Optional[str] = Field(None, description="Parameter name for credentials (e.g., 'Authorization', 'X-API-Key')")
    flow: Optional[str] = Field(None, description="OAuth2 flow type (e.g., 'client_credentials', 'authorization_code')")
    tokenUrl: Optional[HttpUrl] = Field(None, description="OAuth2 token URL for obtaining access tokens")
    scopes: Optional[List[str]] = Field(None, description="OAuth2 scopes required for access")
    credentials: Optional[str] = Field(None, description="Credentials for the client to use for private Cards")


class AgentSkill(BaseModel):
    """Agent Skill Object - Collection of capability units the Agent can perform.
    
    Section 5.5.4 of the A2A Protocol specification. Each skill represents a specific
    capability or task that the Agent can execute.
    """

    id: str = Field(..., description="Unique identifier for the skill (e.g., 'find_recipe', 'create_ticket')")
    name: str = Field(..., description="Human-readable name for the skill")
    description: str = Field(..., description="Detailed description of what the skill does and its purpose")
    tags: List[str] = Field(..., description="Tags describing the skill's capability category for discovery and filtering")
    examples: Optional[List[str]] = Field(None, description="Example scenarios or prompts the skill can execute")
    inputModes: Optional[List[str]] = Field(None, description="Input MIME types supported by the skill (if different from interface defaults)")
    outputModes: Optional[List[str]] = Field(None, description="Output MIME types supported by the skill (if different from interface defaults)")


class AgentInterface(BaseModel):
    """Agent Interface Object - Transport and interaction capabilities.
    
    Section 5.5.5 of the A2A Protocol specification. Defines how clients should
    communicate with the Agent, including transport protocols and data formats.
    """

    preferredTransport: str = Field(..., description="Preferred transport protocol. Valid values: jsonrpc, grpc, http")
    additionalInterfaces: Optional[List[Dict[str, Any]]] = Field(None, description="Additional transport interfaces supported. Each entry should have 'transport' and 'url' fields")
    defaultInputModes: List[str] = Field(..., description="Default input MIME types supported (e.g., ['text/plain', 'application/json'])")
    defaultOutputModes: List[str] = Field(..., description="Default output MIME types supported (e.g., ['text/plain', 'application/json'])")


class AgentCardSignature(BaseModel):
    """Agent Card Signature Object - Digital signature information.
    
    Section 5.5.6 of the A2A Protocol specification. Provides cryptographic
    verification of the Agent Card's integrity and authenticity.
    """

    algorithm: Optional[str] = Field(None, description="Signature algorithm used (e.g., 'RS256', 'ES256')")
    signature: Optional[str] = Field(None, description="Digital signature value (base64-encoded)")
    jwksUrl: Optional[HttpUrl] = Field(None, description="JWKS URL for signature verification (e.g., 'https://example.com/.well-known/jwks.json')")


class AgentCardSpec(BaseModel):
    """Agent Card specification following A2A Protocol specification.
    
    This class implements the complete Agent Card structure as defined in the
    A2A Protocol specification, Section 5.5. The Agent Card is a JSON document
    that describes an agent's capabilities, endpoints, and metadata, facilitating
    agent discovery and interoperability.
    
    Reference: https://a2a-protocol.org/dev/specification/#355-extension-method-naming
    """

    # Core identification fields (required)
    name: str = Field(..., description="Human-readable name for the Agent")
    description: str = Field(..., description="Human-readable description of the Agent's function and capabilities")
    url: HttpUrl = Field(..., description="URL address where the Agent is hosted and can be accessed")
    version: str = Field(..., description="Version of the Agent implementation (semantic versioning recommended, e.g., '1.0.0')")

    # A2A Protocol objects (required)
    provider: Optional[AgentProvider] = Field(None, description="Agent Provider Object (Section 5.5.1) - Service provider information")
    capabilities: AgentCapabilities = Field(..., description="Agent Capabilities Object (Section 5.5.2) - Optional capabilities supported by the Agent")
    securitySchemes: List[SecurityScheme] = Field(..., description="Security Scheme Objects (Section 5.5.3) - Authentication requirements for accessing the Agent")
    skills: List[AgentSkill] = Field(..., description="Agent Skill Objects (Section 5.5.4) - Collection of capability units the Agent can perform")
    interface: AgentInterface = Field(..., description="Agent Interface Object (Section 5.5.5) - Transport and interaction capabilities")

    # Optional fields
    documentationUrl: Optional[HttpUrl] = Field(None, description="URL for the Agent's documentation and API reference")
    signature: Optional[AgentCardSignature] = Field(None, description="Agent Card Signature Object (Section 5.5.6) - Digital signature information for verification")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Recipe Agent",
                "description": ("An AI agent that helps users find and create recipes " "based on available ingredients and dietary preferences"),
                "url": "https://recipe-agent.example.com",
                "version": "1.0.0",
                "provider": {"organization": "Culinary AI Solutions", "url": "https://culinary-ai.com"},
                "capabilities": {
                    "streaming": True,
                    "pushNotifications": False,
                    "stateTransitionHistory": True,
                    "supportsAuthenticatedExtendedCard": False,
                },
                "securitySchemes": [
                    {
                        "type": "apiKey",
                        "location": "header",
                        "name": "X-API-Key",
                        "credentials": "api_key_for_private_recipes",
                    },
                    {
                        "type": "oauth2",
                        "flow": "client_credentials",
                        "tokenUrl": "https://culinary-ai.com/oauth/token",
                        "scopes": ["read", "write"],
                    },
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
                            "What can I make with chicken and rice?",
                        ],
                        "inputModes": ["text/plain"],
                        "outputModes": ["application/json"],
                    },
                    {
                        "id": "create_meal_plan",
                        "name": "Create Meal Plan",
                        "description": "Generate a weekly meal plan based on dietary goals",
                        "tags": ["meal-planning", "nutrition", "diet"],
                        "examples": [
                            "Create a keto meal plan for the week",
                            "Plan meals for a family of 4",
                            "Generate a balanced meal plan",
                        ],
                    },
                ],
                "interface": {
                    "preferredTransport": "jsonrpc",
                    "additionalInterfaces": [{"transport": "http", "url": "https://recipe-agent.example.com/api"}],
                    "defaultInputModes": ["text/plain", "application/json"],
                    "defaultOutputModes": ["text/plain", "application/json"],
                },
                "documentationUrl": "https://recipe-agent.example.com/docs",
                "signature": {
                    "algorithm": "RS256",
                    "jwksUrl": "https://recipe-agent.example.com/.well-known/jwks.json",
                },
            }
        }
    )
