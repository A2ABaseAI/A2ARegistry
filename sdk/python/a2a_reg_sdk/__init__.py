"""
A2A Agent Registry Python SDK

A Python SDK for interacting with the A2A Agent Registry.
Provides easy-to-use classes and methods for agent registration, discovery, and management.
"""

from .client import A2ARegClient
from .models import (
    # Core models
    Agent,
    # A2A Protocol specification models
    AgentProvider,
    AgentCapabilities,
    SecurityScheme,
    AgentSkill,
    AgentInterface,
    AgentCardSignature,
    AgentCardSpec,
    AgentTeeDetails,
    # Builders - A2A Protocol specification
    AgentProviderBuilder,
    AgentCapabilitiesBuilder,
    SecuritySchemeBuilder,
    AgentSkillBuilder,
    AgentInterfaceBuilder,
    AgentCardSignatureBuilder,
    AgentCardSpecBuilder,
    AgentBuilder,
    AgentTeeDetailsBuilder,
)
from .exceptions import A2AError, AuthenticationError, ValidationError, NotFoundError

__version__ = "1.0.0"
__all__ = [
    # Client
    "A2ARegClient",
    # Core models
    "Agent",
    # A2A Protocol specification models
    "AgentProvider",
    "AgentCapabilities",
    "SecurityScheme",
    "AgentSkill",
    "AgentInterface",
    "AgentCardSignature",
    "AgentCardSpec",
    "AgentTeeDetails",
    # Builders - A2A Protocol specification
    "AgentProviderBuilder",
    "AgentCapabilitiesBuilder",
    "SecuritySchemeBuilder",
    "AgentSkillBuilder",
    "AgentInterfaceBuilder",
    "AgentCardSignatureBuilder",
    "AgentCardSpecBuilder",
    "AgentBuilder",
    "AgentTeeDetailsBuilder",
    # Exceptions
    "A2AError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
]
