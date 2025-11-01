"""Tests for security utilities."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from registry.security import (
    create_access_token,
    extract_context,
    hash_password,
    require_oauth,
    require_roles,
    verify_access_token,
    verify_password,
)


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Should not be the same as original
        assert hashed != password

        # Should be a string
        assert isinstance(hashed, str)

        # Should contain salt and hash separated by colon
        assert ":" in hashed

        # Should be reasonably long (PBKDF2 with salt)
        assert len(hashed) > 50

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_different_hashes(self):
        """Test that same password produces different hashes."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (due to random salt)
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_password_edge_cases(self):
        """Test password hashing with edge cases."""
        # Empty password
        empty_hash = hash_password("")
        assert verify_password("", empty_hash) is True

        # Very long password
        long_password = "a" * 1000
        long_hash = hash_password(long_password)
        assert verify_password(long_password, long_hash) is True

        # Special characters
        special_password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_hash = hash_password(special_password)
        assert verify_password(special_password, special_hash) is True

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash format."""
        password = "testpassword123"

        # Invalid hash format
        assert verify_password(password, "invalid_hash") is False
        assert verify_password(password, "no_colon") is False
        assert verify_password(password, "too:many:colons") is False


class TestJWTTokenSecurity:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test access token creation."""
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=["User", "Admin"],
            tenant_id="default",
        )

        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are typically long

        # Should contain dots (JWT format)
        assert token.count(".") == 2

    def test_verify_access_token_success(self):
        """Test successful token verification."""
        token = create_access_token(user_id="user123", username="testuser", email="test@example.com", roles=["User"], tenant_id="default")

        payload = verify_access_token(token)

        assert payload["user_id"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert payload["roles"] == ["User"]
        assert payload["tenant"] == "default"
        assert payload["client_id"] == "user123"
        assert "iat" in payload
        assert "exp" in payload

    def test_verify_access_token_expired(self):
        """Test token verification with expired token."""
        # Create token with very short expiration
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=["User"],
            tenant_id="default",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_access_token(token)

        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()

    def test_verify_access_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_tokens = [
            "invalid.token.here",
            "not.a.jwt.token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
            "",
            "not-a-token",
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(HTTPException) as exc_info:
                verify_access_token(invalid_token)

            assert exc_info.value.status_code == 401

    def test_create_token_with_custom_expiration(self):
        """Test token creation with custom expiration."""
        expires_delta = timedelta(hours=2)
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=["User"],
            tenant_id="default",
            expires_delta=expires_delta,
        )

        payload = verify_access_token(token)

        # Check that expiration is approximately 2 hours from now
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]
        token_lifetime = exp_timestamp - iat_timestamp

        # Should be approximately 2 hours (7200 seconds)
        assert abs(token_lifetime - 7200) < 60  # Allow 1 minute tolerance

    def test_token_claims_structure(self):
        """Test that token contains all required claims."""
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=["User", "Admin"],
            tenant_id="test_tenant",
        )

        payload = verify_access_token(token)

        # Standard JWT claims
        assert "iss" in payload
        assert "aud" in payload
        assert "sub" in payload
        assert "iat" in payload
        assert "exp" in payload
        assert "nbf" in payload

        # A2A Registry specific claims
        assert "user_id" in payload
        assert "username" in payload
        assert "email" in payload
        assert "client_id" in payload
        assert "roles" in payload
        assert "tenant" in payload


class TestAuthenticationDependencies:
    """Test authentication dependencies and utilities."""

    def test_extract_context(self):
        """Test context extraction from JWT payload."""
        payload = {
            "user_id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["User", "Admin"],
            "tenant": "default",
            "client_id": "user123",
        }

        context = extract_context(payload)

        assert context["roles"] == ["User", "Admin"]
        assert context["tenant"] == "default"
        assert context["client_id"] == "user123"

    def test_extract_context_missing_fields(self):
        """Test context extraction with missing fields."""
        payload = {
            "user_id": "user123",
            "username": "testuser",
            # Missing roles, tenant, client_id
        }

        context = extract_context(payload)

        assert context["roles"] == []
        assert context["tenant"] is None
        assert context["client_id"] == "user123"  # Falls back to user_id

    def test_extract_context_alternative_client_id(self):
        """Test context extraction with alternative client_id fields."""
        payload = {"sub": "user123", "client_id": "client456", "roles": ["User"], "tenant": "default"}

        context = extract_context(payload)

        assert context["client_id"] == "client456"
        assert context["roles"] == ["User"]
        assert context["tenant"] == "default"

    def test_require_roles_success(self):
        """Test require_roles with valid roles."""
        # Mock the require_oauth dependency
        mock_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["Admin", "User"],
            "tenant": "default",
            "client_id": "user123",
        }

        # Create the dependency function
        role_dep = require_roles("Admin")

        # Mock the require_oauth dependency
        with patch("registry.security.require_oauth", return_value=mock_payload):
            result = role_dep(mock_payload)

            assert result["roles"] == ["Admin", "User"]
            assert result["tenant"] == "default"
            assert result["client_id"] == "user123"

    def test_require_roles_insufficient_permissions(self):
        """Test require_roles with insufficient permissions."""
        mock_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["User"],  # Only User role, not Admin
            "tenant": "default",
            "client_id": "user123",
        }

        role_dep = require_roles("Admin")

        with patch("registry.security.require_oauth", return_value=mock_payload):
            with pytest.raises(HTTPException) as exc_info:
                role_dep(mock_payload)

            assert exc_info.value.status_code == 403
            assert "Insufficient permissions" in str(exc_info.value.detail)

    def test_require_roles_multiple_roles(self):
        """Test require_roles with multiple required roles."""
        mock_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["User"],  # Has User role
            "tenant": "default",
            "client_id": "user123",
        }

        # Require either Admin OR User
        role_dep = require_roles("Admin", "User")

        with patch("registry.security.require_oauth", return_value=mock_payload):
            result = role_dep(mock_payload)

            assert result["roles"] == ["User"]

    def test_require_roles_no_roles(self):
        """Test require_roles with user having no roles."""
        mock_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": [],  # No roles
            "tenant": "default",
            "client_id": "user123",
        }

        role_dep = require_roles("Admin")

        with patch("registry.security.require_oauth", return_value=mock_payload):
            with pytest.raises(HTTPException) as exc_info:
                role_dep(mock_payload)

            assert exc_info.value.status_code == 403

    def test_require_oauth_missing_token(self):
        """Test require_oauth with missing token."""
        with pytest.raises(HTTPException) as exc_info:
            require_oauth(None)

        assert exc_info.value.status_code == 401
        assert "Missing bearer token" in str(exc_info.value.detail)

    def test_require_oauth_invalid_token(self):
        """Test require_oauth with invalid token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        with pytest.raises(HTTPException) as exc_info:
            require_oauth(mock_credentials)

        assert exc_info.value.status_code == 401


class TestSecurityEdgeCases:
    """Test security utilities with edge cases."""

    def test_password_with_unicode(self):
        """Test password hashing with unicode characters."""
        unicode_password = "密码123🔐"
        hashed = hash_password(unicode_password)

        assert verify_password(unicode_password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_token_with_special_characters(self):
        """Test token creation with special characters in user data."""
        token = create_access_token(
            user_id="user-123_test",
            username="test@user#name",
            email="test+tag@example.com",
            roles=["User/Role", "Admin-Role"],
            tenant_id="tenant_123",
        )

        payload = verify_access_token(token)

        assert payload["user_id"] == "user-123_test"
        assert payload["username"] == "test@user#name"
        assert payload["email"] == "test+tag@example.com"
        assert payload["roles"] == ["User/Role", "Admin-Role"]
        assert payload["tenant"] == "tenant_123"

    def test_empty_roles_list(self):
        """Test token creation and verification with empty roles."""
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=[],  # Empty roles
            tenant_id="default",
        )

        payload = verify_access_token(token)

        assert payload["roles"] == []

    def test_none_values_in_token(self):
        """Test token creation with None values."""
        token = create_access_token(
            user_id="user123",
            username="testuser",
            email="test@example.com",
            roles=["User"],
            tenant_id=None,  # None tenant
        )

        payload = verify_access_token(token)

        assert payload["tenant"] is None

    def test_very_long_strings(self):
        """Test with very long strings."""
        long_string = "a" * 1000

        token = create_access_token(
            user_id=long_string,
            username=long_string,
            email=f"{long_string}@example.com",
            roles=[long_string],
            tenant_id=long_string,
        )

        payload = verify_access_token(token)

        assert payload["user_id"] == long_string
        assert payload["username"] == long_string
        assert payload["roles"] == [long_string]
        assert payload["tenant"] == long_string
