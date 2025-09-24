"""
A2A Agent Publisher

High-level publisher class for easier agent publishing and management.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import yaml
import json

from .client import A2AClient
from .models import (
    Agent,
    AgentBuilder,
    AgentCapabilitiesBuilder,
    AuthSchemeBuilder,
    AgentTeeDetailsBuilder,
    AgentSkillsBuilder,
    InputSchemaBuilder,
    OutputSchemaBuilder,
    AgentCard,
)
from .exceptions import ValidationError


class AgentPublisher:
    """High-level agent publisher for the A2A registry."""

    def __init__(self, client: A2AClient):
        """
        Initialize the publisher with an A2A client.

        Args:
            client: Authenticated A2AClient instance
        """
        self.client = client

    def load_agent_from_file(self, file_path: Union[str, Path]) -> Agent:
        """
        Load agent configuration from a file.

        Args:
            file_path: Path to YAML or JSON configuration file

        Returns:
            Agent object

        Raises:
            ValidationError: If file cannot be loaded or parsed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            return Agent.from_dict(data)
        except Exception as e:
            raise ValidationError(f"Failed to load agent configuration: {e}")

    def validate_agent(self, agent: Agent) -> List[str]:
        """
        Validate an agent configuration.

        Args:
            agent: Agent to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required fields
        if not agent.name:
            errors.append("Agent name is required")
        if not agent.description:
            errors.append("Agent description is required")
        if not agent.version:
            errors.append("Agent version is required")
        if not agent.provider:
            errors.append("Agent provider is required")

        # Validate capabilities if present
        if agent.capabilities:
            # protocols and supported_formats are always lists due to default_factory=list
            # No need to validate their types
            pass

        # Validate auth schemes
        for i, scheme in enumerate(agent.auth_schemes):
            if not scheme.type:
                errors.append(f"Auth scheme {i} missing required field: type")
            if scheme.type not in ["api_key", "oauth2", "jwt", "mtls", "bearer"]:
                errors.append(f"Auth scheme {i} has invalid type: {scheme.type}")

        # Validate agent card if present
        if agent.agent_card:
            if not agent.agent_card.name:
                errors.append("Agent card name is required")
            if not agent.agent_card.description:
                errors.append("Agent card description is required")
            if not agent.agent_card.version:
                errors.append("Agent card version is required")
            if not agent.agent_card.author:
                errors.append("Agent card author is required")

        return errors

    def publish(self, agent: Agent, validate: bool = True) -> Agent:
        """
        Publish an agent to the registry.

        Args:
            agent: Agent to publish
            validate: Whether to validate the agent before publishing

        Returns:
            Published agent with assigned ID

        Raises:
            ValidationError: If validation fails
            A2AError: If publishing fails
        """
        if validate:
            errors = self.validate_agent(agent)
            if errors:
                raise ValidationError(f"Agent validation failed: {'; '.join(errors)}")

        return self.client.publish_agent(agent)

    def publish_from_file(self, file_path: Union[str, Path], validate: bool = True) -> Agent:
        """
        Load and publish an agent from a configuration file.

        Args:
            file_path: Path to agent configuration file
            validate: Whether to validate the agent before publishing

        Returns:
            Published agent with assigned ID
        """
        agent = self.load_agent_from_file(file_path)
        return self.publish(agent, validate)

    def update(self, agent_id: str, agent: Agent, validate: bool = True) -> Agent:
        """
        Update an existing agent.

        Args:
            agent_id: ID of the agent to update
            agent: Updated agent data
            validate: Whether to validate the agent before updating

        Returns:
            Updated agent
        """
        if validate:
            errors = self.validate_agent(agent)
            if errors:
                raise ValidationError(f"Agent validation failed: {'; '.join(errors)}")

        return self.client.update_agent(agent_id, agent)

    def create_sample_agent(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        provider: str = "my-org",
        api_url: Optional[str] = None,
    ) -> Agent:
        """
        Create a sample agent configuration.

        Args:
            name: Agent name
            description: Agent description
            version: Agent version
            provider: Agent provider
            api_url: API base URL

        Returns:
            Sample agent configuration
        """
        capabilities = (
            AgentCapabilitiesBuilder()
            .protocols(["http", "websocket"])
            .supported_formats(["json"])
            .max_request_size(1048576)
            .max_concurrent_requests(10)
            .a2a_version("1.0")
            .build()
        )

        auth_schemes = [AuthSchemeBuilder("api_key").description("API key authentication").required(True).header_name("X-API-Key").build()]

        tee_details = AgentTeeDetailsBuilder().enabled(False).build()

        # Create input and output schemas using builders
        input_schema = (
            InputSchemaBuilder()
            .add_string_property("message", "Message to process", required=True)
            .add_object_property("context", {}, "Request context")
            .build()
        )
        output_schema = (
            OutputSchemaBuilder()
            .add_string_property("response", "Agent response", required=True)
            .add_number_property("confidence", "Response confidence score", required=True, minimum=0.0, maximum=1.0)
            .build()
        )

        skills = (
            AgentSkillsBuilder()
            .input_schema(input_schema)
            .output_schema(output_schema)
            .examples(["Input: {'message': 'Hello'} -> Output: {'response': 'Hi there!', 'confidence': 0.95}"])
            .build()
        )

        agent_card = AgentCard(
            name=name,
            description=description,
            version=version,
            author=provider,
            api_base_url=api_url,
            capabilities=capabilities,
            auth_schemes=auth_schemes,
            endpoints={
                "chat": "/chat",
                "status": "/status",
                "capabilities": "/capabilities",
            },
            skills=skills,
        )

        return (
            AgentBuilder(name, description, version, provider)
            .with_tags(["ai", "assistant", "sample"])
            .with_location(api_url or f"https://{provider}.com/api/agent", "api_endpoint")
            .with_capabilities(capabilities)
            .with_auth_schemes(auth_schemes)
            .with_tee_details(tee_details)
            .with_skills(skills)
            .with_agent_card(agent_card)
            .public(True)
            .active(True)
            .build()
        )

    def save_agent_config(self, agent: Agent, file_path: Union[str, Path], format: str = "yaml") -> None:
        """
        Save agent configuration to a file.

        Args:
            agent: Agent to save
            file_path: Output file path
            format: File format ("yaml" or "json")
        """
        file_path = Path(file_path)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if format.lower() == "yaml":
                    yaml.dump(agent.to_dict(), f, default_flow_style=False, indent=2)
                else:
                    json.dump(agent.to_dict(), f, indent=2)
        except Exception as e:
            raise ValidationError(f"Failed to save agent configuration: {e}")


# Convenience functions


def create_quick_publisher(
    registry_url: str = "http://localhost:8000",
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> AgentPublisher:
    """
    Create a publisher with authentication.

    Args:
        registry_url: Registry URL
        client_id: OAuth client ID
        client_secret: OAuth client secret

    Returns:
        Configured and authenticated AgentPublisher
    """
    client = A2AClient(registry_url, client_id, client_secret)
    if client_id and client_secret:
        client.authenticate()
    return AgentPublisher(client)


def publish_agent_from_dict(
    agent_data: Dict[str, Any],
    registry_url: str = "http://localhost:8000",
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> Agent:
    """
    Quick function to publish an agent from a dictionary.

    Args:
        agent_data: Agent configuration as dictionary
        registry_url: Registry URL
        client_id: OAuth client ID
        client_secret: OAuth client secret

    Returns:
        Published agent
    """
    publisher = create_quick_publisher(registry_url, client_id, client_secret)
    agent = Agent.from_dict(agent_data)
    return publisher.publish(agent)
