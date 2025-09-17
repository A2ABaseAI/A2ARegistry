"""Pydantic schemas for the A2A Agent Registry."""

from .agent import (
    AgentCard,
    AgentCapabilities,
    AgentAuthScheme,
    AgentTeeDetails,
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentSearchRequest,
    AgentSearchResponse,
)
from .client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientEntitlementCreate,
    ClientEntitlementResponse,
)
from .peering import (
    PeerRegistryCreate,
    PeerRegistryUpdate,
    PeerRegistryResponse,
)
from .common import (
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    PaginatedResponse,
)

__all__ = [
    "AgentCard",
    "AgentCapabilities", 
    "AgentAuthScheme",
    "AgentTeeDetails",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentSearchRequest",
    "AgentSearchResponse",
    "ClientCreate",
    "ClientUpdate", 
    "ClientResponse",
    "ClientEntitlementCreate",
    "ClientEntitlementResponse",
    "PeerRegistryCreate",
    "PeerRegistryUpdate",
    "PeerRegistryResponse",
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse",
]
