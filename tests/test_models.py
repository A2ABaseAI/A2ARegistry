"""Tests for app/models/ - Database models."""

import pytest


from app.models.agent_core import AgentRecord, AgentVersion, Entitlement
from .base_test import BaseTest


class TestModels(BaseTest):
    """Tests for database models."""

    def test_agent_record_creation(self, db_session):
        """Test AgentRecord model creation."""
        agent_record = self.create_test_agent_record(db_session)

        # Verify the record was created
        assert agent_record.id == "test-agent-123"
        assert agent_record.publisher_id == "test-publisher"
        assert agent_record.tenant_id == "default"
        assert agent_record.agent_key == "test-key-test-agent-123"  # Updated to match new unique key format
        assert agent_record.latest_version == "1.0.0"

        # Verify it was saved to database
        saved_record = db_session.query(AgentRecord).filter_by(id="test-agent-123").first()
        assert saved_record is not None
        assert saved_record.id == agent_record.id

    def test_agent_version_creation(self, db_session):
        """Test AgentVersion model creation."""
        # First create an agent record
        self.create_test_agent_record(db_session)

        agent_version = self.create_test_agent_version(db_session)

        # Verify the version was created
        assert agent_version.id == "version-test-agent-123"
        assert agent_version.agent_id == "test-agent-123"
        assert agent_version.version == "1.0.0"
        assert agent_version.protocol_version == "0.3.0"
        assert agent_version.public is True
        assert agent_version.signature_valid is True

        # Verify it was saved to database
        saved_version = db_session.query(AgentVersion).filter_by(
            id="version-test-agent-123"
        ).first()
        assert saved_version is not None
        assert saved_version.id == agent_version.id

    def test_entitlement_creation(self, db_session):
        """Test Entitlement model creation."""
        # First create an agent record
        self.create_test_agent_record(db_session)

        entitlement = self.create_test_entitlement(db_session)

        # Verify the entitlement was created
        assert entitlement.id == "entitlement-test-agent-123"
        assert entitlement.tenant_id == "default"
        assert entitlement.client_id == "test-client"
        assert entitlement.agent_id == "test-agent-123"
        assert entitlement.scope == "view"

        # Verify it was saved to database
        saved_entitlement = db_session.query(Entitlement).filter_by(
            id="entitlement-test-agent-123"
        ).first()
        assert saved_entitlement is not None
        assert saved_entitlement.id == entitlement.id

    def test_agent_record_relationships(self, db_session):
        """Test AgentRecord relationships."""
        # Create agent record and versions
        agent_record, version1 = self.setup_complete_agent(db_session, "test-agent-123")

        self.create_test_agent_version(
            db_session,
            "test-agent-123",
            id="version-2",
            version="2.0.0",
            card_json={"name": "Test Agent v2"}
        )

        # Test relationships
        versions = db_session.query(AgentVersion).filter_by(agent_id="test-agent-123").all()
        assert len(versions) == 2
        assert any(v.version == "1.0.0" for v in versions)
        assert any(v.version == "2.0.0" for v in versions)

    def test_model_timestamps(self, db_session):
        """Test model timestamp fields."""
        agent_record = self.create_test_agent_record(db_session)

        # Check that timestamps are set
        assert agent_record.created_at is not None

        # AgentRecord only has created_at, not updated_at
        # Test that created_at is set
        assert agent_record.created_at is not None

    def test_agent_version_json_field(self, db_session):
        """Test AgentVersion JSON field handling."""
        self.create_test_agent_record(db_session)

        complex_card_json = {
            "name": "Test Agent",
            "description": "A test agent",
            "capabilities": {
                "a2a_version": "0.3.0",
                "supported_protocols": ["text"],
                "text": True
            },
            "skills": [],
            "authSchemes": []
        }

        agent_version = self.create_test_agent_version(
            db_session,
            card_json=complex_card_json
        )

        # Verify JSON field is stored and retrieved correctly
        assert agent_version.card_json == complex_card_json
        assert agent_version.card_json["name"] == "Test Agent"
        assert agent_version.card_json["capabilities"]["a2a_version"] == "0.3.0"

    def test_entitlement_scopes(self, db_session):
        """Test Entitlement scope field."""
        self.create_test_agent_record(db_session)

        # Test different scopes
        scopes = ["view", "use", "admin"]
        for scope in scopes:
            entitlement = self.create_test_entitlement(
                db_session,
                agent_id=f"test-agent-{scope}",
                id=f"entitlement-{scope}",
                scope=scope
            )
            assert entitlement.scope == scope

    def test_agent_record_constraints(self, db_session):
        """Test AgentRecord field constraints."""
        # Test required fields - this should succeed with all required fields
        agent_record = AgentRecord(
            id="test-agent-id",
            tenant_id="default",
            publisher_id="test-publisher",
            agent_key="test-key"
        )
        db_session.add(agent_record)
        db_session.commit()
        
        # Verify the record was created
        assert agent_record.id == "test-agent-id"
        assert agent_record.tenant_id == "default"
        assert agent_record.publisher_id == "test-publisher"
        assert agent_record.agent_key == "test-key"

    def test_agent_version_constraints(self, db_session):
        """Test AgentVersion field constraints."""
        self.create_test_agent_record(db_session)

        # Test required fields - this should succeed with all required fields
        agent_version = AgentVersion(
            id="test-agent:1.0.0",
            agent_id="test-agent-id",
            version="1.0.0",
            protocol_version="0.3.0",
            card_json={},
            card_hash="test-hash"
        )
        db_session.add(agent_version)
        db_session.commit()
        
        # Verify the record was created
        assert agent_version.id == "test-agent:1.0.0"
        assert agent_version.agent_id == "test-agent-id"
        assert agent_version.version == "1.0.0"

    def test_entitlement_constraints(self, db_session):
        """Test Entitlement field constraints."""
        self.create_test_agent_record(db_session)

        # Test required fields - this should succeed with all required fields
        entitlement = Entitlement(
            id="test-entitlement-id",
            tenant_id="default",
            client_id="test-client",
            agent_id="test-agent-id",
            scope="read"
        )
        db_session.add(entitlement)
        db_session.commit()
        
        # Verify the record was created
        assert entitlement.id == "test-entitlement-id"
        assert entitlement.tenant_id == "default"
        assert entitlement.client_id == "test-client"
        assert entitlement.scope == "read"

    def test_complete_agent_setup(self, db_session):
        """Test the complete agent setup helper method."""
        agent_record, agent_version = self.setup_complete_agent(db_session)

        # Verify both were created
        assert agent_record.id == "test-agent-123"
        assert agent_version.agent_id == "test-agent-123"

        # Verify they're linked
        assert agent_record.latest_version == agent_version.version

        # Verify they're in the database
        saved_record = db_session.query(AgentRecord).filter_by(id="test-agent-123").first()
        saved_version = db_session.query(AgentVersion).filter_by(agent_id="test-agent-123").first()

        assert saved_record is not None
        assert saved_version is not None
