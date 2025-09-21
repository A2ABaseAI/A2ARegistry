"""Agent database models."""

import uuid
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Agent(Base):
    """Agent database model."""

    __tablename__ = "agents"

    # Core identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False)
    description = Column(Text)
    provider = Column(String, nullable=False, index=True)

    # Agent card data (stored as JSON)
    agent_card = Column(JSON, nullable=False)

    # Visibility and status
    is_public = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)

    # Location information
    location_url = Column(String)
    location_type = Column(String, default="agent_card")

    # Metadata
    tags = Column(JSON, default=list)  # List of strings
    capabilities = Column(JSON)  # AgentCapabilities
    auth_schemes = Column(JSON)  # List of AgentAuthScheme
    tee_details = Column(JSON)  # AgentTeeDetails

    # Ownership - simplified without client relationships
    owner_id = Column(String, nullable=True, index=True)  # Simple string identifier

    def to_agent_response(self) -> Dict[str, Any]:
        """Convert to AgentResponse format."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description or "",
            "provider": self.provider,
            "tags": self.tags or [],
            "is_public": self.is_public,
            "is_active": self.is_active,
            "location": {"url": self.location_url, "type": self.location_type},
            "capabilities": self.capabilities or {},
            "auth_schemes": self.auth_schemes or [],
            "tee_details": self.tee_details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_agent_card(self) -> Dict[str, Any]:
        """Convert to AgentCard format."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description or "",
            "capabilities": self.capabilities or {},
            "skills": self.agent_card.get("skills", {}),
            "auth_schemes": self.auth_schemes or [],
            "tee_details": self.tee_details,
            "provider": self.provider,
            "tags": self.tags or [],
            "location": {"url": self.location_url, "type": self.location_type},
        }
