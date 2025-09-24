"""Tests for authentication API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import AuthService
from tests.base_test import BaseTest


class TestAuthAPI(BaseTest):
    """Test cases for authentication API endpoints."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch, mock_services_db):
        """Create a test client with mocked dependencies."""
        # Mock the AuthService to use the test database session
        with patch("app.api.auth.AuthService") as mock_auth_service:

            def create_auth_service():
                service = AuthService(db_session=db_session)
                return service

            mock_auth_service.side_effect = create_auth_service

            with TestClient(app) as test_client:
                yield test_client

    @pytest.fixture
    def sample_user_data(self):
        """Sample user registration data."""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
            "tenant_id": "default",
        }

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration via API."""
        response = client.post("/auth/register", json=sample_user_data)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["tenant_id"] == "default"
        assert data["roles"] == ["User"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_register_user_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email via API."""
        # Register first user
        client.post("/auth/register", json=sample_user_data)

        # Try to register with same email
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"

        response = client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 409
        assert "User with this email already exists" in response.json()["error"]

    def test_register_user_duplicate_username(self, client, sample_user_data):
        """Test registration with duplicate username via API."""
        # Register first user
        client.post("/auth/register", json=sample_user_data)

        # Try to register with same username
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"

        response = client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 409
        assert "Username already taken" in response.json()["error"]

    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data."""
        invalid_data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid email
            "password": "123",  # Too short
        }

        response = client.post("/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "username": "testuser"
            # Missing email, password
        }

        response = client.post("/auth/register", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    def test_login_user_success_email(self, client, sample_user_data):
        """Test successful login with email via API."""
        # Register user first
        client.post("/auth/register", json=sample_user_data)

        # Login with email
        login_data = {"email_or_username": "test@example.com", "password": "securepassword123"}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"

    def test_login_user_success_username(self, client, sample_user_data):
        """Test successful login with username via API."""
        # Register user first
        client.post("/auth/register", json=sample_user_data)

        # Login with username
        login_data = {"email_or_username": "testuser", "password": "securepassword123"}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "testuser"

    def test_login_user_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials via API."""
        # Register user first
        client.post("/auth/register", json=sample_user_data)

        # Login with wrong password
        login_data = {"email_or_username": "test@example.com", "password": "wrongpassword"}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["error"]

    def test_login_user_nonexistent_user(self, client):
        """Test login with non-existent user via API."""
        login_data = {"email_or_username": "nonexistent@example.com", "password": "password123"}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["error"]

    def test_login_user_missing_fields(self, client):
        """Test login with missing fields."""
        incomplete_data = {
            "email_or_username": "test@example.com"
            # Missing password
        }

        response = client.post("/auth/login", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    def test_refresh_token_success(self, client, sample_user_data):
        """Test successful token refresh via API."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        refresh_token = login_response.json()["refresh_token"]

        # Mock the verify_access_token call to avoid external JWKS dependency
        with patch("app.security.jwt.verify_access_token") as mock_verify:
            mock_verify.return_value = {
                "user_id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "tenant": "default",
                "roles": ["User"],
                "iat": 1640995200,
            }

            # Refresh token
            refresh_data = {"refresh_token": refresh_token}
            response = client.post("/auth/refresh", json=refresh_data)

            assert response.status_code == 200
            data = response.json()

            assert "access_token" in data
            assert data["refresh_token"] == refresh_token
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 1800
            assert "user" in data

    def test_refresh_token_invalid_token(self, client):
        """Test token refresh with invalid token via API."""
        refresh_data = {"refresh_token": "invalid_token"}

        response = client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["error"]

    def test_refresh_token_missing_field(self, client):
        """Test token refresh with missing field."""
        incomplete_data = {}  # Missing refresh_token

        response = client.post("/auth/refresh", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    def test_get_current_user_success(self, client, sample_user_data):
        """Test successful get current user via API."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        access_token = login_response.json()["access_token"]

        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["tenant_id"] == "default"
        assert data["roles"] == ["User"]
        assert data["is_active"] is True

    def test_get_current_user_no_token(self, client):
        """Test get current user without token."""
        response = client.get("/auth/me")

        assert response.status_code == 401  # FastAPI returns 401 for missing auth

    def test_get_current_user_invalid_token(self, client):
        """Test get current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401
        assert "Invalid token" in response.json()["error"]

    def test_change_password_success(self, client, sample_user_data):
        """Test successful password change via API."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        access_token = login_response.json()["access_token"]

        # Change password
        password_data = {"current_password": "securepassword123", "new_password": "newpassword456"}

        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]

        # Verify new password works
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "newpassword456"}
        )

        assert login_response.status_code == 200

    def test_change_password_wrong_current_password(self, client, sample_user_data):
        """Test password change with wrong current password."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        access_token = login_response.json()["access_token"]

        # Change password with wrong current password
        password_data = {"current_password": "wrongpassword", "new_password": "newpassword456"}

        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["error"]

    def test_change_password_no_token(self, client):
        """Test password change without token."""
        password_data = {"current_password": "oldpassword", "new_password": "newpassword"}

        response = client.post("/auth/change-password", json=password_data)

        assert response.status_code == 401  # FastAPI returns 401 for missing auth

    def test_change_password_invalid_data(self, client, sample_user_data):
        """Test password change with invalid data."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        access_token = login_response.json()["access_token"]

        # Change password with invalid data
        password_data = {"current_password": "securepassword123", "new_password": "123"}  # Too short

        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 422  # Validation error

    def test_logout_user_success(self, client, sample_user_data):
        """Test successful user logout via API."""
        # Register and login user
        client.post("/auth/register", json=sample_user_data)
        login_response = client.post(
            "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
        )

        access_token = login_response.json()["access_token"]

        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/auth/logout", headers=headers)

        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]

    def test_logout_user_no_token(self, client):
        """Test logout without token."""
        response = client.post("/auth/logout")

        assert response.status_code == 401  # FastAPI returns 401 for missing auth

    def test_logout_user_invalid_token(self, client):
        """Test logout with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/auth/logout", headers=headers)

        assert response.status_code == 401
        assert "Invalid token" in response.json()["error"]

    def test_complete_auth_flow(self, client):
        """Test complete authentication flow."""
        # 1. Register user
        user_data = {
            "username": "flowtest",
            "email": "flow@example.com",
            "password": "password123",
            "full_name": "Flow Test User",
            "tenant_id": "test_tenant",
        }

        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Login user
        login_response = client.post(
            "/auth/login", json={"email_or_username": "flow@example.com", "password": "password123"}
        )
        assert login_response.status_code == 200

        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 3. Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "flowtest"

        # 4. Refresh token (with JWKS mocking)
        with patch("app.security.jwt.verify_access_token") as mock_verify:
            mock_verify.return_value = {
                "user_id": "test-user-id",
                "username": "flowtest",
                "email": "flow@example.com",
                "full_name": "Flow Test User",
                "tenant": "test_tenant",
                "roles": ["User"],
                "iat": 1640995200,
            }

            refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
            assert refresh_response.status_code == 200

            new_access_token = refresh_response.json()["access_token"]

        # 5. Use new token
        headers = {"Authorization": f"Bearer {new_access_token}"}
        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200

        # 6. Change password
        password_response = client.post(
            "/auth/change-password",
            json={"current_password": "password123", "new_password": "newpassword456"},
            headers=headers,
        )
        assert password_response.status_code == 200

        # 7. Login with new password
        new_login_response = client.post(
            "/auth/login", json={"email_or_username": "flow@example.com", "password": "newpassword456"}
        )
        assert new_login_response.status_code == 200

        # 8. Logout
        logout_response = client.post("/auth/logout", headers=headers)
        assert logout_response.status_code == 200

    def test_api_error_handling(self, client):
        """Test API error handling for various scenarios."""
        # Test with malformed JSON
        response = client.post("/auth/register", content="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422

        # Test with wrong content type
        response = client.post(
            "/auth/login",
            content="username=test&password=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 422

    def test_api_rate_limiting(self, client, sample_user_data):
        """Test that auth endpoints respect rate limiting."""
        # This test would require actual rate limiting to be enabled
        # For now, just verify endpoints are accessible
        response = client.post("/auth/register", json=sample_user_data)
        assert response.status_code in [200, 409]  # 409 if user already exists

        # Multiple rapid requests should not cause 429 (rate limit) in test environment
        # since Redis is mocked
        for _ in range(5):
            response = client.post(
                "/auth/login", json={"email_or_username": "test@example.com", "password": "securepassword123"}
            )
            # Should get 401 (invalid credentials) or 200 (if user exists)
            assert response.status_code in [200, 401]

    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        # Test CORS headers on a POST request (more realistic)
        response = client.post(
            "/auth/register",
            json={"username": "test", "email": "test@test.com", "password": "test123"},
            headers={"Origin": "http://localhost:3000"},
        )

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
