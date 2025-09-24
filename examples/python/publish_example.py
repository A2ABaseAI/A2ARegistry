#!/usr/bin/env python3
"""
A2A Registry SDK - Agent Publishing Example

This example demonstrates how to publish an agent to the A2A Registry using:
- OAuth authentication with write permissions
- Agent builders for creating complex agent definitions
- Input/output schema builders for detailed skill specifications
"""

import os
from a2a_reg_sdk import (
    A2AClient,
    AgentBuilder,
    AgentCapabilitiesBuilder,
    AuthSchemeBuilder,
    AgentSkillsBuilder,
    InputSchemaBuilder,
    OutputSchemaBuilder,
)


def create_sample_agent():
    """Create a sample agent using SDK builders."""

    # Create input schema for the agent's main skill
    input_schema = (
        InputSchemaBuilder()
        .add_string_property("query", "The user's question or request", required=True)
        .add_string_property("context", "Additional context for the request", required=False)
        .add_object_property("user_info", {"user_id": {"type": "string"}, "preferences": {"type": "object"}}, "User information and preferences")
        .add_array_property("documents", {"type": "string"}, "List of document references")
        .build()
    )

    # Create output schema for the agent's response
    output_schema = (
        OutputSchemaBuilder()
        .add_string_property("response", "The agent's response to the user", required=True)
        .add_object_property(
            "metadata",
            {"confidence": {"type": "number"}, "sources": {"type": "array", "items": {"type": "string"}}, "processing_time": {"type": "number"}},
            "Response metadata",
        )
        .add_array_property("suggestions", {"type": "string"}, "Follow-up suggestions")
        .build()
    )

    # Create agent capabilities
    capabilities = (
        AgentCapabilitiesBuilder()
        .protocols(["http", "https"])
        .supported_formats(["json", "xml"])
        .max_concurrent_requests(10)
        .max_request_size(1024 * 1024)  # 1MB max request size
        .a2a_version("1.0.0")
        .build()
    )

    # Create authentication scheme
    auth_scheme = AuthSchemeBuilder("api_key").description("API key authentication for secure access").required(True).header_name("X-API-Key").build()

    # Create agent skills (single skill with input/output schemas)
    skills = (
        AgentSkillsBuilder()
        .input_schema(input_schema)
        .output_schema(output_schema)
        .examples(["What is the weather like today?", "Can you summarize this document for me?", "How do I implement authentication in my app?"])
        .build()
    )

    # Create the complete agent
    agent = (
        AgentBuilder("ai-assistant", "Intelligent AI Assistant for Q&A and Document Processing", "1.0.0", "ai-org")
        .with_tags(["ai", "assistant", "qa", "nlp", "document-processing"])
        .with_location("https://ai-org.com/api/assistant")
        .with_capabilities(capabilities)
        .with_auth_schemes([auth_scheme])
        .with_skills(skills)
        .public(True)
        .active(True)
        .build()
    )

    return agent


def main():
    """Main function to demonstrate agent publishing."""
    print("🚀 A2A Registry SDK - Agent Publishing Example")
    print("=" * 50)

    # Get admin API key from environment for generating write API key
    admin_api_key = os.getenv("ADMIN_API_KEY", "dev-admin-api-key")
    registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")

    if not admin_api_key:
        print("❌ Missing admin API key!")
        print("Please set the following environment variable:")
        print("  export ADMIN_API_KEY='your-admin-api-key'")
        print("\nNote: Admin API key is needed to generate write API keys")
        return

    print("📡 Connecting to registry: {registry_url}")
    print("🔑 Using admin API key for key generation")

    # Initialize admin client for API key generation
    admin_client = A2AClient(registry_url=registry_url, api_key=admin_api_key)

    try:
        # Generate a write API key for demonstration
        print("\n🔑 Generating write API key for demonstration...")
        write_key, write_key_info = admin_client.generate_api_key(scopes=["read", "write"], expires_days=1)  # Short expiration for demo
        print("✓ Write API key generated: {write_key_info.get('key_id', 'N/A')}")
        print("ℹ️  Note: Generated API keys are not yet integrated with main auth system")
        print("   Using admin API key directly for agent publishing...")

        # Use admin client directly for publishing (since generated keys aren't integrated yet)
        write_client = admin_client

        # Create the agent
        print("\n🏗️  Creating agent definition...")
        agent = create_sample_agent()
        print(f"✓ Agent created: {agent.name} v{agent.version}")
        print(f"  Description: {agent.description}")
        print(f"  Skills: Input/Output schemas defined with {len(agent.skills.examples)} examples")
        print(f"  Tags: {', '.join(agent.tags)}")

        # Publish the agent using the write API key
        print("\n📤 Publishing agent to registry...")
        published_agent = write_client.publish_agent(agent)
        print("✓ Agent published successfully!")
        print(f"  Agent ID: {published_agent.id}")
        print(f"  Version: {published_agent.version}")

        # Verify the agent was published
        print("\n🔍 Verifying agent publication...")
        agent_details = write_client.get_agent(published_agent.id)
        print("✓ Agent retrieved from registry")
        print(f"  Name: {agent_details.name}")
        print(f"  Status: {'Active' if agent_details.is_active else 'Inactive'}")
        print(f"  Public: {'Yes' if agent_details.is_public else 'No'}")

        # List agents to show our published agent
        print("\n📋 Listing published agents...")
        agents_response = write_client.list_agents(page=1, limit=10)
        agents = agents_response.get("agents", [])
        print("✓ Found {len(agents)} agents in registry")

        # Show our agent in the list
        our_agent = next((a for a in agents if a.get("id") == published_agent.id), None)
        if our_agent:
            print("✓ Our agent found in registry: {our_agent.get('name')}")

        # Clean up - revoke the generated API key
        print("\n🧹 Cleaning up generated API key...")
        try:
            admin_client.revoke_api_key(write_key_info.get("key_id"))
            print("✓ Revoked write API key: {write_key_info.get('key_id')}")
        except Exception:
            pass
            print("ℹ️  Could not revoke API key: {e}")

        print("\n✅ Agent publishing example completed successfully!")
        print("🎉 Agent '{agent.name}' is now available in the registry!")
        print("💡 This example demonstrates:")
        print("   - Admin API key generation of write API keys")
        print("   - Agent publishing using admin API key (working approach)")
        print("   - Proper cleanup of generated resources")
        print("   - Note: Generated API keys need backend integration for full functionality")

    except Exception:
        pass
        print("\n❌ Error during agent publishing: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close the client
        print("\n🔚 Closing client connection...")
        admin_client.close()
        print("✓ Client closed successfully")


if __name__ == "__main__":
    main()
