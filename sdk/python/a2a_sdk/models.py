"""
A2A Registry Data Models

Data models for A2A agents and related entities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json


@dataclass
class AgentCapabilities:
    """Agent capabilities specification."""

    protocols: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    max_request_size: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    a2a_version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCapabilities":
        """Create from dictionary."""
        return cls(
            protocols=data.get("protocols", []),
            supported_formats=data.get("supported_formats", []),
            max_request_size=data.get("max_request_size"),
            max_concurrent_requests=data.get("max_concurrent_requests"),
            a2a_version=data.get("a2a_version"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "protocols": self.protocols,
            "supported_formats": self.supported_formats,
            "max_request_size": self.max_request_size,
            "max_concurrent_requests": self.max_concurrent_requests,
            "a2a_version": self.a2a_version,
        }


@dataclass
class AuthScheme:
    """Authentication scheme specification."""

    type: str
    description: Optional[str] = None
    required: bool = False
    header_name: Optional[str] = None
    query_param: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthScheme":
        """Create from dictionary."""
        return cls(
            type=data["type"],
            description=data.get("description"),
            required=data.get("required", False),
            header_name=data.get("header_name"),
            query_param=data.get("query_param"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "header_name": self.header_name,
            "query_param": self.query_param,
        }


@dataclass
class AgentTeeDetails:
    """Trusted Execution Environment details."""

    enabled: bool = False
    provider: Optional[str] = None
    attestation: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTeeDetails":
        """Create from dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            provider=data.get("provider"),
            attestation=data.get("attestation"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "attestation": self.attestation,
        }


@dataclass
class AgentSkills:
    """Agent skills specification."""

    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSkills":
        """Create from dictionary."""
        return cls(
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            examples=data.get("examples", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "examples": self.examples,
        }


@dataclass
class AgentCard:
    """Agent card containing detailed metadata."""

    name: str
    description: str
    version: str
    author: str
    api_base_url: Optional[str] = None
    capabilities: Optional[AgentCapabilities] = None
    auth_schemes: List[AuthScheme] = field(default_factory=list)
    endpoints: Dict[str, str] = field(default_factory=dict)
    skills: Optional[AgentSkills] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        """Create from dictionary."""
        capabilities = None
        if data.get("capabilities"):
            capabilities = AgentCapabilities.from_dict(data["capabilities"])

        auth_schemes = []
        for scheme_data in data.get("auth_schemes", []):
            auth_schemes.append(AuthScheme.from_dict(scheme_data))

        skills = None
        if data.get("skills"):
            skills = AgentSkills.from_dict(data["skills"])

        return cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            author=data["author"],
            api_base_url=data.get("api_base_url"),
            capabilities=capabilities,
            auth_schemes=auth_schemes,
            endpoints=data.get("endpoints", {}),
            skills=skills,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "api_base_url": self.api_base_url,
            "capabilities": self.capabilities.to_dict() if self.capabilities else None,
            "auth_schemes": [scheme.to_dict() for scheme in self.auth_schemes],
            "endpoints": self.endpoints,
            "skills": self.skills.to_dict() if self.skills else None,
        }


@dataclass
class Agent:
    """A2A Agent representation."""

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create from dictionary."""
        capabilities = None
        if data.get("capabilities"):
            capabilities = AgentCapabilities.from_dict(data["capabilities"])

        auth_schemes = []
        for scheme_data in data.get("auth_schemes", []):
            auth_schemes.append(AuthScheme.from_dict(scheme_data))

        tee_details = None
        if data.get("tee_details"):
            tee_details = AgentTeeDetails.from_dict(data["tee_details"])

        skills = None
        if data.get("skills"):
            skills = AgentSkills.from_dict(data["skills"])

        agent_card = None
        if data.get("agent_card"):
            agent_card = AgentCard.from_dict(data["agent_card"])

        # Parse datetime strings
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))

        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data["description"],
            version=data["version"],
            provider=data["provider"],
            tags=data.get("tags", []),
            is_public=data.get("is_public", True),
            is_active=data.get("is_active", True),
            location_url=data.get("location_url"),
            location_type=data.get("location_type"),
            capabilities=capabilities,
            auth_schemes=auth_schemes,
            tee_details=tee_details,
            skills=skills,
            agent_card=agent_card,
            client_id=data.get("client_id"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "provider": self.provider,
            "tags": self.tags,
            "is_public": self.is_public,
            "is_active": self.is_active,
            "location_url": self.location_url,
            "location_type": self.location_type,
            "capabilities": self.capabilities.to_dict() if self.capabilities else None,
            "auth_schemes": [scheme.to_dict() for scheme in self.auth_schemes],
            "tee_details": self.tee_details.to_dict() if self.tee_details else None,
            "skills": self.skills.to_dict() if self.skills else None,
            "agent_card": self.agent_card.to_dict() if self.agent_card else None,
        }

        # Only include ID if it exists (for updates)
        if self.id:
            result["id"] = self.id

        if self.client_id:
            result["client_id"] = self.client_id

        if self.created_at:
            result["created_at"] = self.created_at.isoformat()

        if self.updated_at:
            result["updated_at"] = self.updated_at.isoformat()

        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "Agent":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


# Builder classes for easier agent creation


class AgentBuilder:
    """Builder class for creating Agent objects."""

    def __init__(self, name: str, description: str, version: str, provider: str):
        self._agent = Agent(name=name, description=description, version=version, provider=provider)

    def with_tags(self, tags: List[str]) -> "AgentBuilder":
        """Add tags to the agent."""
        self._agent.tags = tags
        return self

    def with_location(self, url: str, location_type: str = "api_endpoint") -> "AgentBuilder":
        """Set agent location."""
        self._agent.location_url = url
        self._agent.location_type = location_type
        return self

    def with_capabilities(self, capabilities: AgentCapabilities) -> "AgentBuilder":
        """Set agent capabilities."""
        self._agent.capabilities = capabilities
        return self

    def with_auth_schemes(self, auth_schemes: List[AuthScheme]) -> "AgentBuilder":
        """Set authentication schemes."""
        self._agent.auth_schemes = auth_schemes
        return self

    def with_tee_details(self, tee_details: AgentTeeDetails) -> "AgentBuilder":
        """Set TEE details."""
        self._agent.tee_details = tee_details
        return self

    def with_skills(self, skills: AgentSkills) -> "AgentBuilder":
        """Set agent skills."""
        self._agent.skills = skills
        return self

    def with_agent_card(self, agent_card: AgentCard) -> "AgentBuilder":
        """Set agent card."""
        self._agent.agent_card = agent_card
        return self

    def public(self, is_public: bool = True) -> "AgentBuilder":
        """Set public visibility."""
        self._agent.is_public = is_public
        return self

    def active(self, is_active: bool = True) -> "AgentBuilder":
        """Set active status."""
        self._agent.is_active = is_active
        return self

    def build(self) -> Agent:
        """Build the agent."""
        return self._agent
