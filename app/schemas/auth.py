"""Authentication and user management schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegistration(BaseModel):
    """User registration schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    tenant_id: Optional[str] = Field("default", max_length=100, description="Tenant identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "tenant_id": "default",
            }
        }
    )


class UserLogin(BaseModel):
    """User login schema."""

    email_or_username: str = Field(..., description="Email address or username")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(json_schema_extra={"example": {"email_or_username": "john.doe@example.com", "password": "securepassword123"}})


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserProfile" = Field(..., description="User profile information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                "refresh_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "user-123",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "tenant_id": "default",
                    "roles": ["User"],
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            }
        }
    )


class UserProfile(BaseModel):
    """User profile schema."""

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    tenant_id: str = Field(..., description="Tenant identifier")
    roles: List[str] = Field(..., description="User roles")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "user-123",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "tenant_id": "default",
                "roles": ["User"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )


class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = ConfigDict(json_schema_extra={"example": {"current_password": "oldpassword123", "new_password": "newpassword456"}})


class TokenRefresh(BaseModel):
    """Token refresh schema."""

    refresh_token: str = Field(..., description="Refresh token")

    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"}})


class UserInvitation(BaseModel):
    """User invitation schema."""

    email: EmailStr = Field(..., description="Email address to invite")
    roles: List[str] = Field(["User"], description="Roles to assign to the user")
    tenant_id: str = Field("default", description="Tenant identifier")
    message: Optional[str] = Field(None, description="Invitation message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "roles": ["User"],
                "tenant_id": "default",
                "message": "Welcome to our A2A Registry!",
            }
        }
    )


class UserUpdate(BaseModel):
    """User profile update schema."""

    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    tenant_id: Optional[str] = Field(None, max_length=100, description="Tenant identifier")

    model_config = ConfigDict(json_schema_extra={"example": {"full_name": "John Smith", "tenant_id": "enterprise"}})


class UserRoleUpdate(BaseModel):
    """User role update schema (admin only)."""

    roles: List[str] = Field(..., description="New roles for the user")

    model_config = ConfigDict(json_schema_extra={"example": {"roles": ["User", "Publisher"]}})


class UserStatusUpdate(BaseModel):
    """User status update schema (admin only)."""

    is_active: bool = Field(..., description="Whether user is active")

    model_config = ConfigDict(json_schema_extra={"example": {"is_active": True}})


class PasswordReset(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="Email address for password reset")

    model_config = ConfigDict(json_schema_extra={"example": {"email": "john.doe@example.com"}})


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    model_config = ConfigDict(json_schema_extra={"example": {"token": "reset-token-123", "new_password": "newpassword456"}})
