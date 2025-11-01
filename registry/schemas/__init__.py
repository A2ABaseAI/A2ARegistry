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
from .common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
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
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse",
]
