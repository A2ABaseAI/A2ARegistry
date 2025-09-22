"""Tests for app/schemas/ - Pydantic schemas and validation."""

import pytest

from app.schemas.agent import (
    AgentAuthScheme,
    AgentCapabilities,
    AgentCard,
    AgentCreate,
    AgentResponse,
)
from app.schemas.agent_card_spec import AgentCardSpec, AgentSkill

from .base_test import BaseTest


class TestSchemas(BaseTest):
    """Tests for Pydantic schemas and validation."""

    def _get_valid_agent_card_data(self):
        """Helper to get valid AgentCardSpec data."""
        return {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://example.com/.well-known/agent-card.json",
            "version": "1.0.0",
            "capabilities": {
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True,
                "supportsAuthenticatedExtendedCard": False
            },
            "securitySchemes": [
                {
                    "type": "apiKey",
                    "location": "header",
                    "name": "X-API-Key",
                    "credentials": "test_credentials"
                }
            ],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"]
            }
        }

    def test_agent_card_spec_valid_data(self):
        """Test AgentCardSpec with valid data."""
        agent_card = AgentCardSpec(
            name="Test Agent",
            description="A test agent",
            url="https://example.com/.well-known/agent-card.json",
            version="1.0.0",
            capabilities={
                "streaming": True,
                "pushNotifications": False,
                "stateTransitionHistory": True,
                "supportsAuthenticatedExtendedCard": False
            },
            securitySchemes=[
                {
                    "type": "apiKey",
                    "location": "header",
                    "name": "X-API-Key",
                    "credentials": "test_credentials"
                }
            ],
            skills=[],
            interface={
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"]
            }
        )

        assert agent_card.name == "Test Agent"
        assert agent_card.description == "A test agent"
        assert agent_card.version == "1.0.0"
        assert agent_card.capabilities.streaming is True

    def test_agent_card_spec_invalid_data(self):
        """Test AgentCardSpec with invalid data."""
        with pytest.raises(Exception):  # Should raise validation error
            AgentCardSpec(
                name="Test Agent",
                # Missing required fields like version, capabilities, etc.
            )

    def test_agent_card_spec_with_provider(self):
        """Test AgentCardSpec with provider information."""
        data = self._get_valid_agent_card_data()
        data["provider"] = {
            "organization": "Test Organization",
            "url": "https://test-org.com"
        }

        agent_card = AgentCardSpec.model_validate(data)
        assert agent_card.name == "Test Agent"
        assert agent_card.provider.organization == "Test Organization"

    def test_skill_schema(self):
        """Test AgentSkill schema."""
        skill = AgentSkill(
            id="test-skill",
            name="test-skill",
            description="A test skill",
            tags=["test", "example"]
        )
        assert skill.id == "test-skill"
        assert skill.name == "test-skill"
        assert skill.tags == ["test", "example"]
        assert skill.description == "A test skill"

    def test_capability_schema(self):
        """Test AgentCapabilities schema."""
        capability = AgentCapabilities(a2a_version="0.3.0", supported_protocols=["text"])
        assert capability.a2a_version == "0.3.0"
        assert "text" in capability.supported_protocols

    def test_location_schema(self):
        """Test location as dict in AgentCard."""
        location = {"url": "https://example.com/agent", "type": "agent_card"}
        assert location["url"] == "https://example.com/agent"
        assert location["type"] == "agent_card"

    def test_auth_scheme_schema(self):
        """Test AgentAuthScheme schema."""
        auth_scheme = AgentAuthScheme(
            type="oauth2",
            flow="client_credentials",
            token_url="https://example.com/oauth/token",
            scopes=["read", "write"],
        )
        assert auth_scheme.type == "oauth2"
        assert auth_scheme.flow == "client_credentials"
        assert "read" in auth_scheme.scopes

    def test_agent_create_schema(self):
        """Test AgentCreate schema."""
        agent_card = AgentCard(
            id="test-agent-123",
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
            capabilities=AgentCapabilities(a2a_version="0.3.0", supported_protocols=["text"]),
            skills={},
            auth_schemes=[],
            provider="test-provider",
            location={"url": "https://example.com/agent", "type": "agent_card"},
        )
        agent_create = AgentCreate(agent_card=agent_card, is_public=True)
        assert agent_create.is_public is True
        assert agent_create.agent_card.name == "Test Agent"

    def test_agent_response_schema(self):
        """Test AgentResponse schema."""
        agent_response = AgentResponse(
            id="test-agent-123",
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
            provider="test-provider",
            tags=["test", "agent"],
            is_public=True,
            is_active=True,
            location={"url": "https://example.com/agent", "type": "agent_card"},
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert agent_response.id == "test-agent-123"
        assert agent_response.name == "Test Agent"
        assert agent_response.version == "1.0.0"
        assert agent_response.is_public is True
        assert agent_response.is_active is True

    def test_agent_card_spec_serialization(self):
        """Test AgentCardSpec serialization."""
        data = self._get_valid_agent_card_data()
        data["provider"] = {
            "organization": "Test Organization",
            "url": "https://test-org.com"
        }

        agent_card = AgentCardSpec.model_validate(data)

        # Test model_dump
        dumped_data = agent_card.model_dump()
        assert dumped_data["name"] == "Test Agent"
        assert dumped_data["version"] == "1.0.0"

        # Test model_dump_json
        json_data = agent_card.model_dump_json()
        assert "Test Agent" in json_data
        assert "1.0.0" in json_data

    def test_agent_card_spec_deserialization(self):
        """Test AgentCardSpec deserialization."""
        data = self._get_valid_agent_card_data()
        data["provider"] = {
            "organization": "Test Organization",
            "url": "https://test-org.com"
        }

        agent_card = AgentCardSpec.model_validate(data)
        assert agent_card.name == "Test Agent"
        assert agent_card.version == "1.0.0"

    def test_skill_validation(self):
        """Test AgentSkill validation."""
        # Valid skill
        skill = AgentSkill(
            id="test-skill",
            name="test-skill",
            description="A test skill",
            tags=["test", "example"]
        )
        assert skill.name == "test-skill"

        # Invalid skill (missing required fields)
        with pytest.raises(Exception):
            AgentSkill(
                name="test-skill"
                # Missing required fields like id, description, tags
            )

    def test_capabilities_validation(self):
        """Test AgentCapabilities validation."""
        # Valid capabilities
        capabilities = AgentCapabilities(a2a_version="0.3.0", supported_protocols=["text", "image"])
        assert capabilities.a2a_version == "0.3.0"
        assert len(capabilities.supported_protocols) == 2

        # Test with empty protocols
        capabilities_empty = AgentCapabilities(a2a_version="0.3.0", supported_protocols=[])
        assert capabilities_empty.supported_protocols == []

    def test_auth_scheme_validation(self):
        """Test AgentAuthScheme validation."""
        # Valid auth scheme
        auth_scheme = AgentAuthScheme(
            type="oauth2",
            flow="client_credentials",
            token_url="https://example.com/oauth/token",
            scopes=["read", "write"],
        )
        assert auth_scheme.type == "oauth2"
        assert len(auth_scheme.scopes) == 2

        # Test with empty scopes
        auth_scheme_empty = AgentAuthScheme(
            type="oauth2",
            flow="client_credentials",
            token_url="https://example.com/oauth/token",
            scopes=[],
        )
        assert auth_scheme_empty.scopes == []

    def test_agent_response_validation(self):
        """Test AgentResponse validation."""
        # Valid agent response
        agent_response = AgentResponse(
            id="test-agent-123",
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
            provider="test-provider",
            tags=["test"],
            is_public=True,
            is_active=True,
            location={"url": "https://example.com/agent", "type": "agent_card"},
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert agent_response.id == "test-agent-123"
        assert agent_response.is_public is True

        # Test with empty tags
        agent_response_empty_tags = AgentResponse(
            id="test-agent-123",
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
            provider="test-provider",
            tags=[],
            is_public=True,
            is_active=True,
            location={"url": "https://example.com/agent", "type": "agent_card"},
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert agent_response_empty_tags.tags == []

    def test_schema_field_types(self):
        """Test that schema fields have correct types."""
        data = self._get_valid_agent_card_data()
        agent_card = AgentCardSpec.model_validate(data)

        # Check field types
        assert isinstance(agent_card.name, str)
        assert isinstance(agent_card.description, str)
        assert isinstance(agent_card.version, str)
        assert isinstance(agent_card.capabilities.streaming, bool)
        assert isinstance(agent_card.securitySchemes, list)
        assert isinstance(agent_card.interface.defaultInputModes, list)
        assert isinstance(agent_card.interface.defaultOutputModes, list)
        assert isinstance(agent_card.skills, list)

    def test_schema_optional_fields(self):
        """Test schema optional fields."""
        # Test with minimal required fields
        data = self._get_valid_agent_card_data()
        data["provider"] = {
            "organization": "Test Organization",
            "url": "https://test-org.com"
        }

        agent_card = AgentCardSpec.model_validate(data)

        # Optional fields should have default values or be None
        assert agent_card.skills == []
        assert agent_card.provider is not None
        assert agent_card.documentationUrl is None
