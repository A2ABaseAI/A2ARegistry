"""Custom exceptions and error handling."""

import time
from typing import Any, Dict, Optional, Type

from fastapi import HTTPException, status

from registry.core.logging import get_logger

logger = get_logger(__name__)


class A2ARegistryException(Exception):
    """Base exception for A2A Registry."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AgentNotFoundError(A2ARegistryException):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            error_code="AGENT_NOT_FOUND",
            details={"agent_id": agent_id},
        )


class ClientNotFoundError(A2ARegistryException):
    """Raised when a client is not found."""

    def __init__(self, client_id: str):
        super().__init__(
            message=f"Client not found: {client_id}",
            error_code="CLIENT_NOT_FOUND",
            details={"client_id": client_id},
        )


class AccessDeniedError(A2ARegistryException):
    """Raised when access is denied."""

    def __init__(self, resource: str, reason: str = "Insufficient permissions"):
        super().__init__(
            message=f"Access denied to {resource}: {reason}",
            error_code="ACCESS_DENIED",
            details={"resource": resource, "reason": reason},
        )


class ValidationError(A2ARegistryException):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(
            message=f"Validation error for {field}: {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "message": message, "value": value},
        )


class RateLimitExceededError(A2ARegistryException):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: str = "1 minute"):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window},
        )


class SearchServiceError(A2ARegistryException):
    """Raised when search service fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Search service error during {operation}: {reason}",
            error_code="SEARCH_SERVICE_ERROR",
            details={"operation": operation, "reason": reason},
        )


class FederationError(A2ARegistryException):
    """Raised when federation operations fail."""

    def __init__(self, peer_id: str, operation: str, reason: str):
        super().__init__(
            message=(f"Federation error with peer {peer_id} during {operation}: {reason}"),
            error_code="FEDERATION_ERROR",
            details={"peer_id": peer_id, "operation": operation, "reason": reason},
        )


class DatabaseError(A2ARegistryException):
    """Raised when database operations fail."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database error during {operation}: {reason}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "reason": reason},
        )


class CacheError(A2ARegistryException):
    """Raised when cache operations fail."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Cache error during {operation}: {reason}",
            error_code="CACHE_ERROR",
            details={"operation": operation, "reason": reason},
        )


class ExternalServiceError(A2ARegistryException):
    """Raised when external service calls fail."""

    def __init__(self, service: str, operation: str, reason: str):
        super().__init__(
            message=(f"External service error with {service} during {operation}: {reason}"),
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "operation": operation, "reason": reason},
        )


# Error response models
class ErrorResponse:
    """Standardized error response."""

    def __init__(
        self,
        error: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        self.error = error
        self.error_code = error_code
        self.details = details or {}
        self.request_id = request_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        response: Dict[str, Any] = {"error": self.error, "timestamp": self._get_timestamp()}

        if self.error_code:
            response["error_code"] = self.error_code

        if self.details:
            response["details"] = self.details

        if self.request_id:
            response["request_id"] = self.request_id

        return response

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.utcnow().isoformat()


# Exception handlers
def handle_a2a_exception(exc: A2ARegistryException, request_id: Optional[str] = None) -> HTTPException:
    """Convert A2A exception to HTTP exception."""

    # Log the exception
    logger.error(
        f"A2A Registry exception: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "request_id": request_id,
        },
    )

    # Map error codes to HTTP status codes
    status_mapping = {
        "AGENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CLIENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "ACCESS_DENIED": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "SEARCH_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "FEDERATION_ERROR": status.HTTP_502_BAD_GATEWAY,
        "DATABASE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "CACHE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
    }

    http_status = status_mapping.get(exc.error_code or "UNKNOWN_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)

    error_response = ErrorResponse(
        error=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        request_id=request_id,
    )

    return HTTPException(status_code=http_status, detail=error_response.to_dict())


def handle_generic_exception(exc: Exception, request_id: Optional[str] = None) -> HTTPException:
    """Handle generic exceptions."""

    # Log the exception
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"exception_type": type(exc).__name__, "request_id": request_id},
        exc_info=True,
    )

    error_response = ErrorResponse(
        error="Internal server error",
        error_code="INTERNAL_SERVER_ERROR",
        details={"exception_type": type(exc).__name__},
        request_id=request_id,
    )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_response.to_dict(),
    )


# Retry utilities
class RetryConfig:
    """Configuration for retry operations."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def retry_on_exception(exceptions: tuple, config: Optional[RetryConfig] = None, operation_name: str = "operation"):
    """Decorator to retry operations on specific exceptions."""

    if config is None:
        config = RetryConfig()

    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Operation {operation_name} failed after " f"{config.max_attempts} attempts",
                            extra={
                                "operation": operation_name,
                                "attempts": config.max_attempts,
                                "last_error": str(e),
                            },
                        )
                        raise e

                    # Calculate delay
                    delay = min(
                        config.base_delay * (config.exponential_base**attempt),
                        config.max_delay,
                    )

                    if config.jitter:
                        import secrets

                        delay *= 0.5 + secrets.randbelow(100) / 100.0

                    logger.warning(
                        f"Operation {operation_name} failed, retrying in {delay:.2f}s",
                        extra={
                            "operation": operation_name,
                            "attempt": attempt + 1,
                            "delay": delay,
                            "error": str(e),
                        },
                    )

                    import asyncio

                    await asyncio.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# Circuit breaker pattern
class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise ExternalServiceError(
                    service="circuit_breaker",
                    operation="call",
                    reason="Circuit breaker is OPEN",
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if not self.last_failure_time:
            return False
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                "Circuit breaker opened",
                extra={
                    "failure_count": self.failure_count,
                    "threshold": self.failure_threshold,
                },
            )
