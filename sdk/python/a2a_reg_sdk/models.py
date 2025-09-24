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
    def from_dict(cls, data: Union[Dict[str, Any], List[Any]]) -> "AgentSkills":
        """Create from dictionary."""
        # Handle case where data is a list (from API response)
        if isinstance(data, list):
            return cls(
                input_schema={},
                output_schema={},
                examples=[],
            )

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
            author=data.get("author") or data.get("provider", {}).get("organization", "Unknown"),
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
            id=data.get("id") or data.get("agentId"),
            name=data["name"],
            description=data["description"],
            version=data["version"],
            provider=data.get("provider") or data.get("publisherId", "unknown"),
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


class AgentCapabilitiesBuilder:
    """Builder class for creating AgentCapabilities objects."""

    def __init__(self):
        self._capabilities = AgentCapabilities()

    def protocols(self, protocols: List[str]) -> "AgentCapabilitiesBuilder":
        """Set supported protocols."""
        self._capabilities.protocols = protocols
        return self

    def supported_formats(self, formats: List[str]) -> "AgentCapabilitiesBuilder":
        """Set supported formats."""
        self._capabilities.supported_formats = formats
        return self

    def max_request_size(self, size: int) -> "AgentCapabilitiesBuilder":
        """Set maximum request size."""
        self._capabilities.max_request_size = size
        return self

    def max_concurrent_requests(self, count: int) -> "AgentCapabilitiesBuilder":
        """Set maximum concurrent requests."""
        self._capabilities.max_concurrent_requests = count
        return self

    def a2a_version(self, version: str) -> "AgentCapabilitiesBuilder":
        """Set A2A version."""
        self._capabilities.a2a_version = version
        return self

    def build(self) -> AgentCapabilities:
        """Build the capabilities."""
        return self._capabilities


class AuthSchemeBuilder:
    """Builder class for creating AuthScheme objects."""

    def __init__(self, auth_type: str):
        self._scheme = AuthScheme(type=auth_type)

    def description(self, description: str) -> "AuthSchemeBuilder":
        """Set description."""
        self._scheme.description = description
        return self

    def required(self, required: bool = True) -> "AuthSchemeBuilder":
        """Set required flag."""
        self._scheme.required = required
        return self

    def header_name(self, header_name: str) -> "AuthSchemeBuilder":
        """Set header name."""
        self._scheme.header_name = header_name
        return self

    def query_param(self, query_param: str) -> "AuthSchemeBuilder":
        """Set query parameter."""
        self._scheme.query_param = query_param
        return self

    def build(self) -> AuthScheme:
        """Build the auth scheme."""
        return self._scheme


class AgentTeeDetailsBuilder:
    """Builder class for creating AgentTeeDetails objects."""

    def __init__(self):
        self._tee = AgentTeeDetails()

    def enabled(self, enabled: bool = True) -> "AgentTeeDetailsBuilder":
        """Set TEE enabled status."""
        self._tee.enabled = enabled
        return self

    def provider(self, provider: str) -> "AgentTeeDetailsBuilder":
        """Set TEE provider."""
        self._tee.provider = provider
        return self

    def attestation(self, attestation: str) -> "AgentTeeDetailsBuilder":
        """Set attestation."""
        self._tee.attestation = attestation
        return self

    def build(self) -> AgentTeeDetails:
        """Build the TEE details."""
        return self._tee


class AgentSkillsBuilder:
    """Builder class for creating AgentSkills objects."""

    def __init__(self):
        self._skills = AgentSkills()

    def input_schema(self, schema: Dict[str, Any]) -> "AgentSkillsBuilder":
        """Set input schema."""
        self._skills.input_schema = schema
        return self

    def output_schema(self, schema: Dict[str, Any]) -> "AgentSkillsBuilder":
        """Set output schema."""
        self._skills.output_schema = schema
        return self

    def examples(self, examples: List[str]) -> "AgentSkillsBuilder":
        """Set examples."""
        self._skills.examples = examples
        return self

    def with_input_schema_builder(self, schema_builder: "InputSchemaBuilder") -> "AgentSkillsBuilder":
        """Set input schema using InputSchemaBuilder."""
        self._skills.input_schema = schema_builder.build()
        return self

    def with_output_schema_builder(self, schema_builder: "OutputSchemaBuilder") -> "AgentSkillsBuilder":
        """Set output schema using OutputSchemaBuilder."""
        self._skills.output_schema = schema_builder.build()
        return self

    def build(self) -> AgentSkills:
        """Build the skills."""
        return self._skills


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


class InputSchemaBuilder:
    """Builder class for creating input schemas."""

    def __init__(self):
        self._schema: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    def add_property(self, name: str, property_type: str, description: Optional[str] = None, required: bool = False, **kwargs) -> "InputSchemaBuilder":
        """Add a property to the schema."""
        prop = {"type": property_type}
        if description:
            prop["description"] = description

        # Add any additional properties
        prop.update(kwargs)

        self._schema["properties"][name] = prop

        if required:
            if name not in self._schema["required"]:
                self._schema["required"].append(name)

        return self

    def add_string_property(
        self,
        name: str,
        description: Optional[str] = None,
        required: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
    ) -> "InputSchemaBuilder":
        """Add a string property."""
        kwargs: Dict[str, Any] = {}
        if min_length is not None:
            kwargs["minLength"] = min_length
        if max_length is not None:
            kwargs["maxLength"] = max_length
        if pattern:
            kwargs["pattern"] = pattern

        return self.add_property(name, "string", description, required, **kwargs)

    def add_number_property(
        self, name: str, description: Optional[str] = None, required: bool = False, minimum: Optional[float] = None, maximum: Optional[float] = None
    ) -> "InputSchemaBuilder":
        """Add a number property."""
        kwargs = {}
        if minimum is not None:
            kwargs["minimum"] = minimum
        if maximum is not None:
            kwargs["maximum"] = maximum

        return self.add_property(name, "number", description, required, **kwargs)

    def add_integer_property(
        self, name: str, description: Optional[str] = None, required: bool = False, minimum: Optional[int] = None, maximum: Optional[int] = None
    ) -> "InputSchemaBuilder":
        """Add an integer property."""
        kwargs = {}
        if minimum is not None:
            kwargs["minimum"] = minimum
        if maximum is not None:
            kwargs["maximum"] = maximum

        return self.add_property(name, "integer", description, required, **kwargs)

    def add_boolean_property(self, name: str, description: Optional[str] = None, required: bool = False) -> "InputSchemaBuilder":
        """Add a boolean property."""
        return self.add_property(name, "boolean", description, required)

    def add_array_property(
        self,
        name: str,
        item_type: str,
        description: Optional[str] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> "InputSchemaBuilder":
        """Add an array property."""
        kwargs: Dict[str, Any] = {"items": {"type": item_type}}
        if min_items is not None:
            kwargs["minItems"] = min_items
        if max_items is not None:
            kwargs["maxItems"] = max_items

        return self.add_property(name, "array", description, required, **kwargs)

    def add_object_property(self, name: str, properties: Dict[str, Any], description: Optional[str] = None, required: bool = False) -> "InputSchemaBuilder":
        """Add an object property."""
        return self.add_property(name, "object", description, required, properties=properties)

    def set_required(self, required_fields: List[str]) -> "InputSchemaBuilder":
        """Set required fields."""
        self._schema["required"] = required_fields
        return self

    def add_required(self, field_name: str) -> "InputSchemaBuilder":
        """Add a required field."""
        if field_name not in self._schema["required"]:
            self._schema["required"].append(field_name)
        return self

    def build(self) -> Dict[str, Any]:
        """Build the input schema."""
        return self._schema.copy()


class OutputSchemaBuilder:
    """Builder class for creating output schemas."""

    def __init__(self):
        self._schema: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    def add_property(self, name: str, property_type: str, description: Optional[str] = None, required: bool = False, **kwargs) -> "OutputSchemaBuilder":
        """Add a property to the schema."""
        prop = {"type": property_type}
        if description:
            prop["description"] = description

        # Add any additional properties
        prop.update(kwargs)

        self._schema["properties"][name] = prop

        if required:
            if name not in self._schema["required"]:
                self._schema["required"].append(name)

        return self

    def add_string_property(
        self, name: str, description: Optional[str] = None, required: bool = False, min_length: Optional[int] = None, max_length: Optional[int] = None
    ) -> "OutputSchemaBuilder":
        """Add a string property."""
        kwargs = {}
        if min_length is not None:
            kwargs["minLength"] = min_length
        if max_length is not None:
            kwargs["maxLength"] = max_length

        return self.add_property(name, "string", description, required, **kwargs)

    def add_number_property(
        self, name: str, description: Optional[str] = None, required: bool = False, minimum: Optional[float] = None, maximum: Optional[float] = None
    ) -> "OutputSchemaBuilder":
        """Add a number property."""
        kwargs = {}
        if minimum is not None:
            kwargs["minimum"] = minimum
        if maximum is not None:
            kwargs["maximum"] = maximum

        return self.add_property(name, "number", description, required, **kwargs)

    def add_integer_property(
        self, name: str, description: Optional[str] = None, required: bool = False, minimum: Optional[int] = None, maximum: Optional[int] = None
    ) -> "OutputSchemaBuilder":
        """Add an integer property."""
        kwargs = {}
        if minimum is not None:
            kwargs["minimum"] = minimum
        if maximum is not None:
            kwargs["maximum"] = maximum

        return self.add_property(name, "integer", description, required, **kwargs)

    def add_boolean_property(self, name: str, description: Optional[str] = None, required: bool = False) -> "OutputSchemaBuilder":
        """Add a boolean property."""
        return self.add_property(name, "boolean", description, required)

    def add_array_property(
        self,
        name: str,
        item_type: str,
        description: Optional[str] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> "OutputSchemaBuilder":
        """Add an array property."""
        kwargs: Dict[str, Any] = {"items": {"type": item_type}}
        if min_items is not None:
            kwargs["minItems"] = min_items
        if max_items is not None:
            kwargs["maxItems"] = max_items

        return self.add_property(name, "array", description, required, **kwargs)

    def add_object_property(self, name: str, properties: Dict[str, Any], description: Optional[str] = None, required: bool = False) -> "OutputSchemaBuilder":
        """Add an object property."""
        return self.add_property(name, "object", description, required, properties=properties)

    def set_required(self, required_fields: List[str]) -> "OutputSchemaBuilder":
        """Set required fields."""
        self._schema["required"] = required_fields
        return self

    def add_required(self, field_name: str) -> "OutputSchemaBuilder":
        """Add a required field."""
        if field_name not in self._schema["required"]:
            self._schema["required"].append(field_name)
        return self

    def build(self) -> Dict[str, Any]:
        """Build the output schema."""
        return self._schema.copy()
