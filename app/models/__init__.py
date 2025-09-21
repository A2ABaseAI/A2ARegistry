"""Database models for the A2A Agent Registry."""

# Import Pydantic schemas for convenience
from ..schemas.agent import (
    AgentAuthScheme,
    AgentCapabilities,
    AgentCard,
    AgentTeeDetails,
)
from .agent import Agent
from .base import Base
from .client import Client, ClientEntitlement

__all__ = [
    "Base",
    "Agent",
    "AgentCard",
    "AgentCapabilities",
    "AgentAuthScheme",
    "AgentTeeDetails",
    "Client",
    "ClientEntitlement",
]
