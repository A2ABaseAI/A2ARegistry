"""
A2A Agent Registry Python SDK

A Python SDK for interacting with the A2A Agent Registry.
Provides easy-to-use classes and methods for agent registration, discovery, and management.
"""

from .client import A2AClient
from .models import (
    Agent,
    AgentCard,
    AgentCapabilities,
    AuthScheme,
    AgentTeeDetails,
    AgentSkills,
    AgentBuilder,
    AgentCapabilitiesBuilder,
    AuthSchemeBuilder,
    AgentTeeDetailsBuilder,
    AgentSkillsBuilder,
    InputSchemaBuilder,
    OutputSchemaBuilder,
)
from .exceptions import A2AError, AuthenticationError, ValidationError, NotFoundError
from .publisher import AgentPublisher

__version__ = "1.0.0"
__all__ = [
    "A2AClient",
    "Agent",
    "AgentCard",
    "AgentCapabilities",
    "AuthScheme",
    "AgentTeeDetails",
    "AgentSkills",
    "AgentBuilder",
    "AgentCapabilitiesBuilder",
    "AuthSchemeBuilder",
    "AgentTeeDetailsBuilder",
    "AgentSkillsBuilder",
    "InputSchemaBuilder",
    "OutputSchemaBuilder",
    "AgentPublisher",
    "A2AError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
]
