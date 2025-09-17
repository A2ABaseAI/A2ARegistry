"""Pydantic schemas for the A2A Agent Registry."""

from .agent import (
    AgentAuthScheme,
    AgentCapabilities,
    AgentCard,
    AgentCreate,
    AgentResponse,
    AgentSearchRequest,
    AgentSearchResponse,
    AgentTeeDetails,
    AgentUpdate,
)
from .client import (
    ClientCreate,
    ClientEntitlementCreate,
    ClientEntitlementResponse,
    ClientResponse,
    ClientUpdate,
)
from .common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
)
from .peering import (
    PeerRegistryCreate,
    PeerRegistryResponse,
    PeerRegistryUpdate,
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
