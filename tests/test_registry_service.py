"""Tests for app/services/registry_service.py - Registry service functionality."""


from app.services.registry_service import RegistryService
from .base_test import BaseTest


class TestRegistryService(BaseTest):
    """Tests for RegistryService."""

    def test_registry_service_initialization(self, db_session):
        """Test RegistryService initialization."""
        service = RegistryService(db_session)
        assert service is not None
        assert service.db == db_session

    def test_list_public_agents(self, db_session):
        """Test listing public agents."""
        service = RegistryService(db_session)

        # Create some test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        # Test listing
        agents, count = service.list_public("default", top=10, skip=0)
        assert isinstance(agents, list)
        assert isinstance(count, int)
        assert len(agents) == 2

    def test_list_entitled_agents(self, db_session):
        """Test listing entitled agents."""
        service = RegistryService(db_session)

        # Create test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        # Create entitlement
        self.create_test_entitlement(db_session, "agent-1", client_id="test-client")

        # Test listing
        agents, count = service.list_entitled("default", "test-client", top=10, skip=0)
        assert isinstance(agents, list)
        assert isinstance(count, int)
        # Should include both public agents and entitled agent
        assert len(agents) >= 1

    def test_get_latest_agent(self, db_session):
        """Test getting latest agent version."""
        service = RegistryService(db_session)

        # Create test agent
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent-123")

        # Test getting latest
        result = service.get_latest("default", "test-agent-123")
        assert result is not None
        agent_record_result, agent_version_result = result
        assert agent_record_result.id == "test-agent-123"
        assert agent_version_result.version == "1.0.0"

    def test_get_latest_agent_not_found(self, db_session):
        """Test getting latest agent that doesn't exist."""
        service = RegistryService(db_session)

        result = service.get_latest("default", "non-existent-agent")
        assert result is None

    def test_is_entitled(self, db_session):
        """Test entitlement checking."""
        service = RegistryService(db_session)

        # Create test agent and entitlement
        self.setup_complete_agent(db_session, "test-agent-123")
        self.create_test_entitlement(db_session, "test-agent-123", client_id="test-client")

        # Test entitlement check
        assert service.is_entitled("default", "test-client", "test-agent-123") is True
        assert service.is_entitled("default", "other-client", "test-agent-123") is False
        assert service.is_entitled("default", "test-client", "other-agent") is False

    def test_agent_record_creation_with_data(self, db_session):
        """Test agent record creation with actual data."""
        service = RegistryService(db_session)

        # Create a test agent record
        self.create_test_agent_record(db_session)

        self.create_test_agent_version(db_session)

        # Test that we can retrieve it
        result = service.get_latest("default", "test-agent-123")
        assert result is not None
        agent_record_result, agent_version_result = result
        assert agent_record_result.id == "test-agent-123"
        assert agent_version_result.version == "1.0.0"

    def test_pagination(self, db_session):
        """Test pagination functionality."""
        service = RegistryService(db_session)

        # Create multiple test agents
        for i in range(5):
            self.setup_complete_agent(db_session, f"agent-{i}")

        # Test pagination
        agents_page1, count1 = service.list_public("default", top=2, skip=0)
        agents_page2, count2 = service.list_public("default", top=2, skip=2)

        assert len(agents_page1) == 2
        assert len(agents_page2) == 2
        assert count1 == count2  # Total count should be the same

        # Ensure different agents are returned
        agent_ids_page1 = {agent["agentId"] for agent in agents_page1}
        agent_ids_page2 = {agent["agentId"] for agent in agents_page2}
        assert agent_ids_page1.isdisjoint(agent_ids_page2)

    def test_tenant_isolation(self, db_session):
        """Test that agents are isolated by tenant."""
        service = RegistryService(db_session)

        # Create agents in different tenants
        self.create_test_agent_record(db_session, "agent-1", tenant_id="tenant-1")
        self.create_test_agent_version(db_session, "agent-1")
        self.create_test_agent_record(db_session, "agent-2", tenant_id="tenant-2")
        self.create_test_agent_version(db_session, "agent-2")

        # Test tenant isolation
        agents_tenant1, _ = service.list_public("tenant-1", top=10, skip=0)
        agents_tenant2, _ = service.list_public("tenant-2", top=10, skip=0)

        assert len(agents_tenant1) == 1
        assert len(agents_tenant2) == 1
        assert agents_tenant1[0]["agentId"] == "agent-1"
        assert agents_tenant2[0]["agentId"] == "agent-2"

    def test_public_vs_private_agents(self, db_session):
        """Test filtering of public vs private agents."""
        service = RegistryService(db_session)

        # Create public and private agents
        self.setup_complete_agent(db_session, "public-agent", public=True)
        self.setup_complete_agent(db_session, "private-agent", public=False)

        # Test public listing
        public_agents, _ = service.list_public("default", top=10, skip=0)
        public_agent_ids = {agent["agentId"] for agent in public_agents}

        assert "public-agent" in public_agent_ids
        assert "private-agent" not in public_agent_ids
