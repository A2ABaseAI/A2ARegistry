"""User and authentication models."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, String, Text

from .base import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # Basic user information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Tenant and organization
    tenant_id = Column(String(100), nullable=False, default="default", index=True)

    # Authorization
    roles = Column(JSON, nullable=False, default=["User"])
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Profile information
    profile_data = Column(Text, nullable=True)  # JSON string for additional profile data

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', tenant='{self.tenant_id}')>"

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "tenant_id": self.tenant_id,
            "roles": self.roles,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class UserSession(Base):
    """User session model for token management."""

    __tablename__ = "user_sessions"

    # Session information
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)

    # Session metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible

    # Session lifecycle
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', active={self.is_active})>"

    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
        }


class UserInvitation(Base):
    """User invitation model for inviting new users."""

    __tablename__ = "user_invitations"

    # Invitation information
    email = Column(String(255), nullable=False, index=True)
    invited_by = Column(String, nullable=False, index=True)
    tenant_id = Column(String(100), nullable=False, default="default", index=True)

    # Invitation details
    roles = Column(JSON, nullable=False, default=["User"])
    invitation_token = Column(String(255), nullable=False, unique=True, index=True)

    # Invitation lifecycle
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Invitation metadata
    message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<UserInvitation(email='{self.email}', tenant='{self.tenant_id}', active={self.is_active})>"

    def to_dict(self) -> dict:
        """Convert invitation to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "invited_by": self.invited_by,
            "tenant_id": self.tenant_id,
            "roles": self.roles,
            "invitation_token": self.invitation_token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "is_active": self.is_active,
            "message": self.message,
        }
