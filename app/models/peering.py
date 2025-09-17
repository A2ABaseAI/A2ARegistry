"""Peering database models."""

import uuid
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class PeerRegistry(Base):
    """Peer registry database model."""

    __tablename__ = "peer_registries"

    # Core identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    base_url = Column(String, nullable=False, unique=True)
    description = Column(Text)

    # Authentication
    auth_token = Column(String)  # Encrypted in production

    # Synchronization settings
    sync_enabled = Column(Boolean, default=True, index=True)
    sync_interval_minutes = Column(Integer, default=60)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_sync_at = Column(DateTime, nullable=True)

    # Relationships
    syncs = relationship(
        "PeerSync", back_populates="peer_registry", cascade="all, delete-orphan"
    )

    def to_peer_response(self) -> dict:
        """Convert to PeerRegistryResponse format."""
        return {
            "id": self.id,
            "name": self.name,
            "base_url": self.base_url,
            "description": self.description,
            "sync_enabled": self.sync_enabled,
            "sync_interval_minutes": self.sync_interval_minutes,
            "is_active": self.is_active,
            "last_sync_at": (
                self.last_sync_at.isoformat() if self.last_sync_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PeerSync(Base):
    """Peer synchronization log model."""

    __tablename__ = "peer_syncs"

    # Core identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    peer_registry_id = Column(
        String, ForeignKey("peer_registries.id"), nullable=False, index=True
    )

    # Sync details
    sync_type = Column(String, nullable=False)  # "full", "incremental", "manual"
    status = Column(String, nullable=False)  # "success", "failed", "in_progress"
    agents_synced = Column(Integer, default=0)
    agents_added = Column(Integer, default=0)
    agents_updated = Column(Integer, default=0)
    agents_removed = Column(Integer, default=0)

    # Error handling
    error_message = Column(Text)

    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    peer_registry = relationship("PeerRegistry", back_populates="syncs")

    def to_sync_response(self) -> dict:
        """Convert to sync response format."""
        return {
            "id": self.id,
            "peer_registry_id": self.peer_registry_id,
            "sync_type": self.sync_type,
            "status": self.status,
            "agents_synced": self.agents_synced,
            "agents_added": self.agents_added,
            "agents_updated": self.agents_updated,
            "agents_removed": self.agents_removed,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
