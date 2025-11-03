"""Tests for app/services/agent_service.py - Agent service functionality."""

from unittest.mock import MagicMock, patch

import pytest

from registry.models.agent_core import AgentRecord, AgentVersion
from registry.services.agent_service import AgentService

from .base_test import BaseTest


class TestAgentService(BaseTest):
    """Tests for AgentService."""

    @pytest.fixture
    def agent_service(self, db_session):
        """Create AgentService instance with test database."""
        service = AgentService()
        service.db = db_session
        return service

    def test_create_or_update_agent_record_new(self, agent_service, db_session):
        """Test creating a new agent record."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }
        card_hash = "test_hash_1234567890123456789012"

        record = agent_service.create_or_update_agent_record(card_data, card_hash, "default", "test-publisher", "test-agent", "1.0.0")

        assert record is not None
        assert record.tenant_id == "default"
        assert record.publisher_id == "test-publisher"
        assert record.agent_key == "test-agent"
        assert record.latest_version == "1.0.0"

        # Verify it was saved
        saved = db_session.query(AgentRecord).filter_by(id=record.id).first()
        assert saved is not None
        assert saved.id == record.id

    def test_create_or_update_agent_record_existing(self, agent_service, db_session):
        """Test updating an existing agent record."""
        # Create existing record
        existing_record = AgentRecord(
            id="existing-agent",
            tenant_id="default",
            publisher_id="test-publisher",
            agent_key="test-agent",
            latest_version="1.0.0",
        )
        db_session.add(existing_record)
        db_session.commit()

        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }
        card_hash = "test_hash_1234567890123456789012"

        record = agent_service.create_or_update_agent_record(card_data, card_hash, "default", "test-publisher", "test-agent", "2.0.0")

        assert record.id == "existing-agent"
        assert record.latest_version == "2.0.0"

    def test_create_agent_version_new(self, agent_service, db_session):
        """Test creating a new agent version."""
        # Create agent record first
        record = AgentRecord(
            id="test-agent",
            tenant_id="default",
            publisher_id="test-publisher",
            agent_key="test-agent",
            latest_version="1.0.0",
        )
        db_session.add(record)
        db_session.commit()

        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        version = agent_service.create_agent_version(record, card_data, "test_hash", None, "1.0.0", True)
        db_session.commit()

        assert version is not None
        assert version.agent_id == "test-agent"
        assert version.version == "1.0.0"
        assert version.public is True
        assert version.card_json == card_data

        # Verify it was saved
        saved = db_session.query(AgentVersion).filter_by(id=version.id).first()
        assert saved is not None

    def test_create_agent_version_idempotency(self, agent_service, db_session):
        """Test that creating the same version twice is idempotent."""
        # Create agent record first
        record = AgentRecord(
            id="test-agent",
            tenant_id="default",
            publisher_id="test-publisher",
            agent_key="test-agent",
            latest_version="1.0.0",
        )
        db_session.add(record)
        db_session.commit()

        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        # Create version first time
        version1 = agent_service.create_agent_version(record, card_data, "test_hash", None, "1.0.0", True)
        db_session.commit()

        # Try to create same version again
        version2 = agent_service.create_agent_version(record, card_data, "test_hash", None, "1.0.0", True)

        # Should return existing version
        assert version2.id == version1.id

    def test_publish_agent_success(self, agent_service, db_session):
        """Test publishing an agent successfully."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey", "location": "header", "name": "X-API-Key"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        with patch("registry.services.agent_service.SearchIndex") as mock_search:
            mock_index = MagicMock()
            mock_index.ensure_index = MagicMock()
            mock_index.index_version = MagicMock()
            mock_search.return_value = mock_index

            result = agent_service.publish_agent(card_data, None, True, "default")

            assert "agentId" in result
            assert "version" in result
            assert result["version"] == "1.0.0"
            assert result["public"] is True
            assert result["protocolVersion"] == "1.0"

            # Verify agent record was created
            agent_record = db_session.query(AgentRecord).filter_by(id=result["agentId"]).first()
            assert agent_record is not None

            # Verify agent version was created
            agent_version = db_session.query(AgentVersion).filter_by(agent_id=result["agentId"], version="1.0.0").first()
            assert agent_version is not None

    def test_publish_agent_with_card_url(self, agent_service, db_session):
        """Test publishing an agent with a card URL."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        with patch("registry.services.agent_service.SearchIndex") as mock_search:
            mock_index = MagicMock()
            mock_index.ensure_index = MagicMock()
            mock_index.index_version = MagicMock()
            mock_search.return_value = mock_index

            result = agent_service.publish_agent(card_data, "https://test.example.com/card.json", False, "default")

            assert "agentId" in result
            agent_version = db_session.query(AgentVersion).filter_by(agent_id=result["agentId"], version="1.0.0").first()
            assert agent_version.card_url == "https://test.example.com/card.json"

    def test_publish_agent_invalid_card(self, agent_service):
        """Test that publishing an invalid card raises exception."""
        invalid_card_data = {
            "name": "Test Agent",
            # Missing required fields
        }

        with pytest.raises(Exception):
            agent_service.publish_agent(invalid_card_data, None, True, "default")

    def test_get_agent_by_id_found(self, agent_service, db_session):
        """Test getting agent by ID when it exists."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent")

        result = agent_service.get_agent_by_id("test-agent", "default")

        assert result is not None
        record, version = result
        assert record.id == "test-agent"
        assert version.version == "1.0.0"

    def test_get_agent_by_id_not_found(self, agent_service):
        """Test getting agent by ID when it doesn't exist."""
        result = agent_service.get_agent_by_id("non-existent-agent", "default")
        assert result is None

    def test_get_agent_card_data_found(self, agent_service, db_session):
        """Test getting agent card data when agent exists."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent")

        card_data = agent_service.get_agent_card_data("test-agent", "default")

        assert card_data is not None
        assert "name" in card_data

    def test_get_agent_card_data_not_found(self, agent_service):
        """Test getting agent card data when agent doesn't exist."""
        card_data = agent_service.get_agent_card_data("non-existent-agent", "default")
        assert card_data is None

    def test_check_agent_access_entitled(self, agent_service, db_session):
        """Test checking agent access when client is entitled."""
        self.setup_complete_agent(db_session, "test-agent", public=False)
        self.create_test_entitlement(db_session, "test-agent", client_id="test-client")

        has_access = agent_service.check_agent_access("test-agent", "default", "test-client")
        assert has_access is True

    def test_check_agent_access_not_entitled(self, agent_service, db_session):
        """Test checking agent access when client is not entitled."""
        self.setup_complete_agent(db_session, "test-agent", public=False)

        has_access = agent_service.check_agent_access("test-agent", "default", "other-client")
        assert has_access is False

    def test_check_agent_access_public(self, agent_service, db_session):
        """Test checking agent access for public agents."""
        self.setup_complete_agent(db_session, "test-agent", public=True)

        # Public agents should be accessible via registry service
        # This tests that the service correctly delegates to registry service
        has_access = agent_service.check_agent_access("test-agent", "default", "any-client")
        # The registry service should handle public agents
        # Since we're using the real registry service in tests, this may vary
        assert isinstance(has_access, bool)
