import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.base_test import BaseTest


class TestAgentsAPI(BaseTest):
    """Tests for agent management API endpoints."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch):
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

        # Don't clear all overrides, just the db one
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]

    def test_public_agents_endpoint(self, client, db_session, mock_services_db):
        """Test public agents endpoint."""
        # Create test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        response = client.get("/agents/public")
        assert response.status_code == 200

        data = response.json()
        self.assert_paginated_response_structure(data)
        assert len(data["items"]) == 2

    def test_entitled_agents_endpoint(self, client, db_session, mock_auth, mock_services_db):
        """Test entitled agents endpoint."""
        # Create test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        # Create entitlement
        self.create_test_entitlement(db_session, "agent-1", client_id="test-client")

        response = client.get("/agents/entitled")
        assert response.status_code == 200

        data = response.json()
        self.assert_paginated_response_structure(data)
        assert len(data["items"]) >= 1

    def test_publish_agent_valid_data(self, client, db_session, mock_auth, mock_services_db):
        """Test publishing agent with valid data."""
        valid_data = self.get_valid_publish_data()

        response = client.post("/agents/publish", json=valid_data)
        assert response.status_code == 201

        data = response.json()
        self.assert_agent_response_structure(data)
        assert data["public"] is True
        assert data["signatureValid"] is False

    def test_publish_agent_invalid_data(self, client, mock_auth):
        """Test publishing agent with invalid data."""
        invalid_data = {
            "public": True,
            "card": {
                "name": "Invalid Agent",
            },
        }

        response = client.post("/agents/publish", json=invalid_data)
        assert response.status_code == 400

    def test_publish_agent_by_url(self, client, db_session, mock_auth):
        """Test publishing agent by URL."""
        url_data = {"public": True, "cardUrl": "https://example.com/agent-card.json"}

        response = client.post("/agents/publish", json=url_data)
        assert response.status_code in [400, 500]

    def test_agent_info_endpoint(self, client, db_session, mock_auth, mock_services_db):
        """Test agent info endpoint."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent-123")

        response = client.get(f"/agents/{agent_record.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["agentId"] == agent_record.id

    def test_agent_info_not_found(self, client, mock_auth):
        """Test agent info endpoint with non-existent agent."""
        response = client.get("/agents/non-existent-agent")
        assert response.status_code == 404

    def test_agent_card_endpoint(self, client, db_session, mock_auth, mock_services_db):
        """Test agent card endpoint."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "test-agent-123")

        response = client.get(f"/agents/{agent_record.id}/card")
        assert response.status_code == 200

        data = response.json()
        assert "protocolVersion" in data
        assert "name" in data

    def test_agent_card_not_found(self, client, mock_auth):
        """Test agent card endpoint with non-existent agent."""
        response = client.get("/agents/non-existent-agent/card")
        assert response.status_code == 404

    def test_agent_card_public(self, client, db_session, mock_auth, mock_services_db):
        """Test accessing public agent card."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "public-agent", public=True)

        response = client.get(f"/agents/{agent_record.id}/card")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Agent"

    def test_agent_card_private_access_denied(self, client, db_session, mock_auth, mock_services_db):
        """Test accessing private agent card without entitlement."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "private-agent", public=False)

        response = client.get(f"/agents/{agent_record.id}/card")
        assert response.status_code == 403

    def test_agent_card_private_with_entitlement(self, client, db_session, mock_auth, mock_services_db):
        """Test accessing private agent card with entitlement."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "private-agent", public=False)

        self.create_test_entitlement(db_session, "private-agent", client_id="test-client")

        response = client.get(f"/agents/{agent_record.id}/card")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Agent"

    def test_search_endpoint(self, client, mock_auth):
        """Test search endpoint."""
        search_data = {"q": "test", "top": 10, "skip": 0}

        response = client.post("/agents/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        self.assert_paginated_response_structure(data)

    def test_pagination_parameters(self, client, db_session, mock_auth, mock_services_db):
        """Test pagination parameters."""
        for i in range(5):
            self.setup_complete_agent(db_session, f"agent-{i}")

        response = client.get("/agents/public?top=2&skip=0")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) <= 2

    def test_authentication_required(self, db_session, mock_redis, mock_opensearch):
        """Test that authentication is required for protected endpoints."""
        from app.database import get_db

        def get_test_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = get_test_db

        with TestClient(app) as client:
            response = client.get("/agents/entitled")
            assert response.status_code == 401

        app.dependency_overrides.clear()

    def test_role_based_access_control(self, client, mock_auth, mock_services_db):
        """Test role-based access control for publish endpoint."""
        valid_data = self.get_valid_publish_data()

        response = client.post("/agents/publish", json=valid_data)
        assert response.status_code == 201

    def test_agent_card_data_structure(self, client, db_session, mock_auth, mock_services_db):
        """Test agent card data structure."""
        agent_record, agent_version = self.setup_complete_agent(db_session, "structure-test-agent")

        response = client.get(f"/agents/{agent_record.id}/card")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["protocolVersion", "name", "description", "capabilities", "skills"]
        for field in required_fields:
            assert field in data
