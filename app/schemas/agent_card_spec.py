"""A2A Agent Card spec models (pydantic v2)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Skill(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    ioSchemas: Optional[Dict[str, Any]] = Field(None, description="JSON Schemas for IO")


class AgentCardSpec(BaseModel):
    # Required core
    protocolVersion: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    url: HttpUrl = Field(...)

    # Recommended
    version: Optional[str] = Field(None)
    defaultInputModes: Optional[List[str]] = Field(default=None)
    defaultOutputModes: Optional[List[str]] = Field(default=None)
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    skills: List[Skill] = Field(default_factory=list)
    extensions: List[Dict[str, Any]] = Field(default_factory=list)
    authSchemes: List[Dict[str, Any]] = Field(default_factory=list)

    # Security
    jwks: Optional[Dict[str, Any]] = Field(default=None)
    jwks_uri: Optional[HttpUrl] = Field(default=None)

    # Compatibility alias
    a2aSpecVersion: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "protocolVersion": "0.3.0",
                "name": "Checkout Concierge",
                "description": "Enterprise payments agent",
                "url": "https://checkout.com/.well-known/agent-card.json",
                "version": "1.4.2",
                "defaultInputModes": ["text"],
                "defaultOutputModes": ["text"],
                "capabilities": {"streaming": True},
                "skills": [
                    {
                        "id": "create_session",
                        "name": "Create Session",
                        "description": "Create a checkout session",
                    }
                ],
                "authSchemes": [{"type": "oauth2", "flow": "client_credentials"}],
            }
        }
    )
