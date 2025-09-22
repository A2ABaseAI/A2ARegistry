"""Authentication endpoints for user registration, login, and token management."""

import secrets
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..core.logging import get_logger
from ..core.security import require_oauth
from ..services.auth_service import AuthService
from ..schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    UserProfile,
    PasswordChange,
    TokenRefresh
)

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
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            tenant_id=user.tenant_id,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserProfile)
def get_current_user(credentials: HTTPBearer = Depends(HTTPBearer())):
    """
    Get current user profile.
    
    Returns the profile information of the currently authenticated user.
    """
    try:
        current_user = require_oauth(credentials)
        from ..auth_jwks import extract_context
        context = extract_context(current_user)
        user_id = context.get("client_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        auth_service = AuthService()
        user = auth_service.get_user_profile(user_id)
        
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            tenant_id=user.tenant_id,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    credentials: HTTPBearer = Depends(HTTPBearer())
):
    """
    Change user password.
    
    Allows authenticated users to change their password.
    Requires the current password for verification.
    """
    try:
        current_user = require_oauth(credentials)
        from ..auth_jwks import extract_context
        context = extract_context(current_user)
        user_id = context.get("client_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        auth_service = AuthService()
        success = auth_service.change_password(user_id, password_data)
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/logout")
def logout_user(credentials: HTTPBearer = Depends(HTTPBearer())):
    """
    Logout user and invalidate session.
    
    Invalidates the current user session and refresh token.
    """
    try:
        current_user = require_oauth(credentials)
        from ..auth_jwks import extract_context
        context = extract_context(current_user)
        user_id = context.get("client_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        auth_service = AuthService()
        success = auth_service.logout_user(user_id)
        
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
