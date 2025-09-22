"""A2A Agent Card spec models following A2A Protocol specification (pydantic v2)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class AgentProvider(BaseModel):
    """Agent Provider Object - Service provider information for the Agent."""

    organization: str = Field(..., description="Organization name")
    url: HttpUrl = Field(..., description="Organization URL")


class AgentCapabilities(BaseModel):
    """Agent Capabilities Object - Optional capabilities supported by the Agent."""

    streaming: Optional[bool] = Field(None, description="If the Agent supports Server-Sent Events (SSE)")
    pushNotifications: Optional[bool] = Field(
        None, description="If the Agent can push update notifications to the client"
    )
    stateTransitionHistory: Optional[bool] = Field(None, description="If the Agent exposes task state change history")
    supportsAuthenticatedExtendedCard: Optional[bool] = Field(
        None, description="If the Agent supports authenticated extended card retrieval"
    )


class SecurityScheme(BaseModel):
    """Security Scheme Object - Authentication requirements for the Agent."""

    type: str = Field(..., description="Authentication type (apiKey, oauth2, jwt, mTLS)")
    location: Optional[str] = Field(None, description="Location of credentials (header, query, body)")
    name: Optional[str] = Field(None, description="Parameter name for credentials")
    flow: Optional[str] = Field(None, description="OAuth2 flow type")
    tokenUrl: Optional[HttpUrl] = Field(None, description="OAuth2 token URL")
    scopes: Optional[List[str]] = Field(None, description="OAuth2 scopes")
    credentials: Optional[str] = Field(None, description="Credentials for the client to use for private Cards")


class AgentSkill(BaseModel):
    """Agent Skill Object - Collection of capability units the Agent can perform."""

    id: str = Field(..., description="Unique identifier for the skill")
    name: str = Field(..., description="Human-readable name for the skill")
    description: str = Field(..., description="Skill description")
    tags: List[str] = Field(..., description="Tags describing the skill's capability category")
    examples: Optional[List[str]] = Field(None, description="Example scenarios or prompts the skill can execute")
    inputModes: Optional[List[str]] = Field(None, description="Input MIME types supported by the skill")
    outputModes: Optional[List[str]] = Field(None, description="Output MIME types supported by the skill")


class AgentInterface(BaseModel):
    """Agent Interface Object - Transport and interaction capabilities."""

    preferredTransport: str = Field(..., description="Preferred transport protocol")
    additionalInterfaces: Optional[List[Dict[str, Any]]] = Field(
        None, description="Additional transport interfaces supported"
    )
    defaultInputModes: List[str] = Field(..., description="Supported input MIME types")
    defaultOutputModes: List[str] = Field(..., description="Supported output MIME types")


class AgentCardSignature(BaseModel):
    """Agent Card Signature Object - Digital signature information."""

    algorithm: Optional[str] = Field(None, description="Signature algorithm used")
    signature: Optional[str] = Field(None, description="Digital signature value")
    jwksUrl: Optional[HttpUrl] = Field(None, description="JWKS URL for signature verification")


class AgentCardSpec(BaseModel):
    """Agent Card specification following A2A Protocol specification."""

    # Core identification fields
    name: str = Field(..., description="Human-readable name for the Agent")
    description: str = Field(..., description="Human-readable description of the Agent's function")
    url: HttpUrl = Field(..., description="URL address where the Agent is hosted")
    version: str = Field(..., description="Version of the Agent")

    # A2A Protocol objects
    provider: Optional[AgentProvider] = Field(None, description="Agent Provider Object - Service provider information")
    capabilities: AgentCapabilities = Field(
        ..., description="Agent Capabilities Object - Optional capabilities supported"
    )
    securitySchemes: List[SecurityScheme] = Field(
        ..., description="Security Scheme Objects - Authentication requirements"
    )
    skills: List[AgentSkill] = Field(..., description="Agent Skill Objects - Collection of capability units")
    interface: AgentInterface = Field(
        ..., description="Agent Interface Object - Transport and interaction capabilities"
    )

    # Optional fields
    documentationUrl: Optional[HttpUrl] = Field(None, description="URL for the Agent's documentation")
    signature: Optional[AgentCardSignature] = Field(
        None, description="Agent Card Signature Object - Digital signature information"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Recipe Agent",
                "description": (
                    "An AI agent that helps users find and create recipes "
                    "based on available ingredients and dietary preferences"
                ),
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
