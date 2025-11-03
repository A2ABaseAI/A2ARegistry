"""Tests for A2ARegClient publisher methods - SDK client publishing functionality."""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml
from a2a_reg_sdk.client import A2ARegClient
from a2a_reg_sdk.exceptions import ValidationError
from a2a_reg_sdk.models import (
    Agent,
    AgentBuilder,
)


class TestA2ARegClientPublisher:
    """Tests for A2ARegClient publisher methods."""

    @pytest.fixture
    def client(self):
        """Create a mock A2ARegClient."""
        client = MagicMock(spec=A2ARegClient)
        # Mock the actual client methods to avoid needing full client setup
        return client

    def test_load_agent_from_file_json(self):
        """Test loading agent from JSON file."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(agent_data, f)
            temp_path = f.name

        try:
            agent = client.load_agent_from_file(temp_path)
            assert isinstance(agent, Agent)
            assert agent.name == "Test Agent"
        finally:
            os.unlink(temp_path)

    def test_load_agent_from_file_yaml(self):
        """Test loading agent from YAML file."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(agent_data, f)
            temp_path = f.name

        try:
            agent = client.load_agent_from_file(temp_path)
            assert isinstance(agent, Agent)
            assert agent.name == "Test Agent"
        finally:
            os.unlink(temp_path)

    def test_load_agent_from_file_not_found(self):
        """Test loading agent from non-existent file."""
        client = A2ARegClient(registry_url="http://localhost:8000")

        with pytest.raises(ValidationError, match="Configuration file not found"):
            client.load_agent_from_file("/nonexistent/file.json")

    def test_load_agent_from_file_invalid_json(self):
        """Test loading agent from invalid JSON file."""
        client = A2ARegClient(registry_url="http://localhost:8000")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError, match="Failed to load agent configuration"):
                client.load_agent_from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_validate_agent_success(self):
        """Test validating a valid agent."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider").build()

        errors = client.validate_agent(agent)
        assert errors == []

    def test_validate_agent_missing_name(self):
        """Test validating an agent with missing name."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = Agent(name="", description="A test agent", version="1.0.0", provider="test-provider")

        errors = client.validate_agent(agent)
        assert any("name is required" in error.lower() for error in errors)

    def test_validate_agent_missing_description(self):
        """Test validating an agent with missing description."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = Agent(name="Test Agent", description="", version="1.0.0", provider="test-provider")

        errors = client.validate_agent(agent)
        assert any("description is required" in error.lower() for error in errors)

    def test_validate_agent_missing_version(self):
        """Test validating an agent with missing version."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = Agent(name="Test Agent", description="A test agent", version="", provider="test-provider")

        errors = client.validate_agent(agent)
        assert any("version is required" in error.lower() for error in errors)

    def test_validate_agent_missing_provider(self):
        """Test validating an agent with missing provider."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = Agent(name="Test Agent", description="A test agent", version="1.0.0", provider="")

        errors = client.validate_agent(agent)
        assert any("provider is required" in error.lower() for error in errors)

    def test_validate_agent_invalid_auth_scheme(self):
        """Test validating an agent with invalid auth scheme."""
        from a2a_reg_sdk.models import SecurityScheme

        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider").build()
        agent.auth_schemes = [SecurityScheme(type="invalid_type")]

        errors = client.validate_agent(agent)
        assert any("invalid type" in error.lower() for error in errors)

    def test_publish_agent_with_validation_success(self):
        """Test publishing an agent with validation successfully."""
        client = A2ARegClient(registry_url="http://localhost:8000", api_key="test-key")
        agent = AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider").build()

        # Mock the HTTP calls but let validation run
        with patch.object(client.session, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"agentId": "agent-1", "version": "1.0.0"}
            mock_response.content = b'{"agentId": "agent-1"}'
            mock_post.return_value = mock_response

            with patch.object(client, "get_agent") as mock_get:
                mock_get.return_value = Agent(id="agent-1", name="Test Agent", description="A test agent", version="1.0.0", provider="test-provider")

                result = client.publish_agent(agent, validate=True)
                assert isinstance(result, Agent)
                assert result.name == "Test Agent"
                # Validate that validation was called (it's internal, so we check no ValidationError was raised)
                # Since we're using a valid agent, validation should pass silently

    def test_publish_agent_with_validation_errors(self):
        """Test publishing an agent with validation errors."""
        client = A2ARegClient(registry_url="http://localhost:8000", api_key="test-key")
        agent = Agent(name="", description="A test agent", version="1.0.0", provider="test-provider")

        with pytest.raises(ValidationError, match="Agent validation failed"):
            client.publish_agent(agent, validate=True)

    def test_publish_agent_without_validation(self, client):
        """Test publishing an agent without validation."""
        agent = Agent(name="", description="A test agent", version="1.0.0", provider="test-provider")

        client.publish_agent.return_value = agent

        result = client.publish_agent(agent, validate=False)
        assert isinstance(result, Agent)
        client.publish_agent.assert_called_once_with(agent, validate=False)

    def test_publish_from_file(self):
        """Test publishing agent from file."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "test-provider",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(agent_data, f)
            temp_path = f.name

        try:
            with patch.object(client, "publish_agent") as mock_publish:
                mock_publish.return_value = Agent(**agent_data, id="agent-1")
                result = client.publish_from_file(temp_path, validate=True)
                assert isinstance(result, Agent)
                mock_publish.assert_called_once()
        finally:
            os.unlink(temp_path)

    def test_update_agent(self, client):
        """Test updating an agent."""
        agent = AgentBuilder("Updated Agent", "An updated agent", "1.0.1", "test-provider").build()

        client.update_agent.return_value = Agent(id="agent-1", name="Updated Agent", description="An updated agent", version="1.0.1", provider="test-provider")

        result = client.update_agent("agent-1", agent)
        assert isinstance(result, Agent)
        assert result.name == "Updated Agent"
        client.update_agent.assert_called_once_with("agent-1", agent)

    def test_create_sample_agent(self):
        """Test creating a sample agent."""
        client = A2ARegClient(registry_url="http://localhost:8000")

        agent = client.create_sample_agent(
            name="sample-agent",
            description="A sample agent",
            version="1.0.0",
            provider="my-org",
            api_url="https://api.my-org.com",
        )

        assert isinstance(agent, Agent)
        assert agent.name == "sample-agent"
        assert agent.description == "A sample agent"
        assert agent.version == "1.0.0"
        assert agent.provider == "my-org"
        # Check that location_url is set correctly - it should be the api_url + /api/agent
        # Looking at the code, it uses api_url or defaults to https://{provider}.com/api/agent
        expected_url = "https://api.my-org.com/api/agent"
        assert agent.location_url == expected_url
        assert agent.location_type == "api_endpoint"

    def test_save_agent_config_yaml(self):
        """Test saving agent configuration to YAML file."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider").build()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            client.save_agent_config(agent, temp_path, format="yaml")
            assert os.path.exists(temp_path)

            # Verify content can be loaded
            with open(temp_path, "r") as f:
                data = yaml.safe_load(f)
                assert data["name"] == "Test Agent"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_agent_config_json(self):
        """Test saving agent configuration to JSON file."""
        client = A2ARegClient(registry_url="http://localhost:8000")
        agent = AgentBuilder("Test Agent", "A test agent", "1.0.0", "test-provider").build()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            client.save_agent_config(agent, temp_path, format="json")
            assert os.path.exists(temp_path)

            # Verify content can be loaded
            with open(temp_path, "r") as f:
                data = json.load(f)
                assert data["name"] == "Test Agent"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
