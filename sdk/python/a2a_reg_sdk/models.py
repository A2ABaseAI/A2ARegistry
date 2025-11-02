"""
A2A Registry Data Models

Data models for A2A agents and related entities following the A2A Protocol specification.
This module implements the Agent Card schema as defined in Section 5.5 of the A2A Protocol.

Reference: https://a2a-protocol.org/dev/specification/#355-extension-method-naming
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json


@dataclass
class AgentProvider:
    """Agent Provider Object - Service provider information for the Agent.
    
    Section 5.5.1 of the A2A Protocol specification.
    """

    organization: str
    url: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProvider":
        """Create from dictionary."""
        return cls(
            organization=data["organization"],
            url=data["url"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "organization": self.organization,
            "url": self.url,
        }


@dataclass
class AgentCapabilities:
    """Agent Capabilities Object - Optional capabilities supported by the Agent.
    
    Section 5.5.2 of the A2A Protocol specification defines these capability flags
    that indicate what optional features the Agent supports.
    """

    streaming: Optional[bool] = None
    pushNotifications: Optional[bool] = None
    stateTransitionHistory: Optional[bool] = None
    supportsAuthenticatedExtendedCard: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCapabilities":
        """Create from dictionary."""
        return cls(
            streaming=data.get("streaming"),
            pushNotifications=data.get("pushNotifications"),
            stateTransitionHistory=data.get("stateTransitionHistory"),
            supportsAuthenticatedExtendedCard=data.get("supportsAuthenticatedExtendedCard"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.streaming is not None:
            result["streaming"] = self.streaming
        if self.pushNotifications is not None:
            result["pushNotifications"] = self.pushNotifications
        if self.stateTransitionHistory is not None:
            result["stateTransitionHistory"] = self.stateTransitionHistory
        if self.supportsAuthenticatedExtendedCard is not None:
            result["supportsAuthenticatedExtendedCard"] = self.supportsAuthenticatedExtendedCard
        return result


@dataclass
class SecurityScheme:
    """Security Scheme Object - Authentication requirements for the Agent.
    
    Section 5.5.3 of the A2A Protocol specification. Defines how clients should
    authenticate when interacting with the Agent.
    """

    type: str  # apiKey, oauth2, jwt, mTLS
    location: Optional[str] = None  # header, query, body
    name: Optional[str] = None  # Parameter name for credentials
    flow: Optional[str] = None  # OAuth2 flow type
    tokenUrl: Optional[str] = None  # OAuth2 token URL
    scopes: Optional[List[str]] = None  # OAuth2 scopes
    credentials: Optional[str] = None  # Credentials for private Cards

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityScheme":
        """Create from dictionary."""
        return cls(
            type=data["type"],
            location=data.get("location"),
            name=data.get("name"),
            flow=data.get("flow"),
            tokenUrl=data.get("tokenUrl"),
            scopes=data.get("scopes"),
            credentials=data.get("credentials"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"type": self.type}
        if self.location is not None:
            result["location"] = self.location
        if self.name is not None:
            result["name"] = self.name
        if self.flow is not None:
            result["flow"] = self.flow
        if self.tokenUrl is not None:
            result["tokenUrl"] = self.tokenUrl
        if self.scopes is not None:
            result["scopes"] = self.scopes
        if self.credentials is not None:
            result["credentials"] = self.credentials
        return result




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
class AgentSkill:
    """Agent Skill Object - Collection of capability units the Agent can perform.
    
    Section 5.5.4 of the A2A Protocol specification. Each skill represents a specific
    capability or task that the Agent can execute.
    """

    id: str
    name: str
    description: str
    tags: List[str]
    examples: Optional[List[str]] = None
    inputModes: Optional[List[str]] = None
    outputModes: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSkill":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            tags=data["tags"],
            examples=data.get("examples"),
            inputModes=data.get("inputModes"),
            outputModes=data.get("outputModes"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
        }
        if self.examples is not None:
            result["examples"] = self.examples
        if self.inputModes is not None:
            result["inputModes"] = self.inputModes
        if self.outputModes is not None:
            result["outputModes"] = self.outputModes
        return result


@dataclass
class AgentInterface:
    """Agent Interface Object - Transport and interaction capabilities.
    
    Section 5.5.5 of the A2A Protocol specification. Defines how clients should
    communicate with the Agent, including transport protocols and data formats.
    """

    preferredTransport: str  # jsonrpc, grpc, http
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    additionalInterfaces: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInterface":
        """Create from dictionary."""
        return cls(
            preferredTransport=data["preferredTransport"],
            defaultInputModes=data["defaultInputModes"],
            defaultOutputModes=data["defaultOutputModes"],
            additionalInterfaces=data.get("additionalInterfaces"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "preferredTransport": self.preferredTransport,
            "defaultInputModes": self.defaultInputModes,
            "defaultOutputModes": self.defaultOutputModes,
        }
        if self.additionalInterfaces is not None:
            result["additionalInterfaces"] = self.additionalInterfaces
        return result


@dataclass
class AgentCardSignature:
    """Agent Card Signature Object - Digital signature information.
    
    Section 5.5.6 of the A2A Protocol specification. Provides cryptographic
    verification of the Agent Card's integrity and authenticity.
    """

    algorithm: Optional[str] = None
    signature: Optional[str] = None
    jwksUrl: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCardSignature":
        """Create from dictionary."""
        return cls(
            algorithm=data.get("algorithm"),
            signature=data.get("signature"),
            jwksUrl=data.get("jwksUrl"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.algorithm is not None:
            result["algorithm"] = self.algorithm
        if self.signature is not None:
            result["signature"] = self.signature
        if self.jwksUrl is not None:
            result["jwksUrl"] = self.jwksUrl
        return result


@dataclass
class AgentCardSpec:
    """Agent Card specification following A2A Protocol specification.
    
    This class implements the complete Agent Card structure as defined in the
    A2A Protocol specification, Section 5.5. The Agent Card is a JSON document
    that describes an agent's capabilities, endpoints, and metadata, facilitating
    agent discovery and interoperability.
    
    Reference: https://a2a-protocol.org/dev/specification/#355-extension-method-naming
    """

    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    securitySchemes: Dict[str, SecurityScheme]  # Changed from List to Dict for ADK compatibility
    skills: List[AgentSkill]
    interface: AgentInterface
    provider: Optional[AgentProvider] = None
    documentationUrl: Optional[str] = None
    signature: Optional[AgentCardSignature] = None
    defaultInputModes: Optional[List[str]] = None  # ADK-compatible top-level field
    defaultOutputModes: Optional[List[str]] = None  # ADK-compatible top-level field

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCardSpec":
        """Create from dictionary."""
        provider = None
        if data.get("provider"):
            provider = AgentProvider.from_dict(data["provider"])

        capabilities = AgentCapabilities.from_dict(data.get("capabilities", {}))

        # Handle securitySchemes as either List or Dict for backward compatibility
        security_schemes_data = data.get("securitySchemes", {})
        security_schemes: Dict[str, SecurityScheme] = {}
        if isinstance(security_schemes_data, list):
            # Convert list to dict keyed by type
            for scheme_data in security_schemes_data:
                scheme = SecurityScheme.from_dict(scheme_data)
                security_schemes[scheme.type] = scheme
        elif isinstance(security_schemes_data, dict):
            # Already a dict, convert values
            for key, scheme_data in security_schemes_data.items():
                if isinstance(scheme_data, SecurityScheme):
                    security_schemes[key] = scheme_data
                else:
                    security_schemes[key] = SecurityScheme.from_dict(scheme_data)
        else:
            security_schemes = {}

        skills = []
        for skill_data in data.get("skills", []):
            skills.append(AgentSkill.from_dict(skill_data))

        interface = AgentInterface.from_dict(data["interface"])

        signature = None
        if data.get("signature"):
            signature = AgentCardSignature.from_dict(data["signature"])

        # Get top-level defaultInputModes and defaultOutputModes, or copy from interface
        default_input_modes = data.get("defaultInputModes")
        if default_input_modes is None and interface and interface.defaultInputModes:
            default_input_modes = interface.defaultInputModes

        default_output_modes = data.get("defaultOutputModes")
        if default_output_modes is None and interface and interface.defaultOutputModes:
            default_output_modes = interface.defaultOutputModes

        return cls(
            name=data["name"],
            description=data["description"],
            url=data["url"],
            version=data["version"],
            provider=provider,
            capabilities=capabilities,
            securitySchemes=security_schemes,
            skills=skills,
            interface=interface,
            documentationUrl=data.get("documentationUrl"),
            signature=signature,
            defaultInputModes=default_input_modes,
            defaultOutputModes=default_output_modes,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "capabilities": self.capabilities.to_dict(),
            "securitySchemes": {key: scheme.to_dict() for key, scheme in self.securitySchemes.items()},
            "skills": [skill.to_dict() for skill in self.skills],
            "interface": self.interface.to_dict(),
        }
        if self.provider is not None:
            result["provider"] = self.provider.to_dict()
        if self.documentationUrl is not None:
            result["documentationUrl"] = self.documentationUrl
        if self.signature is not None:
            result["signature"] = self.signature.to_dict()
        # Add top-level defaultInputModes and defaultOutputModes for ADK compatibility
        if self.defaultInputModes is not None:
            result["defaultInputModes"] = self.defaultInputModes
        elif self.interface and self.interface.defaultInputModes:
            result["defaultInputModes"] = self.interface.defaultInputModes
        if self.defaultOutputModes is not None:
            result["defaultOutputModes"] = self.defaultOutputModes
        elif self.interface and self.interface.defaultOutputModes:
            result["defaultOutputModes"] = self.interface.defaultOutputModes
        return result


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
    auth_schemes: List[SecurityScheme] = field(default_factory=list)
    tee_details: Optional[AgentTeeDetails] = None
    skills: Optional[List[AgentSkill]] = None
    agent_card: Optional[AgentCardSpec] = None
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
            auth_schemes.append(SecurityScheme.from_dict(scheme_data))

        tee_details = None
        if data.get("tee_details"):
            tee_details = AgentTeeDetails.from_dict(data["tee_details"])

        skills = None
        if data.get("skills"):
            if isinstance(data["skills"], list):
                skills = [AgentSkill.from_dict(skill_data) for skill_data in data["skills"]]
            else:
                # Legacy format - convert to list of AgentSkill
                skills = []

        agent_card = None
        if data.get("agent_card"):
            agent_card = AgentCardSpec.from_dict(data["agent_card"])

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
            "skills": [skill.to_dict() for skill in self.skills] if self.skills else None,
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


# Fluent Builder classes for A2A Protocol specification


class AgentProviderBuilder:
    """Fluent builder for creating AgentProvider objects."""

    def __init__(self, organization: str, url: str):
        """Initialize builder with required fields."""
        self._provider = AgentProvider(organization=organization, url=url)

    def build(self) -> AgentProvider:
        """Build the AgentProvider."""
        return self._provider


class AgentCapabilitiesBuilder:
    """Fluent builder for creating AgentCapabilities objects."""

    def __init__(self):
        self._capabilities = AgentCapabilities()

    def streaming(self, enabled: bool = True) -> "AgentCapabilitiesBuilder":
        """Enable/disable Server-Sent Events (SSE) support."""
        self._capabilities.streaming = enabled
        return self

    def push_notifications(self, enabled: bool = True) -> "AgentCapabilitiesBuilder":
        """Enable/disable push notifications capability."""
        self._capabilities.pushNotifications = enabled
        return self

    def state_transition_history(self, enabled: bool = True) -> "AgentCapabilitiesBuilder":
        """Enable/disable task state change history exposure."""
        self._capabilities.stateTransitionHistory = enabled
        return self

    def supports_authenticated_extended_card(self, enabled: bool = True) -> "AgentCapabilitiesBuilder":
        """Enable/disable authenticated extended card retrieval."""
        self._capabilities.supportsAuthenticatedExtendedCard = enabled
        return self

    def build(self) -> AgentCapabilities:
        """Build the AgentCapabilities."""
        return self._capabilities


class SecuritySchemeBuilder:
    """Fluent builder for creating SecurityScheme objects."""

    def __init__(self, scheme_type: str):
        """Initialize builder with authentication type (apiKey, oauth2, jwt, mTLS)."""
        self._scheme = SecurityScheme(type=scheme_type)

    def location(self, location: str) -> "SecuritySchemeBuilder":
        """Set location of credentials (header, query, body)."""
        self._scheme.location = location
        return self

    def name(self, name: str) -> "SecuritySchemeBuilder":
        """Set parameter name for credentials (e.g., 'Authorization', 'X-API-Key')."""
        self._scheme.name = name
        return self

    def flow(self, flow: str) -> "SecuritySchemeBuilder":
        """Set OAuth2 flow type (e.g., 'client_credentials', 'authorization_code')."""
        self._scheme.flow = flow
        return self

    def token_url(self, token_url: str) -> "SecuritySchemeBuilder":
        """Set OAuth2 token URL for obtaining access tokens."""
        self._scheme.tokenUrl = token_url
        return self

    def scopes(self, scopes: List[str]) -> "SecuritySchemeBuilder":
        """Set OAuth2 scopes required for access."""
        self._scheme.scopes = scopes
        return self

    def credentials(self, credentials: str) -> "SecuritySchemeBuilder":
        """Set credentials for the client to use for private Cards."""
        self._scheme.credentials = credentials
        return self

    def build(self) -> SecurityScheme:
        """Build the SecurityScheme."""
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


class AgentSkillBuilder:
    """Fluent builder for creating AgentSkill objects."""

    def __init__(self, skill_id: str, name: str, description: str, tags: List[str]):
        """Initialize builder with required fields."""
        self._skill = AgentSkill(id=skill_id, name=name, description=description, tags=tags)

    def examples(self, examples: List[str]) -> "AgentSkillBuilder":
        """Set example scenarios or prompts the skill can execute."""
        self._skill.examples = examples
        return self

    def input_modes(self, input_modes: List[str]) -> "AgentSkillBuilder":
        """Set input MIME types supported by the skill."""
        self._skill.inputModes = input_modes
        return self

    def output_modes(self, output_modes: List[str]) -> "AgentSkillBuilder":
        """Set output MIME types supported by the skill."""
        self._skill.outputModes = output_modes
        return self

    def build(self) -> AgentSkill:
        """Build the AgentSkill."""
        return self._skill


class AgentInterfaceBuilder:
    """Fluent builder for creating AgentInterface objects."""

    def __init__(self, preferred_transport: str, default_input_modes: List[str], default_output_modes: List[str]):
        """Initialize builder with required fields."""
        self._interface = AgentInterface(
            preferredTransport=preferred_transport,
            defaultInputModes=default_input_modes,
            defaultOutputModes=default_output_modes,
        )

    def additional_interface(self, transport: str, url: str) -> "AgentInterfaceBuilder":
        """Add an additional transport interface."""
        if self._interface.additionalInterfaces is None:
            self._interface.additionalInterfaces = []
        self._interface.additionalInterfaces.append({"transport": transport, "url": url})
        return self

    def build(self) -> AgentInterface:
        """Build the AgentInterface."""
        return self._interface


class AgentCardSignatureBuilder:
    """Fluent builder for creating AgentCardSignature objects."""

    def __init__(self):
        self._signature = AgentCardSignature()

    def algorithm(self, algorithm: str) -> "AgentCardSignatureBuilder":
        """Set signature algorithm (e.g., 'RS256', 'ES256')."""
        self._signature.algorithm = algorithm
        return self

    def signature(self, signature: str) -> "AgentCardSignatureBuilder":
        """Set digital signature value (base64-encoded)."""
        self._signature.signature = signature
        return self

    def jwks_url(self, jwks_url: str) -> "AgentCardSignatureBuilder":
        """Set JWKS URL for signature verification."""
        self._signature.jwksUrl = jwks_url
        return self

    def build(self) -> AgentCardSignature:
        """Build the AgentCardSignature."""
        return self._signature


class AgentCardSpecBuilder:
    """Fluent builder for creating AgentCardSpec objects following A2A Protocol specification."""

    def __init__(self, name: str, description: str, url: str, version: str):
        """Initialize builder with required core fields."""
        self._card_spec = AgentCardSpec(
            name=name,
            description=description,
            url=url,
            version=version,
            capabilities=AgentCapabilities(),
            securitySchemes={},  # Changed from [] to {} for ADK compatibility
            skills=[],
            interface=None,  # Will be set via with_interface
        )

    def with_provider(self, organization: str, provider_url: str) -> "AgentCardSpecBuilder":
        """Set agent provider information."""
        self._card_spec.provider = AgentProvider(organization=organization, url=provider_url)
        return self

    def with_provider_builder(self, provider: AgentProvider) -> "AgentCardSpecBuilder":
        """Set agent provider using AgentProviderBuilder."""
        self._card_spec.provider = provider
        return self

    def with_capabilities(self, capabilities: AgentCapabilities) -> "AgentCardSpecBuilder":
        """Set agent capabilities."""
        self._card_spec.capabilities = capabilities
        return self

    def with_capabilities_builder(self, builder: AgentCapabilitiesBuilder) -> "AgentCardSpecBuilder":
        """Set agent capabilities using AgentCapabilitiesBuilder."""
        self._card_spec.capabilities = builder.build()
        return self

    def add_security_scheme(self, scheme: SecurityScheme) -> "AgentCardSpecBuilder":
        """Add a security scheme (dict format for ADK compatibility)."""
        self._card_spec.securitySchemes[scheme.type] = scheme
        return self

    def add_security_scheme_builder(self, builder: SecuritySchemeBuilder) -> "AgentCardSpecBuilder":
        """Add a security scheme using SecuritySchemeBuilder (dict format for ADK compatibility)."""
        scheme = builder.build()
        self._card_spec.securitySchemes[scheme.type] = scheme
        return self

    def add_skill(self, skill: AgentSkill) -> "AgentCardSpecBuilder":
        """Add an agent skill."""
        self._card_spec.skills.append(skill)
        return self

    def add_skill_builder(self, builder: AgentSkillBuilder) -> "AgentCardSpecBuilder":
        """Add an agent skill using AgentSkillBuilder."""
        self._card_spec.skills.append(builder.build())
        return self

    def with_interface(self, interface: AgentInterface) -> "AgentCardSpecBuilder":
        """Set agent interface."""
        self._card_spec.interface = interface
        return self

    def with_interface_builder(self, builder: AgentInterfaceBuilder) -> "AgentCardSpecBuilder":
        """Set agent interface using AgentInterfaceBuilder."""
        self._card_spec.interface = builder.build()
        return self

    def documentation_url(self, url: str) -> "AgentCardSpecBuilder":
        """Set documentation URL."""
        self._card_spec.documentationUrl = url
        return self

    def with_signature(self, signature: AgentCardSignature) -> "AgentCardSpecBuilder":
        """Set agent card signature."""
        self._card_spec.signature = signature
        return self

    def with_signature_builder(self, builder: AgentCardSignatureBuilder) -> "AgentCardSpecBuilder":
        """Set agent card signature using AgentCardSignatureBuilder."""
        self._card_spec.signature = builder.build()
        return self

    def build(self) -> AgentCardSpec:
        """Build the AgentCardSpec."""
        if self._card_spec.interface is None:
            raise ValueError("AgentInterface is required. Use with_interface() or with_interface_builder()")
        
        # Auto-populate defaultInputModes and defaultOutputModes from interface if not set
        if self._card_spec.defaultInputModes is None and self._card_spec.interface.defaultInputModes:
            self._card_spec.defaultInputModes = list(self._card_spec.interface.defaultInputModes)
        if self._card_spec.defaultOutputModes is None and self._card_spec.interface.defaultOutputModes:
            self._card_spec.defaultOutputModes = list(self._card_spec.interface.defaultOutputModes)
        
        return self._card_spec


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

    def with_auth_schemes(self, auth_schemes: List[SecurityScheme]) -> "AgentBuilder":
        """Set authentication schemes."""
        self._agent.auth_schemes = auth_schemes
        return self

    def with_tee_details(self, tee_details: AgentTeeDetails) -> "AgentBuilder":
        """Set TEE details."""
        self._agent.tee_details = tee_details
        return self

    def with_skills(self, skills: List[AgentSkill]) -> "AgentBuilder":
        """Set agent skills."""
        self._agent.skills = skills
        return self

    def with_agent_card(self, agent_card: AgentCardSpec) -> "AgentBuilder":
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
