"""Database models for the A2A Agent Registry."""

# Import Pydantic schemas for convenience
from ..schemas.agent import (
    AgentAuthScheme,
    AgentCapabilities,
    AgentCard,
    AgentTeeDetails,
)
from .agent_core import AgentRecord, AgentVersion, Entitlement
from .base import Base
from .tenant import OAuthClient, Tenant

__all__ = [
    "Base",
    "Tenant",
    "OAuthClient",
    "AgentRecord",
    "AgentVersion",
    "Entitlement",
    "AgentCard",
    "AgentCapabilities",
    "AgentAuthScheme",
    "AgentTeeDetails",
]
