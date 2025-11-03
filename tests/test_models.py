"""Unit tests for a2a_reg_sdk.models - A2A Protocol specification models and builders."""

import pytest
from a2a_reg_sdk.models import (
    Agent,
    AgentBuilder,
    AgentCapabilities,
    AgentCapabilitiesBuilder,
    AgentCardSignature,
    AgentCardSignatureBuilder,
    AgentCardSpec,
    AgentCardSpecBuilder,
    AgentInterface,
    AgentInterfaceBuilder,
    AgentProvider,
    AgentProviderBuilder,
    AgentSkill,
    AgentSkillBuilder,
    SecurityScheme,
    SecuritySchemeBuilder,
)


class TestAgentProvider:
    """Tests for AgentProvider model."""

    def test_create_agent_provider(self):
        """Test creating an AgentProvider."""
        provider = AgentProvider(organization="Test Org", url="https://test.org")
        assert provider.organization == "Test Org"
        assert provider.url == "https://test.org"

    def test_agent_provider_from_dict(self):
        """Test creating AgentProvider from dictionary."""
        data = {"organization": "Test Org", "url": "https://test.org"}
        provider = AgentProvider.from_dict(data)
        assert provider.organization == "Test Org"
        assert provider.url == "https://test.org"

    def test_agent_provider_to_dict(self):
        """Test converting AgentProvider to dictionary."""
        provider = AgentProvider(organization="Test Org", url="https://test.org")
        data = provider.to_dict()
        assert data["organization"] == "Test Org"
        assert data["url"] == "https://test.org"


class TestAgentCapabilities:
    """Tests for AgentCapabilities model."""

    def test_create_agent_capabilities(self):
        """Test creating AgentCapabilities."""
        caps = AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=True,
            supportsAuthenticatedExtendedCard=False,
        )
        assert caps.streaming is True
        assert caps.pushNotifications is False
        assert caps.stateTransitionHistory is True
        assert caps.supportsAuthenticatedExtendedCard is False

    def test_agent_capabilities_from_dict(self):
        """Test creating AgentCapabilities from dictionary."""
        data = {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True,
            "supportsAuthenticatedExtendedCard": False,
        }
        caps = AgentCapabilities.from_dict(data)
        assert caps.streaming is True
        assert caps.pushNotifications is False

    def test_agent_capabilities_to_dict(self):
        """Test converting AgentCapabilities to dictionary."""
        caps = AgentCapabilities(streaming=True, pushNotifications=False)
        data = caps.to_dict()
        assert data["streaming"] is True
        assert data["pushNotifications"] is False
        # Only included fields should be in dict
        assert "stateTransitionHistory" not in data or data.get("stateTransitionHistory") is None


class TestSecurityScheme:
    """Tests for SecurityScheme model."""

    def test_create_security_scheme_api_key(self):
        """Test creating an API key SecurityScheme."""
        scheme = SecurityScheme(type="apiKey", location="header", name="X-API-Key", credentials="test_key")
        assert scheme.type == "apiKey"
        assert scheme.location == "header"
        assert scheme.name == "X-API-Key"
        assert scheme.credentials == "test_key"

    def test_create_security_scheme_oauth2(self):
        """Test creating an OAuth2 SecurityScheme."""
        scheme = SecurityScheme(
            type="oauth2",
            flow="client_credentials",
            tokenUrl="https://example.com/token",
            scopes=["read", "write"],
        )
        assert scheme.type == "oauth2"
        assert scheme.flow == "client_credentials"
        assert scheme.tokenUrl == "https://example.com/token"
        assert scheme.scopes == ["read", "write"]

    def test_security_scheme_from_dict(self):
        """Test creating SecurityScheme from dictionary."""
        data = {"type": "apiKey", "location": "header", "name": "Authorization"}
        scheme = SecurityScheme.from_dict(data)
        assert scheme.type == "apiKey"
        assert scheme.location == "header"
        assert scheme.name == "Authorization"

    def test_security_scheme_to_dict(self):
        """Test converting SecurityScheme to dictionary."""
        scheme = SecurityScheme(type="apiKey", location="header", name="X-API-Key")
        data = scheme.to_dict()
        assert data["type"] == "apiKey"
        assert data["location"] == "header"
        assert data["name"] == "X-API-Key"


class TestAgentSkill:
    """Tests for AgentSkill model."""

    def test_create_agent_skill(self):
        """Test creating an AgentSkill."""
        skill = AgentSkill(
            id="find_recipe",
            name="Find Recipe",
            description="Find recipes based on ingredients",
            tags=["cooking", "recipe"],
            examples=["I need a recipe for bread"],
            inputModes=["text/plain"],
            outputModes=["application/json"],
        )
        assert skill.id == "find_recipe"
        assert skill.name == "Find Recipe"
        assert skill.description == "Find recipes based on ingredients"
        assert skill.tags == ["cooking", "recipe"]
        assert skill.examples == ["I need a recipe for bread"]
        assert skill.inputModes == ["text/plain"]
        assert skill.outputModes == ["application/json"]

    def test_agent_skill_from_dict(self):
        """Test creating AgentSkill from dictionary."""
        data = {
            "id": "find_recipe",
            "name": "Find Recipe",
            "description": "Find recipes based on ingredients",
            "tags": ["cooking", "recipe"],
            "examples": ["I need a recipe for bread"],
        }
        skill = AgentSkill.from_dict(data)
        assert skill.id == "find_recipe"
        assert skill.name == "Find Recipe"
        assert skill.tags == ["cooking", "recipe"]

    def test_agent_skill_to_dict(self):
        """Test converting AgentSkill to dictionary."""
        skill = AgentSkill(
            id="find_recipe",
            name="Find Recipe",
            description="Find recipes based on ingredients",
            tags=["cooking", "recipe"],
        )
        data = skill.to_dict()
        assert data["id"] == "find_recipe"
        assert data["name"] == "Find Recipe"
        assert data["tags"] == ["cooking", "recipe"]
        # Optional fields should not be included if None
        assert "examples" not in data or data.get("examples") is None


class TestAgentInterface:
    """Tests for AgentInterface model."""

    def test_create_agent_interface(self):
        """Test creating an AgentInterface."""
        interface = AgentInterface(
            preferredTransport="jsonrpc",
            defaultInputModes=["text/plain", "application/json"],
            defaultOutputModes=["text/plain", "application/json"],
            additionalInterfaces=[{"transport": "http", "url": "https://example.com/api"}],
        )
        assert interface.preferredTransport == "jsonrpc"
        assert interface.defaultInputModes == ["text/plain", "application/json"]
        assert len(interface.additionalInterfaces) == 1

    def test_agent_interface_from_dict(self):
        """Test creating AgentInterface from dictionary."""
        data = {
            "preferredTransport": "jsonrpc",
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["application/json"],
        }
        interface = AgentInterface.from_dict(data)
        assert interface.preferredTransport == "jsonrpc"
        assert interface.defaultInputModes == ["text/plain"]

    def test_agent_interface_to_dict(self):
        """Test converting AgentInterface to dictionary."""
        interface = AgentInterface(
            preferredTransport="jsonrpc",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["application/json"],
        )
        data = interface.to_dict()
        assert data["preferredTransport"] == "jsonrpc"
        assert data["defaultInputModes"] == ["text/plain"]
        assert data["defaultOutputModes"] == ["application/json"]


class TestAgentCardSignature:
    """Tests for AgentCardSignature model."""

    def test_create_agent_card_signature(self):
        """Test creating an AgentCardSignature."""
        signature = AgentCardSignature(
            algorithm="RS256",
            signature="test_signature",
            jwksUrl="https://example.com/.well-known/jwks.json",
        )
        assert signature.algorithm == "RS256"
        assert signature.signature == "test_signature"
        assert signature.jwksUrl == "https://example.com/.well-known/jwks.json"

    def test_agent_card_signature_from_dict(self):
        """Test creating AgentCardSignature from dictionary."""
        data = {"algorithm": "RS256", "jwksUrl": "https://example.com/.well-known/jwks.json"}
        signature = AgentCardSignature.from_dict(data)
        assert signature.algorithm == "RS256"
        assert signature.jwksUrl == "https://example.com/.well-known/jwks.json"

    def test_agent_card_signature_to_dict(self):
        """Test converting AgentCardSignature to dictionary."""
        signature = AgentCardSignature(algorithm="RS256", jwksUrl="https://example.com/.well-known/jwks.json")
        data = signature.to_dict()
        assert data["algorithm"] == "RS256"
        assert data["jwksUrl"] == "https://example.com/.well-known/jwks.json"


class TestAgentCardSpec:
    """Tests for AgentCardSpec model."""

    def test_create_agent_card_spec(self):
        """Test creating an AgentCardSpec."""
        capabilities = AgentCapabilities(streaming=True)
        security_schemes = [SecurityScheme(type="apiKey", location="header", name="X-API-Key")]
        skills = [
            AgentSkill(
                id="find_recipe",
                name="Find Recipe",
                description="Find recipes",
                tags=["cooking"],
            )
        ]
        interface = AgentInterface(
            preferredTransport="jsonrpc",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["application/json"],
        )

        card_spec = AgentCardSpec(
            name="Recipe Agent",
            description="An AI agent for recipes",
            url="https://recipe-agent.example.com",
            version="1.0.0",
            capabilities=capabilities,
            securitySchemes=security_schemes,
            skills=skills,
            interface=interface,
        )
        assert card_spec.name == "Recipe Agent"
        assert card_spec.version == "1.0.0"
        assert len(card_spec.securitySchemes) == 1
        assert len(card_spec.skills) == 1

    def test_agent_card_spec_from_dict(self):
        """Test creating AgentCardSpec from dictionary."""
        data = {
            "name": "Recipe Agent",
            "description": "An AI agent for recipes",
            "url": "https://recipe-agent.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": True},
            "securitySchemes": [{"type": "apiKey", "location": "header", "name": "X-API-Key"}],
            "skills": [{"id": "find_recipe", "name": "Find Recipe", "description": "Find recipes", "tags": ["cooking"]}],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["application/json"],
            },
        }
        card_spec = AgentCardSpec.from_dict(data)
        assert card_spec.name == "Recipe Agent"
        assert len(card_spec.securitySchemes) == 1
        assert len(card_spec.skills) == 1

    def test_agent_card_spec_to_dict(self):
        """Test converting AgentCardSpec to dictionary."""
        capabilities = AgentCapabilities(streaming=True)
        security_schemes = {"apiKey": SecurityScheme(type="apiKey")}
        skills = [AgentSkill(id="find_recipe", name="Find Recipe", description="Find recipes", tags=["cooking"])]
        interface = AgentInterface(
            preferredTransport="jsonrpc",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["application/json"],
        )

        card_spec = AgentCardSpec(
            name="Recipe Agent",
            description="An AI agent for recipes",
            url="https://recipe-agent.example.com",
            version="1.0.0",
            capabilities=capabilities,
            securitySchemes=security_schemes,
            skills=skills,
            interface=interface,
        )
        data = card_spec.to_dict()
        assert data["name"] == "Recipe Agent"
        assert data["version"] == "1.0.0"
        assert len(data["securitySchemes"]) == 1
        assert len(data["skills"]) == 1


class TestAgent:
    """Tests for Agent model."""

    def test_create_agent(self):
        """Test creating an Agent."""
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            provider="Test Provider",
        )
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.version == "1.0.0"
        assert agent.provider == "Test Provider"
        assert agent.is_public is True
        assert agent.is_active is True

    def test_agent_from_dict(self):
        """Test creating Agent from dictionary."""
        data = {
            "name": "Test Agent",
            "description": "A test agent",
            "version": "1.0.0",
            "provider": "Test Provider",
            "tags": ["test"],
            "is_public": True,
            "is_active": True,
        }
        agent = Agent.from_dict(data)
        assert agent.name == "Test Agent"
        assert agent.provider == "Test Provider"
        assert agent.tags == ["test"]

    def test_agent_to_dict(self):
        """Test converting Agent to dictionary."""
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            provider="Test Provider",
            tags=["test"],
        )
        data = agent.to_dict()
        assert data["name"] == "Test Agent"
        assert data["provider"] == "Test Provider"
        assert data["tags"] == ["test"]

    def test_agent_with_skills_list(self):
        """Test Agent with skills as a list of AgentSkill."""
        skills = [
            AgentSkill(id="skill1", name="Skill 1", description="First skill", tags=["test"]),
            AgentSkill(id="skill2", name="Skill 2", description="Second skill", tags=["test"]),
        ]
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            provider="Test Provider",
            skills=skills,
        )
        assert agent.skills == skills
        assert len(agent.skills) == 2

    def test_agent_with_agent_card_spec(self):
        """Test Agent with AgentCardSpec."""
        capabilities = AgentCapabilities(streaming=True)
        security_schemes = [SecurityScheme(type="apiKey")]
        skills = [AgentSkill(id="skill1", name="Skill 1", description="First skill", tags=["test"])]
        interface = AgentInterface(
            preferredTransport="jsonrpc",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["application/json"],
        )

        card_spec = AgentCardSpec(
            name="Test Agent",
            description="A test agent",
            url="https://test.example.com",
            version="1.0.0",
            capabilities=capabilities,
            securitySchemes=security_schemes,
            skills=skills,
            interface=interface,
        )

        agent = Agent(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            provider="Test Provider",
            agent_card=card_spec,
        )
        assert agent.agent_card == card_spec
        assert isinstance(agent.agent_card, AgentCardSpec)


class TestAgentProviderBuilder:
    """Tests for AgentProviderBuilder."""

    def test_build_agent_provider(self):
        """Test building an AgentProvider using the builder."""
        provider = AgentProviderBuilder("Test Org", "https://test.org").build()
        assert provider.organization == "Test Org"
        assert provider.url == "https://test.org"


class TestAgentCapabilitiesBuilder:
    """Tests for AgentCapabilitiesBuilder."""

    def test_build_capabilities(self):
        """Test building AgentCapabilities using the builder."""
        caps = (
            AgentCapabilitiesBuilder()
            .streaming(True)
            .push_notifications(False)
            .state_transition_history(True)
            .supports_authenticated_extended_card(False)
            .build()
        )
        assert caps.streaming is True
        assert caps.pushNotifications is False
        assert caps.stateTransitionHistory is True
        assert caps.supportsAuthenticatedExtendedCard is False

    def test_builder_fluent_interface(self):
        """Test that builder methods return self for fluent chaining."""
        builder = AgentCapabilitiesBuilder()
        result = builder.streaming(True).push_notifications(False)
        assert result is builder


class TestSecuritySchemeBuilder:
    """Tests for SecuritySchemeBuilder."""

    def test_build_api_key_scheme(self):
        """Test building an API key SecurityScheme."""
        scheme = SecuritySchemeBuilder("apiKey").location("header").name("X-API-Key").credentials("test_key").build()
        assert scheme.type == "apiKey"
        assert scheme.location == "header"
        assert scheme.name == "X-API-Key"
        assert scheme.credentials == "test_key"

    def test_build_oauth2_scheme(self):
        """Test building an OAuth2 SecurityScheme."""
        scheme = SecuritySchemeBuilder("oauth2").flow("client_credentials").token_url("https://example.com/token").scopes(["read", "write"]).build()
        assert scheme.type == "oauth2"
        assert scheme.flow == "client_credentials"
        assert scheme.tokenUrl == "https://example.com/token"
        assert scheme.scopes == ["read", "write"]


class TestAgentSkillBuilder:
    """Tests for AgentSkillBuilder."""

    def test_build_skill(self):
        """Test building an AgentSkill using the builder."""
        skill = (
            AgentSkillBuilder("find_recipe", "Find Recipe", "Find recipes based on ingredients", ["cooking", "recipe"])
            .examples(["I need a recipe for bread"])
            .input_modes(["text/plain"])
            .output_modes(["application/json"])
            .build()
        )
        assert skill.id == "find_recipe"
        assert skill.name == "Find Recipe"
        assert skill.tags == ["cooking", "recipe"]
        assert skill.examples == ["I need a recipe for bread"]
        assert skill.inputModes == ["text/plain"]
        assert skill.outputModes == ["application/json"]


class TestAgentInterfaceBuilder:
    """Tests for AgentInterfaceBuilder."""

    def test_build_interface(self):
        """Test building an AgentInterface using the builder."""
        interface = (
            AgentInterfaceBuilder("jsonrpc", ["text/plain", "application/json"], ["text/plain", "application/json"])
            .additional_interface("http", "https://example.com/api")
            .additional_interface("grpc", "https://example.com:443")
            .build()
        )
        assert interface.preferredTransport == "jsonrpc"
        assert interface.defaultInputModes == ["text/plain", "application/json"]
        assert len(interface.additionalInterfaces) == 2
        assert interface.additionalInterfaces[0]["transport"] == "http"
        assert interface.additionalInterfaces[1]["transport"] == "grpc"


class TestAgentCardSignatureBuilder:
    """Tests for AgentCardSignatureBuilder."""

    def test_build_signature(self):
        """Test building an AgentCardSignature using the builder."""
        signature = AgentCardSignatureBuilder().algorithm("RS256").signature("test_signature").jwks_url("https://example.com/.well-known/jwks.json").build()
        assert signature.algorithm == "RS256"
        assert signature.signature == "test_signature"
        assert signature.jwksUrl == "https://example.com/.well-known/jwks.json"


class TestAgentCardSpecBuilder:
    """Tests for AgentCardSpecBuilder."""

    def test_build_card_spec(self):
        """Test building an AgentCardSpec using the builder."""
        capabilities = AgentCapabilitiesBuilder().streaming(True).build()
        security_scheme = SecuritySchemeBuilder("apiKey").location("header").name("X-API-Key").build()
        skill = AgentSkillBuilder("find_recipe", "Find Recipe", "Find recipes", ["cooking"]).build()
        interface = AgentInterfaceBuilder("jsonrpc", ["text/plain"], ["application/json"]).build()

        card_spec = (
            AgentCardSpecBuilder("Recipe Agent", "An AI agent for recipes", "https://recipe-agent.example.com", "1.0.0")
            .with_provider("Culinary AI", "https://culinary-ai.com")
            .with_capabilities(capabilities)
            .add_security_scheme(security_scheme)
            .add_skill(skill)
            .with_interface(interface)
            .documentation_url("https://recipe-agent.example.com/docs")
            .build()
        )

        assert card_spec.name == "Recipe Agent"
        assert card_spec.version == "1.0.0"
        assert card_spec.provider is not None
        assert card_spec.provider.organization == "Culinary AI"
        assert len(card_spec.securitySchemes) == 1
        assert len(card_spec.skills) == 1
        assert card_spec.documentationUrl == "https://recipe-agent.example.com/docs"

    def test_build_card_spec_with_builders(self):
        """Test building AgentCardSpec using nested builders."""
        card_spec = (
            AgentCardSpecBuilder("Recipe Agent", "An AI agent for recipes", "https://recipe-agent.example.com", "1.0.0")
            .with_provider_builder(AgentProviderBuilder("Culinary AI", "https://culinary-ai.com").build())
            .with_capabilities_builder(AgentCapabilitiesBuilder().streaming(True))
            .add_security_scheme_builder(SecuritySchemeBuilder("apiKey").location("header").name("X-API-Key"))
            .add_skill_builder(AgentSkillBuilder("find_recipe", "Find Recipe", "Find recipes", ["cooking"]))
            .with_interface_builder(AgentInterfaceBuilder("jsonrpc", ["text/plain"], ["application/json"]))
            .build()
        )

        assert card_spec.name == "Recipe Agent"
        assert len(card_spec.securitySchemes) == 1
        assert len(card_spec.skills) == 1

    def test_build_card_spec_missing_interface(self):
        """Test that building AgentCardSpec without interface raises error."""
        builder = AgentCardSpecBuilder("Test Agent", "A test agent", "https://test.com", "1.0.0")
        with pytest.raises(ValueError, match="AgentInterface is required"):
            builder.build()


class TestAgentBuilder:
    """Tests for AgentBuilder."""

    def test_build_agent(self):
        """Test building an Agent using the builder."""
        capabilities = AgentCapabilitiesBuilder().streaming(True).build()
        security_scheme = SecuritySchemeBuilder("apiKey").location("header").name("X-API-Key").build()
        skill = AgentSkillBuilder("skill1", "Skill 1", "First skill", ["test"]).build()
        interface = AgentInterfaceBuilder("jsonrpc", ["text/plain"], ["application/json"]).build()

        card_spec = (
            AgentCardSpecBuilder("Test Agent", "A test agent", "https://test.com", "1.0.0")
            .with_capabilities(capabilities)
            .add_security_scheme(security_scheme)
            .add_skill(skill)
            .with_interface(interface)
            .build()
        )

        agent = (
            AgentBuilder("Test Agent", "A test agent", "1.0.0", "Test Provider")
            .with_tags(["test", "agent"])
            .with_location("https://test.com/api", "api_endpoint")
            .with_capabilities(capabilities)
            .with_auth_schemes([security_scheme])
            .with_skills([skill])
            .with_agent_card(card_spec)
            .public(True)
            .active(True)
            .build()
        )

        assert agent.name == "Test Agent"
        assert agent.tags == ["test", "agent"]
        assert agent.is_public is True
        assert agent.is_active is True
        assert agent.agent_card == card_spec
        assert agent.skills == [skill]
