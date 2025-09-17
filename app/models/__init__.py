"""Database models for the A2A Agent Registry."""

from .agent import Agent
from .client import Client, ClientEntitlement
from .peering import PeerRegistry, PeerSync
from .base import Base

# Import Pydantic schemas for convenience
from ..schemas.agent import AgentCard, AgentCapabilities, AgentAuthScheme, AgentTeeDetails

__all__ = [
    "Base",
    "Agent",
    "AgentCard", 
    "AgentCapabilities",
    "AgentAuthScheme",
    "AgentTeeDetails",
    "Client",
    "ClientEntitlement",
    "PeerRegistry",
    "PeerSync",
]
