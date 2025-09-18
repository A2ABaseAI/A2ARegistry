"""
A2A SDK Exceptions

Custom exception classes for the A2A SDK.
"""


class A2AError(Exception):
    """Base exception for A2A SDK errors."""

    pass


class AuthenticationError(A2AError):
    """Raised when authentication fails."""

    pass


class ValidationError(A2AError):
    """Raised when data validation fails."""

    pass


class NotFoundError(A2AError):
    """Raised when a requested resource is not found."""

    pass


class RateLimitError(A2AError):
    """Raised when rate limits are exceeded."""

    pass


class ServerError(A2AError):
    """Raised when the server returns an error."""

    pass
