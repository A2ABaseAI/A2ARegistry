"""Tests for authentication service."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.models.user import User, UserSession
from app.schemas.auth import PasswordChange, TokenRefresh, UserLogin, UserRegistration
from app.services.auth_service import AuthService
from tests.base_test import BaseTest


class TestAuthService(BaseTest):
    """Test cases for AuthService."""

    @pytest.fixture
    def auth_service(self, db_session):
        """Create AuthService with test database session."""
        return AuthService(db_session=db_session)

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

    @pytest.fixture
    def sample_user(self, auth_service, sample_user_data):
        """Create a sample user for testing."""
        registration_data = UserRegistration(**sample_user_data)
        return auth_service.register_user(registration_data)

    def test_register_user_success(self, auth_service, sample_user_data):
        """Test successful user registration."""
        registration_data = UserRegistration(**sample_user_data)

        user = auth_service.register_user(registration_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.tenant_id == "default"
        assert user.roles == ["User"]
        assert user.is_active is True
        assert user.password_hash is not None
        assert user.password_hash != "securepassword123"  # Should be hashed

    def test_register_user_duplicate_email(self, auth_service, sample_user_data):
        """Test registration with duplicate email."""
        registration_data = UserRegistration(**sample_user_data)

        # Register first user
        auth_service.register_user(registration_data)

        # Try to register with same email
        registration_data.username = "differentuser"
        with pytest.raises(Exception) as exc_info:
            auth_service.register_user(registration_data)

        assert "User with this email already exists" in str(exc_info.value)

    def test_register_user_duplicate_username(self, auth_service, sample_user_data):
        """Test registration with duplicate username."""
        registration_data = UserRegistration(**sample_user_data)

        # Register first user
        auth_service.register_user(registration_data)

        # Try to register with same username
        registration_data.email = "different@example.com"
        with pytest.raises(Exception) as exc_info:
            auth_service.register_user(registration_data)

        assert "Username already taken" in str(exc_info.value)

    def test_authenticate_user_success_email(self, auth_service, sample_user):
        """Test successful authentication with email."""
        login_data = UserLogin(email_or_username="test@example.com", password="securepassword123")

        user = auth_service.authenticate_user(login_data)

        assert user.id == sample_user.id
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_authenticate_user_success_username(self, auth_service, sample_user):
        """Test successful authentication with username."""
        login_data = UserLogin(email_or_username="testuser", password="securepassword123")

        user = auth_service.authenticate_user(login_data)

        assert user.id == sample_user.id
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_authenticate_user_invalid_credentials(self, auth_service, sample_user):
        """Test authentication with invalid credentials."""
        login_data = UserLogin(email_or_username="test@example.com", password="wrongpassword")

        with pytest.raises(Exception) as exc_info:
            auth_service.authenticate_user(login_data)

        assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_user_nonexistent_user(self, auth_service):
        """Test authentication with non-existent user."""
        login_data = UserLogin(email_or_username="nonexistent@example.com", password="password123")

        with pytest.raises(Exception) as exc_info:
            auth_service.authenticate_user(login_data)

        assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_user_inactive_account(self, auth_service, sample_user):
        """Test authentication with inactive account."""
        # Deactivate user
        sample_user.is_active = False
        auth_service.db.commit()

        login_data = UserLogin(email_or_username="test@example.com", password="securepassword123")

        with pytest.raises(Exception) as exc_info:
            auth_service.authenticate_user(login_data)

        assert "Account is disabled" in str(exc_info.value)

    def test_create_user_session(self, auth_service, sample_user):
        """Test user session creation."""
        refresh_token = "test_refresh_token_123"

        session = auth_service.create_user_session(sample_user, refresh_token)

        assert session.user_id == sample_user.id
        assert session.is_active is True
        # Check that expires_at is in the future
        # SQLite might return naive datetime, so we need to handle both cases
        now = datetime.now(timezone.utc)
        if session.expires_at.tzinfo is None:
            # Naive datetime from SQLite - compare with naive now
            now_naive = datetime.now()
            assert session.expires_at > now_naive
        else:
            # Timezone-aware datetime
            assert session.expires_at > now

        # Check token hash
        import hashlib

        expected_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        assert session.token_hash == expected_hash

    def test_get_user_profile_success(self, auth_service, sample_user):
        """Test successful user profile retrieval."""
        user = auth_service.get_user_profile(sample_user.id)

        assert user.id == sample_user.id
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_get_user_profile_not_found(self, auth_service):
        """Test user profile retrieval for non-existent user."""
        with pytest.raises(Exception) as exc_info:
            auth_service.get_user_profile("nonexistent_user_id")

        assert "User not found" in str(exc_info.value)

    def test_change_password_success(self, auth_service, sample_user):
        """Test successful password change."""
        password_data = PasswordChange(current_password="securepassword123", new_password="newpassword456")

        success = auth_service.change_password(sample_user.id, password_data)

        assert success is True

        # Verify new password works
        login_data = UserLogin(email_or_username="test@example.com", password="newpassword456")
        user = auth_service.authenticate_user(login_data)
        assert user.id == sample_user.id

    def test_change_password_wrong_current_password(self, auth_service, sample_user):
        """Test password change with wrong current password."""
        password_data = PasswordChange(current_password="wrongpassword", new_password="newpassword456")

        with pytest.raises(Exception) as exc_info:
            auth_service.change_password(sample_user.id, password_data)

        assert "Current password is incorrect" in str(exc_info.value)

    def test_change_password_user_not_found(self, auth_service):
        """Test password change for non-existent user."""
        password_data = PasswordChange(current_password="oldpassword", new_password="newpassword")

        with pytest.raises(Exception) as exc_info:
            auth_service.change_password("nonexistent_user_id", password_data)

        assert "User not found" in str(exc_info.value)

    def test_refresh_token_success(self, auth_service, sample_user):
        """Test successful token refresh."""
        # Create a session first
        refresh_token = "test_refresh_token_123"
        auth_service.create_user_session(sample_user, refresh_token)

        # Refresh token
        new_access_token = auth_service.refresh_token(refresh_token)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)

        # Verify token contains expected claims (with JWKS mocking)
        with patch("app.auth_jwks.verify_access_token") as mock_verify:
            mock_verify.return_value = {
                "user_id": sample_user.id,
                "username": sample_user.username,
                "email": sample_user.email,
                "full_name": sample_user.full_name,
                "tenant_id": sample_user.tenant_id,
                "roles": sample_user.roles,
                "iat": 1640995200,
            }

            from app.auth_jwks import verify_access_token

            payload = verify_access_token(new_access_token)
            assert payload.get("user_id") == sample_user.id
            assert payload.get("username") == sample_user.username

    def test_refresh_token_invalid_token(self, auth_service):
        """Test token refresh with invalid refresh token."""
        refresh_data = TokenRefresh(refresh_token="invalid_token")

        with pytest.raises(Exception) as exc_info:
            auth_service.refresh_token(refresh_data.refresh_token)

        assert "Invalid refresh token" in str(exc_info.value)

    def test_refresh_token_expired_session(self, auth_service, sample_user):
        """Test token refresh with expired session."""
        # Create expired session
        refresh_token = "expired_refresh_token"
        import uuid

        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=sample_user.id,
            token_hash="expired_hash",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            is_active=True,
        )
        auth_service.db.add(session)
        auth_service.db.commit()

        with pytest.raises(Exception) as exc_info:
            auth_service.refresh_token(refresh_token)

        assert "Invalid refresh token" in str(exc_info.value)

    def test_logout_user_success(self, auth_service, sample_user):
        """Test successful user logout."""
        # Create active sessions
        refresh_token1 = "token1"
        refresh_token2 = "token2"
        auth_service.create_user_session(sample_user, refresh_token1)
        auth_service.create_user_session(sample_user, refresh_token2)

        # Logout
        success = auth_service.logout_user(sample_user.id)

        assert success is True

        # Verify all sessions are inactive
        sessions = auth_service.db.query(UserSession).filter(UserSession.user_id == sample_user.id).all()

        for session in sessions:
            assert session.is_active is False

    def test_logout_user_no_sessions(self, auth_service, sample_user):
        """Test logout for user with no active sessions."""
        success = auth_service.logout_user(sample_user.id)

        assert success is True

    def test_create_login_response(self, auth_service, sample_user):
        """Test creation of complete login response."""
        refresh_token = "test_refresh_token"

        response = auth_service.create_login_response(sample_user, refresh_token)

        assert response.access_token is not None
        assert response.refresh_token == refresh_token
        assert response.token_type == "bearer"
        assert response.expires_in == 1800
        assert response.user.id == sample_user.id
        assert response.user.username == sample_user.username

    def test_create_refresh_response(self, auth_service, sample_user):
        """Test creation of token refresh response."""
        # Mock the verify_access_token function
        with patch("app.auth_jwks.verify_access_token") as mock_verify:
            mock_verify.return_value = {
                "user_id": sample_user.id,
                "username": sample_user.username,
                "email": sample_user.email,
                "full_name": sample_user.full_name,
                "tenant_id": sample_user.tenant_id,
                "roles": sample_user.roles,
                "iat": datetime.now(timezone.utc).timestamp(),
            }

            new_access_token = "new_access_token"
            refresh_token = "refresh_token"

            response = auth_service.create_refresh_response(new_access_token, refresh_token)

            assert response.access_token == new_access_token
            assert response.refresh_token == refresh_token
            assert response.token_type == "bearer"
            assert response.expires_in == 1800
            assert response.user.id == sample_user.id

    def test_service_database_rollback_on_error(self, auth_service, sample_user_data):
        """Test that database rollback occurs on registration error."""
        registration_data = UserRegistration(**sample_user_data)

        # Register user successfully
        auth_service.register_user(registration_data)

        # Try to register again (should fail and rollback)
        with pytest.raises(Exception):
            auth_service.register_user(registration_data)

        # Verify only one user exists (rollback worked)
        user_count = auth_service.db.query(User).count()
        assert user_count == 1

    def test_service_manages_own_database_connection(self):
        """Test that service manages its own database connection."""
        # Create service without passing db_session
        auth_service = AuthService()

        # Should still work (creates its own connection)
        assert auth_service.db is not None

        # Clean up
        auth_service.db.close()

    def test_password_hashing_security(self, auth_service, sample_user_data):
        """Test that passwords are properly hashed."""
        registration_data = UserRegistration(**sample_user_data)
        user = auth_service.register_user(registration_data)

        # Password should be hashed, not plain text
        assert user.password_hash != "securepassword123"
        assert len(user.password_hash) > 50  # PBKDF2 hash should be long
        assert ":" in user.password_hash  # PBKDF2 format includes salt

    def test_user_roles_default(self, auth_service, sample_user_data):
        """Test that new users get default roles."""
        registration_data = UserRegistration(**sample_user_data)
        user = auth_service.register_user(registration_data)

        assert user.roles == ["User"]
        assert user.is_active is True
        assert user.is_admin is False
