"""Database models for the A2A Agent Registry."""

# Import Pydantic schemas for convenience
from ..schemas.agent import (
    AgentAuthScheme,
    AgentCapabilities,
    AgentCard,
    AgentTeeDetails,
)
from .tenant import Tenant, OAuthClient
from .agent_core import AgentRecord, AgentVersion, Entitlement
from .base import Base

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
