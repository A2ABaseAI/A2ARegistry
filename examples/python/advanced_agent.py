#!/usr/bin/env python3
"""
Advanced A2A Agent Example

This example demonstrates creating a sophisticated agent with:
- Complex capabilities and skills
- Multiple authentication schemes
- TEE (Trusted Execution Environment) details
- Comprehensive agent card metadata
"""

import os
from a2a_sdk import (
    A2AClient,
    AgentBuilder,
    AgentCapabilities,
    AuthScheme,
    AgentTeeDetails,
    AgentSkills,
    AgentCard,
)


def create_advanced_agent():
    """Create an advanced agent with comprehensive configuration."""

    # Define sophisticated capabilities
    capabilities = AgentCapabilities(
        protocols=["http", "websocket", "grpc"],
        supported_formats=["json", "xml", "protobuf", "msgpack"],
        max_request_size=10485760,  # 10MB
        max_concurrent_requests=50,
        a2a_version="1.0",
    )

    # Define multiple authentication schemes
    auth_schemes = [
        AuthScheme(
            type="api_key",
            description="API key for basic authentication",
            required=True,
            header_name="X-API-Key",
        ),
        AuthScheme(
            type="oauth2",
            description="OAuth 2.0 for advanced authentication",
            required=False,
        ),
        AuthScheme(
            type="jwt",
            description="JWT tokens for stateless authentication",
            required=False,
            header_name="Authorization",
        ),
    ]

    # Define TEE details for secure execution
    tee_details = AgentTeeDetails(
        enabled=True,
        provider="Intel SGX",
        attestation="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    )

    # Define agent skills with detailed schemas
    skills = AgentSkills(
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query or command",
                },
                "context": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "preferences": {"type": "object"},
                    },
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 4096,
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0,
                        },
                        "top_p": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    },
                },
            },
            "required": ["query"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "response": {"type": "string", "description": "Generated response"},
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score",
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "tokens_used": {"type": "integer"},
                        "processing_time_ms": {"type": "integer"},
                        "model_version": {"type": "string"},
                    },
                },
                "alternatives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Alternative responses",
                },
            },
            "required": ["response", "confidence"],
        },
        examples=[
            "Query: 'Explain quantum computing' -> Response: 'Quantum computing is...', Confidence: 0.92",
            "Query: 'Translate hello to French' -> Response: 'Bonjour', Confidence: 0.98",
            "Query: 'Summarize this document' -> Response: 'The document discusses...', Confidence: 0.85",
        ],
    )

    # Create comprehensive agent card
    agent_card = AgentCard(
        name="advanced-ai-assistant",
        description="An advanced AI assistant with multi-modal capabilities and secure execution",
        version="2.1.0",
        author="Advanced AI Corp",
        api_base_url="https://api.advanced-ai.com/v2",
        capabilities=capabilities,
        auth_schemes=auth_schemes,
        endpoints={
            "chat": "/chat",
            "completion": "/completion",
            "embedding": "/embedding",
            "status": "/status",
            "health": "/health",
            "metrics": "/metrics",
            "capabilities": "/capabilities",
        },
        skills=skills,
    )

    # Build the complete agent
    agent = (
        AgentBuilder(
            name="advanced-ai-assistant",
            description="An advanced AI assistant with multi-modal capabilities, secure TEE execution, and comprehensive API support",
            version="2.1.0",
            provider="advanced-ai-corp",
        )
        .with_tags(
            [
                "ai",
                "assistant",
                "nlp",
                "multimodal",
                "secure",
                "enterprise",
                "conversation",
                "completion",
                "embedding",
                "tee",
            ]
        )
        .with_location("https://api.advanced-ai.com/v2/agent", "api_endpoint")
        .with_capabilities(capabilities)
        .with_auth_schemes(auth_schemes)
        .with_tee_details(tee_details)
        .with_skills(skills)
        .with_agent_card(agent_card)
        .public(True)
        .active(True)
        .build()
    )

    return agent


def main():
    # Initialize client
    client = A2AClient(
        registry_url="http://localhost:8000",
        client_id=os.getenv("A2A_CLIENT_ID"),
        client_secret=os.getenv("A2A_CLIENT_SECRET"),
    )

    try:
        # Authenticate
        client.authenticate()
        print("✓ Authentication successful")

        # Create advanced agent
        advanced_agent = create_advanced_agent()
        print(f"✓ Created advanced agent: {advanced_agent.name}")
        print(f"  - Tags: {', '.join(advanced_agent.tags)}")
        print(f"  - Protocols: {', '.join(advanced_agent.capabilities.protocols)}")
        print(f"  - Auth schemes: {len(advanced_agent.auth_schemes)}")
        print(f"  - TEE enabled: {advanced_agent.tee_details.enabled}")
        print(f"  - Skills examples: {len(advanced_agent.skills.examples)}")

        # Publish the agent
        published_agent = client.publish_agent(advanced_agent)
        print(f"✓ Advanced agent published with ID: {published_agent.id}")

        # Retrieve and display the agent card
        agent_card = client.get_agent_card(published_agent.id)
        print(f"✓ Retrieved agent card:")
        print(f"  - API Base URL: {agent_card.api_base_url}")
        print(f"  - Endpoints: {list(agent_card.endpoints.keys())}")
        print(f"  - Max concurrent requests: {agent_card.capabilities.max_concurrent_requests}")

        # Search for advanced features
        search_results = client.search_agents(
            query="advanced AI TEE secure",
            filters={
                "tags": ["enterprise", "secure"],
                "capabilities.protocols": ["grpc"],
            },
            semantic=True,
        )
        print(f"✓ Semantic search found {len(search_results.get('agents', []))} matching agents")

        # Clean up
        client.delete_agent(published_agent.id)
        print("✓ Advanced agent deleted")

    except Exception as e:
        print(f"✗ Operation failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        client.close()


if __name__ == "__main__":
    main()
