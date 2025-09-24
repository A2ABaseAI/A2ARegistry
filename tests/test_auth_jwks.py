"""Tests for consolidated security utilities."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.security import extract_context, require_oauth

from .base_test import BaseTest


class TestAuthJWKS(BaseTest):
    """Tests for JWT authentication and authorization."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch):
        """Create a test client with mocked dependencies."""

        def get_test_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = get_test_db

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()

    def test_extract_context_complete_payload(self):
        """Test context extraction with complete payload."""
        payload = {
            "sub": "test-client",
            "client_id": "test-client",
            "tenant": "default",
            "roles": ["Administrator", "User"],
        }

        context = extract_context(payload)
        assert context["client_id"] == "test-client"
        assert context["tenant"] == "default"
        assert context["roles"] == ["Administrator", "User"]

    def test_extract_context_minimal_payload(self):
        """Test context extraction with minimal payload."""
        payload = {"sub": "test-client"}

        context = extract_context(payload)
        assert context["client_id"] == "test-client"
        assert context["tenant"] is None
        assert context["roles"] == []

    def test_extract_context_missing_fields(self):
        """Test context extraction with missing fields."""
        payload = {"sub": "test-client"}

        context = extract_context(payload)
        assert context["client_id"] == "test-client"  # Uses sub as fallback
        assert context["tenant"] is None  # No tenant claim
        assert context["roles"] == []

    def test_extract_context_custom_claims(self):
        """Test context extraction with custom claim names."""
        payload = {
            "sub": "test-client",
            "custom_client_id": "custom-client",
            "custom_tenant": "custom-tenant",
            "custom_roles": ["CustomRole"],
        }

        # This would require custom claim configuration
        # For now, test with default claims
        context = extract_context(payload)
        assert context["client_id"] == "test-client"
        assert context["tenant"] is None
        assert context["roles"] == []

    def test_require_roles_success(self):
        """Test require_roles with valid roles."""
        from app.security import require_roles

        # Mock payload with Administrator role
        mock_payload = {
            "sub": "test-client",
            "client_id": "test-client",
            "tenant": "default",
            "roles": ["Administrator"],
        }

        # Create the dependency function
        role_dep = require_roles("Administrator")

        # Mock the require_oauth dependency to return our mock payload
        with patch("app.security.require_oauth", return_value=mock_payload):
            # Call the dependency function
            result = role_dep(mock_payload)

            # Verify the result contains the expected context
            assert result["client_id"] == "test-client"
            assert result["tenant"] == "default"
            assert result["roles"] == ["Administrator"]

        # Test with multiple roles - user has one of the required roles
        role_dep_multi = require_roles("Administrator", "CatalogManager")
        with patch("app.security.require_oauth", return_value=mock_payload):
            result = role_dep_multi(mock_payload)
            assert result["roles"] == ["Administrator"]

        # Test with CatalogManager role
        mock_payload_catalog = {
            "sub": "test-client",
            "client_id": "test-client",
            "tenant": "default",
            "roles": ["CatalogManager"],
        }

        with patch("app.security.require_oauth", return_value=mock_payload_catalog):
            result = role_dep_multi(mock_payload_catalog)
            assert result["roles"] == ["CatalogManager"]

    def test_require_roles_insufficient_permissions(self):
        """Test require_roles with insufficient permissions."""
        from fastapi import HTTPException

        from app.security import require_roles

        # Mock payload with insufficient role
        mock_payload = {
            "sub": "test-client",
            "client_id": "test-client",
            "tenant": "default",
            "roles": ["User"],  # Not Administrator
        }

        # Create the dependency function requiring Administrator role
        role_dep = require_roles("Administrator")

        # Mock the require_oauth dependency to return our mock payload
        with patch("app.security.require_oauth", return_value=mock_payload):
            # This should raise HTTPException with 403 status
            with pytest.raises(HTTPException) as exc_info:
                role_dep(mock_payload)

            # Verify the exception details
            assert exc_info.value.status_code == 403
            assert "Insufficient permissions" in str(exc_info.value.detail)

        # Test with empty roles
        mock_payload_no_roles = {"sub": "test-client", "client_id": "test-client", "tenant": "default", "roles": []}

        with patch("app.security.require_oauth", return_value=mock_payload_no_roles):
            with pytest.raises(HTTPException) as exc_info:
                role_dep(mock_payload_no_roles)

            assert exc_info.value.status_code == 403

        # Test with None roles
        mock_payload_none_roles = {"sub": "test-client", "client_id": "test-client", "tenant": "default", "roles": None}

        with patch("app.security.require_oauth", return_value=mock_payload_none_roles):
            with pytest.raises(HTTPException) as exc_info:
                role_dep(mock_payload_none_roles)

            assert exc_info.value.status_code == 403

    def test_authentication_required_endpoint(self, client):
        """Test that authentication is required for protected endpoints."""
        # Test without authentication
        response = client.get("/agents/entitled")
        assert response.status_code == 401

    def test_authentication_success(self, client, db_session):
        """Test successful authentication."""

        def mock_require_oauth():
            return {"sub": "test-client", "client_id": "test-client", "tenant": "default", "roles": ["Administrator"]}

        # Override the auth dependency
        app.dependency_overrides[require_oauth] = mock_require_oauth

        try:
            response = client.get("/agents/entitled")
            assert response.status_code == 200
        finally:
            # Cleanup
            app.dependency_overrides.clear()

    def test_role_based_access_control(self, client, db_session, mock_services_db):
        """Test role-based access control."""

        def mock_require_oauth():
            return {"sub": "test-client", "client_id": "test-client", "tenant": "default", "roles": ["Administrator"]}

        app.dependency_overrides[require_oauth] = mock_require_oauth

        try:
            # Test publish endpoint (requires Administrator or CatalogManager)
            valid_data = self.get_valid_publish_data()
            response = client.post("/agents/publish", json=valid_data)
            assert response.status_code == 201
        finally:
            app.dependency_overrides.clear()

    def test_tenant_isolation(self, client, db_session, mock_services_db):
        """Test that authentication works with different tenants."""

        def mock_require_oauth():
            return {"sub": "test-client", "client_id": "test-client", "tenant": "tenant-1", "roles": ["Administrator"]}

        app.dependency_overrides[require_oauth] = mock_require_oauth

        try:
            # Create agents in default tenant (since public endpoint uses default)
            self.create_test_agent_record(db_session, "agent-1", tenant_id="default")
            self.create_test_agent_version(db_session, "agent-1", public=True)

            response = client.get("/agents/public")
            assert response.status_code == 200

            data = response.json()
            # Should see the public agent from default tenant
            assert len(data["items"]) == 1
            assert data["items"][0]["id"] == "agent-1"
        finally:
            app.dependency_overrides.clear()

    def test_client_id_extraction(self):
        """Test various ways client_id can be extracted."""
        # Test with client_id claim
        payload1 = {"client_id": "client-1"}
        context1 = extract_context(payload1)
        assert context1["client_id"] == "client-1"

        # Test with sub fallback
        payload2 = {"sub": "client-2"}
        context2 = extract_context(payload2)
        assert context2["client_id"] == "client-2"

        # Test with both (client_id should take precedence)
        payload3 = {"client_id": "client-3", "sub": "client-3-sub"}
        context3 = extract_context(payload3)
        assert context3["client_id"] == "client-3"

    def test_roles_extraction(self):
        """Test roles extraction from various payload formats."""
        # Test with list of roles
        payload1 = {"roles": ["Admin", "User"]}
        context1 = extract_context(payload1)
        assert context1["roles"] == ["Admin", "User"]

        # Test with single role
        payload2 = {"roles": ["Admin"]}
        context2 = extract_context(payload2)
        assert context2["roles"] == ["Admin"]

        # Test with empty roles
        payload3 = {"roles": []}
        context3 = extract_context(payload3)
        assert context3["roles"] == []

        # Test with missing roles
        payload4 = {}
        context4 = extract_context(payload4)
        assert context4["roles"] == []

    def test_tenant_extraction(self):
        """Test tenant extraction from payload."""
        # Test with tenant
        payload1 = {"tenant": "tenant-1"}
        context1 = extract_context(payload1)
        assert context1["tenant"] == "tenant-1"

        # Test without tenant
        payload2 = {}
        context2 = extract_context(payload2)
        assert context2["tenant"] is None

    def test_context_structure(self):
        """Test that extracted context has correct structure."""
        payload = {"sub": "test-client", "client_id": "test-client", "tenant": "default", "roles": ["Administrator"]}

        context = extract_context(payload)

        # Check structure
        assert isinstance(context, dict)
        assert "client_id" in context
        assert "tenant" in context
        assert "roles" in context

        # Check types
        assert isinstance(context["client_id"], str)
        assert isinstance(context["roles"], list)
        # tenant can be None or str
        assert context["tenant"] is None or isinstance(context["tenant"], str)
