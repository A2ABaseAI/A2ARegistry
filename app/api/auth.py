"""Authentication endpoints for user registration, login, token management, and API key generation."""

import secrets
import hashlib
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Form
from ..core.logging import get_logger
from ..security import extract_context, require_oauth, require_roles
from ..schemas.auth import PasswordChange, TokenRefresh, TokenResponse, UserLogin, UserProfile, UserRegistration
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserProfile)
def register_user(registration_data: UserRegistration):
    """
    Register a new user account.

    Creates a new user account with the provided information.
    Returns the user profile upon successful registration.
    """
    try:
        auth_service = AuthService()
        user = auth_service.register_user(registration_data)

        return UserProfile(
            id=str(user.id),
            username=str(user.username),
            email=str(user.email),
            full_name=str(user.full_name) if user.full_name else None,
            tenant_id=str(user.tenant_id),
            roles=list(user.roles) if user.roles else [],
            is_active=bool(user.is_active),
            created_at=user.created_at,  # type: ignore[arg-type]
            updated_at=user.updated_at,  # type: ignore[arg-type]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin):
    """
    Authenticate user and return access token.

    Authenticates the user with email/username and password.
    Returns an access token and refresh token upon successful authentication.
    """
    try:
        auth_service = AuthService()
        user = auth_service.authenticate_user(login_data)

        # Create refresh token
        refresh_token = secrets.token_urlsafe(32)

        # Create complete login response
        return auth_service.create_login_response(user, refresh_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(refresh_data: TokenRefresh):
    """
    Refresh access token using refresh token.

    Generates a new access token using a valid refresh token.
    Returns a new access token and user information.
    """
    try:
        auth_service = AuthService()
        new_access_token = auth_service.refresh_token(refresh_data.refresh_token)

        # Create complete refresh response
        return auth_service.create_refresh_response(new_access_token, refresh_data.refresh_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token refresh failed")


@router.get("/me", response_model=UserProfile)
def get_current_user(current_user: dict = Depends(require_oauth)):
    """
    Get current user profile.

    Returns the profile information of the currently authenticated user.
    """
    try:
        context = extract_context(current_user)
        user_id = context.get("client_id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        auth_service = AuthService()
        user = auth_service.get_user_profile(user_id)

        return UserProfile(
            id=str(user.id),
            username=str(user.username),
            email=str(user.email),
            full_name=str(user.full_name) if user.full_name else None,
            tenant_id=str(user.tenant_id),
            roles=list(user.roles) if user.roles else [],
            is_active=bool(user.is_active),
            created_at=user.created_at,  # type: ignore[arg-type]
            updated_at=user.updated_at,  # type: ignore[arg-type]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user profile")


@router.post("/change-password")
def change_password(password_data: PasswordChange, current_user: dict = Depends(require_oauth)):
    """
    Change user password.

    Allows authenticated users to change their password.
    Requires the current password for verification.
    """
    try:
        context = extract_context(current_user)
        user_id = context.get("client_id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        auth_service = AuthService()
        success = auth_service.change_password(user_id, password_data)

        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password change failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password change failed")


@router.post("/logout")
def logout_user(current_user: dict = Depends(require_oauth)):
    """
    Logout user and invalidate session.

    Invalidates the current user session and refresh token.
    """
    try:
        context = extract_context(current_user)
        user_id = context.get("client_id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        auth_service = AuthService()
        success = auth_service.logout_user(user_id)

        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")


@router.post("/oauth/token")
def oauth_token(
    grant_type: str = Form("client_credentials"),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form("read write")
):
    """
    OAuth 2.0 Client Credentials flow endpoint.

    This endpoint allows clients to authenticate using client_id and client_secret
    and receive an access token for API access.
    """
    try:
        if grant_type != "client_credentials":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only client_credentials grant type is supported"
            )

        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id and client_secret are required"
            )

        # Production implementation: Validate client credentials against database
        from ..security import create_access_token, verify_password
        from ..database import SessionLocal
        from ..models.user import User

        db = SessionLocal()
        try:
            # Validate client credentials against registered users
            # In OAuth 2.0 Client Credentials flow, client_id is typically the username
            user = db.query(User).filter(User.username == client_id).first()

            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client credentials")

            # Verify client_secret against user's password hash
            # In OAuth 2.0 Client Credentials flow, client_secret is typically the user's password
            if not verify_password(client_secret, str(user.password_hash)):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client credentials")

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client account is inactive")

            # Validate requested scopes against user's roles
            scopes = scope.split() if scope else ["read"]
            user_roles: List[str] = list(user.roles) if user.roles else []

            logger.info(f"OAuth token request - User: {user.username}, Scopes: {scopes}, User Roles: {user_roles}")

            # Check if user has sufficient roles for requested scopes
            if ("write" in scopes
                    and "CatalogManager" not in user_roles
                    and "Administrator" not in user_roles):
                logger.warning(
                    f"User {user.username} with roles {user_roles} denied write scope"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for write scope"
                )

            if (("admin" in scopes or "all" in scopes)
                    and "Administrator" not in user_roles):
                logger.warning(f"User {user.username} with roles {user_roles} denied admin scope")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for admin scope"
                )

            # Create token with actual user data
            access_token = create_access_token(
                user_id=str(user.id),
                username=str(user.username),
                email=str(user.email),
                roles=user_roles,
                tenant_id=str(user.tenant_id) if user.tenant_id else "default"
            )

        finally:
            db.close()

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour
            "scope": scope
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth token generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token generation failed")


@router.post("/api-token")
def generate_api_token(ctx=Depends(require_roles("Administrator"))):
    """
    Generate a secure API token and return its SHA-256 hash.

    Admin-only. The plaintext token is returned once. Store only the hash in
    configuration under `API_KEY_HASHES` to enable Bearer API key access.
    """
    try:
        token = secrets.token_urlsafe(48)
        sha256 = hashlib.sha256(token.encode()).hexdigest()

        return {
            "token": token,
            "sha256": sha256,
            "instructions": (
                "Add the sha256 value to API_KEY_HASHES env setting. Do not store the plaintext token."
            ),
        }

    except Exception as e:
        logger.error(f"API token generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate API token")
