"""Core production utilities."""

from .caching import AgentCache, CacheManager, CacheWarmer
from .exceptions import (
    A2ARegistryException,
    AccessDeniedError,
    AgentNotFoundError,
    CacheError,
    CircuitBreaker,
    # ClientNotFoundError (removed: no client module)
    DatabaseError,
    ExternalServiceError,
    # FederationError (removed: no peering)
    RateLimitExceededError,
    RetryConfig,
    # SearchServiceError (deprecated export)
    ValidationError,
    handle_a2a_exception,
    handle_generic_exception,
    retry_on_exception,
)
from .logging import RequestLoggingMiddleware, get_logger, setup_logging
from .monitoring import HealthChecker, MetricsCollector, MetricsMiddleware
from .security import (
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "RequestLoggingMiddleware",
    "MetricsMiddleware",
    "HealthChecker",
    "MetricsCollector",
    "RateLimitMiddleware",
    "RequestSizeLimitMiddleware",
    "CacheManager",
    "AgentCache",
    "CacheWarmer",
    "A2ARegistryException",
    "AgentNotFoundError",
    "AccessDeniedError",
    "ValidationError",
    "RateLimitExceededError",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
    "handle_a2a_exception",
    "handle_generic_exception",
    "RetryConfig",
    "retry_on_exception",
    "CircuitBreaker",
]
