import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.base_test import BaseTest


class TestWellKnownAPI(BaseTest):
    """Tests for well-known endpoints."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch, mock_services_db):
        """Create a test client with mocked dependencies."""
        from app.database import get_db

        def get_test_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = get_test_db

        with TestClient(app) as test_client:
            yield test_client

        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]

    def test_well_known_index(self, client, db_session):
        """Test well-known agents index endpoint."""
        # Create test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        response = client.get("/.well-known/agents/index.json")
        assert response.status_code == 200

        data = response.json()
        assert "agents" in data
        assert "count" in data
        assert len(data["agents"]) == 2

    def test_well_known_index_pagination(self, client, db_session):
        """Test well-known agents index pagination."""
        # Create multiple test agents
        for i in range(5):
            self.setup_complete_agent(db_session, f"agent-{i}")

        response = client.get(
            "/.well-known/agents/index.json?top=2&skip=0"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["agents"]) == 2
        assert data["count"] == 2

        response = client.get(
            "/.well-known/agents/index.json?top=2&skip=2"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["agents"]) == 2
        assert data["count"] == 2

    def test_well_known_agent_card(self, client, db_session, mock_auth):
        """Test well-known agent card endpoint."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent-123")

        response = client.get(
            f"/.well-known/agents/{agent_record.id}/card"
        )
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "protocolVersion" in data
        assert "capabilities" in data

    def test_well_known_agent_card_not_found(self, client, mock_auth):
        """Test well-known agent card endpoint with non-existent agent."""
        response = client.get("/.well-known/agents/non-existent-agent/card")
        assert response.status_code == 404

    def test_well_known_agent_card_public(self, client, db_session, mock_auth):
        """Test accessing public agent card via well-known endpoint."""
        agent_record, agent_version = self.setup_complete_agent(
            db_session, "public-agent", public=True
        )

        response = client.get(
            f"/.well-known/agents/{agent_record.id}/card"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Agent"

    def test_well_known_agent_card_private_access_denied(self, client, db_session, mock_auth):
        """Test accessing private agent card without entitlement."""
        agent_record, agent_version = self.setup_complete_agent(
            db_session, "private-agent", public=False
        )

        response = client.get(
            f"/.well-known/agents/{agent_record.id}/card"
        )
        assert response.status_code == 403

    def test_well_known_agent_card_private_with_entitlement(self, client, db_session, mock_auth):
        """Test accessing private agent card with entitlement."""
        agent_record, agent_version = self.setup_complete_agent(
            db_session, "private-agent", public=False
        )

        self.create_test_entitlement(db_session, "private-agent", client_id="test-client")

        response = client.get(
            f"/.well-known/agents/{agent_record.id}/card"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Agent"

    def test_well_known_index_structure(self, client, db_session):
        """Test well-known index response structure."""
        self.setup_complete_agent(db_session, "structure-test-agent")

        response = client.get("/.well-known/agents/index.json")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["agents", "count", "total_count", "registry_version", "registry_name"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check data types
        assert isinstance(data["agents"], list)
        assert isinstance(data["count"], int)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["registry_version"], str)
        assert isinstance(data["registry_name"], str)

    def test_well_known_agent_structure(self, client, db_session):
        """Test well-known agent structure in index."""
        self.setup_complete_agent(db_session, "structure-test-agent")

        response = client.get("/.well-known/agents/index.json")
        assert response.status_code == 200

        data = response.json()
        agents = data["agents"]

        assert len(agents) > 0
        agent = agents[0]

        # Check location structure
        assert "location" in agent
        location = agent["location"]
        assert "url" in location
        assert "type" in location
        assert location["type"] == "agent_card"

    def test_well_known_empty_index(self, client):
        """Test well-known index with no agents."""
        response = client.get("/.well-known/agents/index.json")
        assert response.status_code == 200

        data = response.json()
        assert data["agents"] == []
        assert data["count"] == 0
        assert data["total_count"] == 0

    def test_well_known_pagination_links(self, client, db_session):
        """Test well-known index pagination links."""
        # Create multiple agents
        for i in range(5):
            self.setup_complete_agent(db_session, f"agent-{i}")

        response = client.get(
            "/.well-known/agents/index.json?top=2&skip=0"
        )
        assert response.status_code == 200

        data = response.json()

        if data["count"] < data["total_count"]:
            assert "next" in data
            assert data["next"].startswith("/.well-known/agents/index.json")

    def test_well_known_agent_card_structure(self, client, db_session, mock_auth):
        """Test well-known agent card response structure."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "structure-test-agent")

        response = client.get(
            f"/.well-known/agents/{agent_record.id}/card"
        )
        assert response.status_code == 200

        data = response.json()
        required_fields = ["protocolVersion", "name", "description", "capabilities", "skills"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check capabilities structure
        assert "a2a_version" in data["capabilities"]
        assert "supported_protocols" in data["capabilities"]

    def test_well_known_endpoints_no_auth_required(self, client, db_session, mock_auth):
        """Test that well-known endpoints don't require authentication for public agents."""
        # Create public agent
        self.setup_complete_agent(db_session, "public-agent", public=True)

        # Test index endpoint (should be public)
        response = client.get("/.well-known/agents/index.json")
        assert response.status_code == 200

        # Test public agent card (should be accessible)
        response = client.get("/.well-known/agents/public-agent/card")
        assert response.status_code == 200

    def test_well_known_agent_card_authentication_required_for_private(
        self, client, db_session, mock_auth
    ):
        """Test that authentication is required for private agent cards."""
        # Create private agent
        self.setup_complete_agent(db_session, "private-agent", public=False)

        # Test without authentication
        response = client.get("/.well-known/agents/private-agent/card")
        assert response.status_code == 403
