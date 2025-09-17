"""Client database models."""

import uuid
from typing import List
from sqlalchemy import Column, String, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Client(Base):
    """Client database model."""
    
    __tablename__ = "clients"
    
    # Core identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    contact_email = Column(String)
    
    # OAuth2 credentials
    client_id = Column(String, unique=True, nullable=False, index=True)
    client_secret = Column(String, nullable=False)
    
    # OAuth2 configuration
    redirect_uris = Column(JSON, default=list)  # List of strings
    scopes = Column(JSON, default=list)  # List of strings
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="client", cascade="all, delete-orphan")
    entitlements = relationship("ClientEntitlement", back_populates="client", cascade="all, delete-orphan")
    
    def to_client_response(self) -> dict:
        """Convert to ClientResponse format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "contact_email": self.contact_email,
            "redirect_uris": self.redirect_uris or [],
            "scopes": self.scopes or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ClientEntitlement(Base):
    """Client entitlement database model."""
    
    __tablename__ = "client_entitlements"
    
    # Core identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    
    # Entitlement details
    scopes = Column(JSON, default=list)  # List of strings
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="entitlements")
    agent = relationship("Agent", back_populates="entitlements")
    
    def to_entitlement_response(self) -> dict:
        """Convert to ClientEntitlementResponse format."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "agent_id": self.agent_id,
            "scopes": self.scopes or [],
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
