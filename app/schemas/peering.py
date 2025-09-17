"""Peering-related Pydantic schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class PeerRegistryCreate(BaseModel):
    """Schema for creating a peer registry."""
    
    name: str = Field(..., description="Peer registry name")
    base_url: HttpUrl = Field(..., description="Peer registry base URL")
    description: Optional[str] = Field(None, description="Peer registry description")
    auth_token: Optional[str] = Field(None, description="Authentication token for peer")
    sync_enabled: bool = Field(True, description="Enable automatic synchronization")
    sync_interval_minutes: int = Field(60, ge=1, description="Sync interval in minutes")


class PeerRegistryUpdate(BaseModel):
    """Schema for updating a peer registry."""
    
    name: Optional[str] = Field(None, description="Updated peer registry name")
    base_url: Optional[HttpUrl] = Field(None, description="Updated base URL")
    description: Optional[str] = Field(None, description="Updated description")
    auth_token: Optional[str] = Field(None, description="Updated auth token")
    sync_enabled: Optional[bool] = Field(None, description="Updated sync enabled status")
    sync_interval_minutes: Optional[int] = Field(None, ge=1, description="Updated sync interval")
    is_active: Optional[bool] = Field(None, description="Active status")


class PeerRegistryResponse(BaseModel):
    """Schema for peer registry response."""
    
    id: str = Field(..., description="Peer registry ID")
    name: str = Field(..., description="Peer registry name")
    base_url: str = Field(..., description="Peer registry base URL")
    description: Optional[str] = Field(None, description="Peer registry description")
    sync_enabled: bool = Field(..., description="Sync enabled status")
    sync_interval_minutes: int = Field(..., description="Sync interval")
    is_active: bool = Field(..., description="Active status")
    last_sync_at: Optional[str] = Field(None, description="Last sync timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
