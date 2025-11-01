"""Tests for a2a_reg_sdk.client - A2A Registry Client SDK."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from a2a_reg_sdk.client import A2ARegClient
from a2a_reg_sdk.exceptions import A2AError, AuthenticationError, ValidationError, NotFoundError
from a2a_reg_sdk.models import Agent, AgentCardSpec


class TestA2ARegClient:
    """Tests for A2ARegClient."""

    def test_client_initialization_default(self):
        """Test client initialization with default parameters."""
        client = A2ARegClient()
        assert client.registry_url == "http://localhost:8000"
        assert client.client_id is None
        assert client.client_secret is None
        assert client.timeout == 30
        assert client._access_token is None
        assert client.session is not None

    def test_client_initialization_custom(self):
        """Test client initialization with custom parameters."""
        client = A2ARegClient(
            registry_url="https://registry.example.com",
            client_id="test-client",
            client_secret="test-secret",
            timeout=60,
            api_key="test-api-key",
        )
        assert client.registry_url == "https://registry.example.com"
        assert client.client_id == "test-client"
        assert client.client_secret == "test-secret"
        assert client.timeout == 60
        assert client._api_key == "test-api-key"
        assert "Authorization" in client.session.headers

    def test_set_api_key(self):
        """Test setting API key."""
        client = A2ARegClient()
        client.set_api_key("test-key", "X-Custom-Key")
        assert client._api_key == "test-key"
        assert client._api_key_header == "X-Custom-Key"
        assert client.session.headers["Authorization"] == "Bearer test-key"

    def test_authenticate_with_api_key(self):
        """Test authentication when API key is already set."""
        client = A2ARegClient(api_key="test-key")
        # Should not raise error and should return immediately
        client.authenticate()

    def test_authenticate_oauth_success(self):
        """Test successful OAuth authentication."""
        client = A2ARegClient(client_id="test-client", client_secret="test-secret", registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with patch.object(client.session, "post", return_value=mock_response):
            client.authenticate()
            assert client._access_token == "test-token"
            assert client._token_expires_at is not None
            assert client.session.headers["Authorization"] == "Bearer test-token"

    def test_authenticate_oauth_missing_credentials(self):
        """Test OAuth authentication without credentials."""
        client = A2ARegClient()
        with pytest.raises(AuthenticationError, match="Client ID and secret are required"):
            client.authenticate()

    def test_authenticate_oauth_failure(self):
        """Test OAuth authentication failure."""
        client = A2ARegClient(client_id="test-client", client_secret="test-secret", registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "invalid_client"}

        with patch.object(client.session, "post", return_value=mock_response):
            with pytest.raises(AuthenticationError):
                client.authenticate()

    def test_authenticate_with_custom_scope(self):
        """Test OAuth authentication with custom scope."""
        client = A2ARegClient(client_id="test-client", client_secret="test-secret", registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with patch.object(client.session, "post", return_value=mock_response) as mock_post:
            client.authenticate(scope="admin")
            # Verify scope was passed
            call_args = mock_post.call_args
            assert call_args[1]["data"]["scope"] == "admin"

    def test_get_health(self):
        """Test getting health status."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "version": "1.0.0"}

        with patch.object(client.session, "get", return_value=mock_response):
            result = client.get_health()
            assert result["status"] == "healthy"
            assert result["version"] == "1.0.0"

    def test_list_agents_public(self):
        """Test listing public agents."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": "agent-1", "name": "Agent 1"}],
            "count": 1,
            "page": 1,
            "limit": 20,
        }

        with patch.object(client.session, "get", return_value=mock_response):
            result = client.list_agents(page=1, limit=20, public_only=True)
            assert result["count"] == 1
            assert len(result["items"]) == 1

    def test_get_agent_success(self):
        """Test getting an agent successfully."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        agent_data = {
            "id": "agent-1",
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = agent_data

        with patch.object(client.session, "get", return_value=mock_response):
            agent = client.get_agent("agent-1")
            assert isinstance(agent, Agent)
            assert agent.id == "agent-1"
            assert agent.name == "Test Agent"

    def test_get_agent_not_found(self):
        """Test getting a non-existent agent."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.content = b'{"detail": "Agent not found"}'
        mock_response.json.return_value = {"detail": "Agent not found"}
        # Create HTTPError that will be raised by raise_for_status
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error

        with patch.object(client.session, "get", return_value=mock_response):
            # _handle_response will raise NotFoundError for 404 status
            with pytest.raises(NotFoundError):
                client.get_agent("non-existent")

    def test_get_agent_card_success(self):
        """Test getting agent card successfully."""
        client = A2ARegClient(registry_url="https://registry.example.com")

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

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = card_data

        with patch.object(client.session, "get", return_value=mock_response):
            card = client.get_agent_card("agent-1")
            assert isinstance(card, AgentCardSpec)
            assert card.name == "Test Agent"
            assert card.version == "1.0.0"

    def test_search_agents(self):
        """Test searching agents."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"items": [{"id": "agent-1", "name": "Agent 1"}], "count": 1}'
        mock_response.json.return_value = {
            "items": [{"id": "agent-1", "name": "Agent 1"}],
            "count": 1,
        }

        with patch.object(client.session, "post", return_value=mock_response):
            result = client.search_agents(query="test", filters={}, page=1, limit=10)
            assert result["count"] == 1
            assert len(result["items"]) == 1

    def test_search_agents_with_filters(self):
        """Test searching agents with filters."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"items": [], "count": 0}'
        mock_response.json.return_value = {"items": [], "count": 0}

        with patch.object(client.session, "post", return_value=mock_response):
            result = client.search_agents(query="test", filters={"publisherId": "test-publisher"}, page=1, limit=10)
            assert result["count"] == 0

    def test_publish_agent_with_dict(self):
        """Test publishing an agent using dictionary."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        publish_response = MagicMock()
        publish_response.status_code = 201
        publish_response.json.return_value = {"agentId": "agent-1", "version": "1.0.0"}

        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {**agent_data, "id": "agent-1"}

        with patch.object(client.session, "post", return_value=publish_response):
            with patch.object(client.session, "get", return_value=get_response):
                agent = client.publish_agent(agent_data)
                assert isinstance(agent, Agent)
                assert agent.name == "Test Agent"

    def test_publish_agent_with_agent_object(self):
        """Test publishing an agent using Agent object."""
        from a2a_reg_sdk.models import AgentBuilder, AgentCapabilitiesBuilder

        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        capabilities = AgentCapabilitiesBuilder().streaming(False).build()
        agent = (
            AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider")
            .with_capabilities(capabilities)
            .build()
        )

        publish_response = MagicMock()
        publish_response.status_code = 201
        publish_response.json.return_value = {"agentId": "agent-1", "version": "1.0.0"}

        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "id": "agent-1",
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        with patch.object(client.session, "post", return_value=publish_response):
            with patch.object(client.session, "get", return_value=get_response):
                result = client.publish_agent(agent)
                assert isinstance(result, Agent)
                assert result.name == "Test Agent"

    def test_update_agent(self):
        """Test updating an agent."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        agent_data = {
            "name": "Updated Agent",
            "description": "An updated agent",
            "version": "1.0.1",
            "provider": "test-provider",
        }

        response_data = {**agent_data, "id": "agent-1"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data

        with patch.object(client.session, "put", return_value=mock_response):
            agent = client.update_agent("agent-1", agent_data)
            assert isinstance(agent, Agent)
            assert agent.name == "Updated Agent"
            assert agent.version == "1.0.1"

    def test_delete_agent(self):
        """Test deleting an agent."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch.object(client.session, "delete", return_value=mock_response):
            # Should not raise exception
            client.delete_agent("agent-1")

    def test_delete_agent_not_found(self):
        """Test deleting a non-existent agent."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Agent not found"}
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        with patch.object(client.session, "delete", return_value=mock_response):
            with patch.object(client, "_handle_response", side_effect=NotFoundError("Agent not found")):
                with pytest.raises(NotFoundError):
                    client.delete_agent("non-existent")

    def test_get_registry_stats(self):
        """Test getting registry statistics."""
        client = A2ARegClient(registry_url="https://registry.example.com", api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_agents": 100,
            "total_publishers": 10,
            "total_versions": 200,
        }

        with patch.object(client.session, "get", return_value=mock_response):
            stats = client.get_registry_stats()
            assert stats["total_agents"] == 100
            assert stats["total_publishers"] == 10

    def test_handle_response_error(self):
        """Test handling response errors."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Bad request"}
        mock_response.raise_for_status.side_effect = requests.HTTPError()

        with patch("requests.Response.raise_for_status", side_effect=requests.HTTPError()):
            with pytest.raises(A2AError):
                client._handle_response(mock_response)

    def test_connection_error(self):
        """Test handling connection errors."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        with patch.object(client.session, "get", side_effect=ConnectionError("Connection failed")):
            with pytest.raises(A2AError):
                client.get_health()

    def test_timeout_error(self):
        """Test handling timeout errors."""
        client = A2ARegClient(registry_url="https://registry.example.com")

        with patch.object(client.session, "get", side_effect=Timeout("Request timed out")):
            with pytest.raises(A2AError):
                client.get_health()

    def test_context_manager(self):
        """Test client as context manager."""
        with A2ARegClient() as client:
            assert client is not None
            # Session should be closed on exit
            # We can't easily test this without mocking, but we can verify it doesn't raise
            pass

    def test_close(self):
        """Test closing the client."""
        client = A2ARegClient()
        # Should not raise
        client.close()
        # Can't easily verify session is closed, but it should handle multiple closes
        client.close()

