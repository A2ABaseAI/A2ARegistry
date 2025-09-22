"""Authentication service for user management and token operations."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..core.security import create_access_token, verify_password, hash_password
from ..models.user import User, UserSession
from ..schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    UserProfile,
    PasswordChange,
    TokenRefresh
)
from ..database import get_db, SessionLocal


def _get_db_session():
    """Get a database session. Can be overridden in tests."""
    return SessionLocal()


logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db_session=None):
        """Initialize with database session."""
        if db_session is not None:
            self.db = db_session
        else:
            # Create a new session using the factory function
            self.db = _get_db_session()
    
    def register_user(self, registration_data: UserRegistration) -> User:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = (
                self.db.query(User)
                .filter(User.email == registration_data.email)
                .first()
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            
            # Check if username already exists
            existing_username = (
                self.db.query(User)
                .filter(User.username == registration_data.username)
                .first()
            )
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken"
                )
            
            # Create new user
            hashed_password = hash_password(registration_data.password)
            import uuid
            user = User(
                id=str(uuid.uuid4()),
                username=registration_data.username,
                email=registration_data.email,
                password_hash=hashed_password,
                full_name=registration_data.full_name,
                tenant_id=registration_data.tenant_id or "default",
                is_active=True,
                roles=["User"]  # Default role
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User registered successfully: {user.username}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    def authenticate_user(self, login_data: UserLogin) -> User:
        """Authenticate user and return user object."""
        try:
            # Find user by email or username
            user = (
                self.db.query(User)
                .filter(
                    (User.email == login_data.email_or_username) |
                    (User.username == login_data.email_or_username)
                )
                .first()
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )
            
            if not verify_password(login_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            logger.info(f"User authenticated successfully: {user.username}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    def create_user_session(self, user: User, token: str) -> UserSession:
        """Create a user session."""
        try:
            # Create session
            import uuid
            session = UserSession(
                id=str(uuid.uuid4()),
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                is_active=True
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.debug(f"User session created: {user.username}")
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Session creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session creation failed"
            )
    
    def get_user_profile(self, user_id: str) -> User:
        """Get user profile."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user profile"
            )
    
    def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """Change user password."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            if not verify_password(password_data.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Update password
            user.password_hash = hash_password(password_data.new_password)
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Password changed for user: {user.username}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Password change failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    
    def refresh_token(self, refresh_token: str) -> str:
        """Refresh access token."""
        try:
            # Find session by refresh token
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            session = (
                self.db.query(UserSession)
                .filter(
                    UserSession.token_hash == token_hash,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.now(timezone.utc)
                )
                .first()
            )
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Get user
            user = self.db.query(User).filter(User.id == session.user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new access token
            new_token = create_access_token(
                user_id=user.id,
                username=user.username,
                email=user.email,
                roles=user.roles,
                tenant_id=user.tenant_id
            )
            
            logger.info(f"Token refreshed for user: {user.username}")
            return new_token
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )
    
    def logout_user(self, user_id: str) -> bool:
        """Logout user and invalidate all sessions."""
        try:
            # Invalidate all sessions for the user
            sessions = (
                self.db.query(UserSession)
                .filter(UserSession.user_id == user_id, UserSession.is_active == True)
                .all()
            )
            
            for session in sessions:
                session.is_active = False
                session.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"User logged out: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Logout failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
    
    def create_login_response(self, user: User, refresh_token: str) -> TokenResponse:
        """Create a complete login response with tokens and user info."""
        try:
            # Create access token
            access_token = create_access_token(
                user_id=user.id,
                username=user.username,
                email=user.email,
                roles=user.roles,
                tenant_id=user.tenant_id
            )
            
            # Create session
            self.create_user_session(user, refresh_token)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=1800,  # 30 minutes
                user=UserProfile(
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
            )
            
        except Exception as e:
            logger.error(f"Failed to create login response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login response creation failed"
            )
    
    def create_refresh_response(self, new_access_token: str, refresh_token: str) -> TokenResponse:
        """Create a token refresh response."""
        try:
            from ..auth_jwks import verify_access_token
            payload = verify_access_token(new_access_token)
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token,  # Keep same refresh token
                token_type="bearer",
                expires_in=1800,  # 30 minutes
                user=UserProfile(
                    id=payload.get("user_id"),
                    username=payload.get("username"),
                    email=payload.get("email"),
                    full_name=payload.get("full_name"),
                    tenant_id=payload.get("tenant_id"),
                    roles=payload.get("roles", []),
                    is_active=True,
                    created_at=payload.get("iat"),
                    updated_at=payload.get("iat")
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to create refresh response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Refresh response creation failed"
            )
