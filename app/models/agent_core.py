"""Agent, versions, and entitlements for the registry."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import JSON
from sqlalchemy.sql import func

from .base import Base


class AgentRecord(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    publisher_id = Column(String, nullable=False, index=True)
    agent_key = Column(String, nullable=False, index=True)
    latest_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "publisher_id", "agent_key", name="uq_agents_pub_key"),
    )


class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(
        String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version = Column(String, nullable=False)
    protocol_version = Column(String, nullable=False)
    card_json = Column(JSON, nullable=False)
    card_hash = Column(String, nullable=False)
    card_url = Column(Text)
    jwks_url = Column(Text)
    signature_valid = Column(Boolean, server_default="false")
    public = Column(Boolean, server_default="true", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("agent_id", "version", name="uq_agent_versions_unique"),
    )


class Entitlement(Base):
    __tablename__ = "entitlements"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    client_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    scope = Column(String, nullable=False)  # view | use | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "client_id", "agent_id", "scope", name="uq_entitlements"),
    )
