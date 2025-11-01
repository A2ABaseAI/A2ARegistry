"""Tests for a2a_reg_sdk.exceptions - SDK exception classes."""

import pytest

from a2a_reg_sdk.exceptions import (
    A2AError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


class TestExceptions:
    """Tests for SDK exception classes."""

    def test_a2a_error_base(self):
        """Test A2AError base exception."""
        error = A2AError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, A2AError)
        assert isinstance(error, Exception)

    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, A2AError)
        assert isinstance(error, Exception)

    def test_not_found_error(self):
        """Test NotFoundError exception."""
        error = NotFoundError("Resource not found")
        assert str(error) == "Resource not found"
        assert isinstance(error, A2AError)
        assert isinstance(error, Exception)

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, A2AError)
        assert isinstance(error, Exception)

    def test_server_error(self):
        """Test ServerError exception."""
        error = ServerError("Server error occurred")
        assert str(error) == "Server error occurred"
        assert isinstance(error, A2AError)
        assert isinstance(error, Exception)

    def test_exception_chaining(self):
        """Test exception chaining."""
        original_error = ValueError("Original error")
        try:
            raise original_error
        except ValueError:
            error = A2AError("Wrapped error")
            error.__cause__ = original_error
        assert str(error) == "Wrapped error"
        assert error.__cause__ == original_error

    def test_exception_with_details(self):
        """Test exception with additional details."""
        error = ValidationError("Validation failed")
        error.details = {"field": "name", "reason": "required"}
        assert error.details["field"] == "name"
        assert error.details["reason"] == "required"

