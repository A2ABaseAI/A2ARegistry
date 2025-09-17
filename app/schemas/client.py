"""Client-related Pydantic schemas."""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    """Schema for creating a new client."""

    name: str = Field(..., description="Client name")
    description: Optional[str] = Field(None, description="Client description")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    redirect_uris: List[str] = Field(
        default_factory=list, description="Allowed redirect URIs"
    )
    scopes: List[str] = Field(default_factory=list, description="Client scopes")


class ClientUpdate(BaseModel):
    """Schema for updating an existing client."""

    name: Optional[str] = Field(None, description="Updated client name")
    description: Optional[str] = Field(None, description="Updated description")
    contact_email: Optional[EmailStr] = Field(None, description="Updated contact email")
    redirect_uris: Optional[List[str]] = Field(
        None, description="Updated redirect URIs"
    )
    scopes: Optional[List[str]] = Field(None, description="Updated scopes")
    is_active: Optional[bool] = Field(None, description="Active status")


class ClientResponse(BaseModel):
    """Schema for client response."""

    id: str = Field(..., description="Client ID")
    name: str = Field(..., description="Client name")
    description: Optional[str] = Field(None, description="Client description")
    contact_email: Optional[str] = Field(None, description="Contact email")
    redirect_uris: List[str] = Field(..., description="Redirect URIs")
    scopes: List[str] = Field(..., description="Client scopes")
    is_active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class ClientEntitlementCreate(BaseModel):
    """Schema for creating client entitlements."""

    client_id: str = Field(..., description="Client ID")
    agent_id: str = Field(..., description="Agent ID")
    scopes: List[str] = Field(default_factory=list, description="Entitlement scopes")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")


class ClientEntitlementResponse(BaseModel):
    """Schema for client entitlement response."""

    id: str = Field(..., description="Entitlement ID")
    client_id: str = Field(..., description="Client ID")
    agent_id: str = Field(..., description="Agent ID")
    scopes: List[str] = Field(..., description="Entitlement scopes")
    is_active: bool = Field(..., description="Active status")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
