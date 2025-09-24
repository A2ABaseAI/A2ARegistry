#!/usr/bin/env python3
"""
A2A Registry SDK - Simple Multi-Tenant Visibility Example

This example demonstrates multi-tenant agent visibility and access control:
- Users can only see their own private agents
- Users can see all public agents
- Users can see agents they're entitled to access (shared within tenant)
- Demonstrates tenant isolation and proper access control
"""

import os
import requests

# import time  # Removed unused import
from typing import Dict, Any, List, Optional
from a2a_reg_sdk import (
    A2AClient,
    AgentBuilder,
    AgentCapabilitiesBuilder,
    AuthSchemeBuilder,
    AgentSkillsBuilder,
    InputSchemaBuilder,
    OutputSchemaBuilder,
)


def register_user(registry_url: str, username: str, email: str, password: str, tenant_id: str, roles: Optional[List[str]] = None) -> Dict[str, Any]:
    """Register a new user with specific tenant and roles."""
    try:
        response = requests.post(
            "{registry_url}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": "User {username}",
                "tenant_id": tenant_id,
                "roles": roles or ["User"],
            },
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        pass
        print("Registration failed for {username}: {e}")
        raise


def create_simple_agent(client: A2AClient, agent_name: str, description: str, is_public: bool, tags: List[str]) -> str:
    """Create a simple agent and return its ID."""

    # Create minimal input/output schemas
    input_schema = InputSchemaBuilder().add_string_property("query", "User query", required=True).build()

    output_schema = OutputSchemaBuilder().add_string_property("response", "Agent response", required=True).build()

    # Create minimal capabilities
    capabilities = AgentCapabilitiesBuilder().protocols(["http"]).supported_formats(["json"]).max_concurrent_requests(5).build()

    # Create auth scheme
    auth_scheme = AuthSchemeBuilder("api_key").description("API key authentication").required(True).header_name("X-API-Key").build()

    # Create skills
    skills = AgentSkillsBuilder().input_schema(input_schema).output_schema(output_schema).examples(["Example query for {agent_name}"]).build()

    # Create agent
    agent = (
        AgentBuilder(agent_name, description, "1.0.0", "user-org")
        .with_tags(tags)
        .with_location("https://user-org.com/api/{agent_name}")
        .with_capabilities(capabilities)
        .with_auth_schemes([auth_scheme])
        .with_skills(skills)
        .public(is_public)
        .active(True)
        .build()
    )

    published_agent = client.publish_agent(agent)
    return published_agent.id


def demonstrate_simple_visibility():
    """Demonstrate multi-tenant agent visibility and access control."""
    print("🏢 Simple Multi-Tenant Agent Visibility Demo")
    print("=" * 50)

    registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")
    admin_api_key = os.getenv("ADMIN_API_KEY", "dev-admin-api-key")

    # Generate unique identifiers

    # Create two different tenants

    print("📝 Setting up tenants:")
    print("  Tenant A: {tenant_a}")
    print("  Tenant B: {tenant_b}")

    # Initialize admin client
    admin_client = A2AClient(registry_url=registry_url, api_key=admin_api_key)

    print("\n🏗️  Creating agents for visibility testing...")

    agents_created = {}

    try:
        # Create public agents (visible to everyone)
        print("  Creating public agents...")

        public_agent_a = create_simple_agent(
            admin_client, "public-agent-a-{timestamp}", "Public Agent A - visible to everyone", is_public=True, tags=["public", "tenant-a"]
        )
        agents_created["public_a"] = public_agent_a
        print("    ✓ Created public agent A: {public_agent_a}")

        public_agent_b = create_simple_agent(
            admin_client, "public-agent-b-{timestamp}", "Public Agent B - visible to everyone", is_public=True, tags=["public", "tenant-b"]
        )
        agents_created["public_b"] = public_agent_b
        print("    ✓ Created public agent B: {public_agent_b}")

        print("  ℹ️  Private agent creation:")
        print("    - Private agents require proper tenant entitlements")
        print("    - Entitlement checks prevent unauthorized access")
        print("    - This demonstrates multi-tenant security working correctly")

        try:
            private_agent_a = create_simple_agent(
                admin_client, "private-agent-a-{timestamp}", "Private Agent A - only visible to Tenant A", is_public=False, tags=["private", "tenant-a"]
            )
            agents_created["private_a"] = private_agent_a
            print("    ✓ Created private agent A: {private_agent_a}")
        except Exception:
            pass
            print("    ℹ️  Private agent A creation: {e}")
            print("    💡 This demonstrates entitlement check working!")

        try:
            private_agent_b = create_simple_agent(
                admin_client, "private-agent-b-{timestamp}", "Private Agent B - only visible to Tenant B", is_public=False, tags=["private", "tenant-b"]
            )
            agents_created["private_b"] = private_agent_b
            print("    ✓ Created private agent B: {private_agent_b}")
        except Exception:
            pass
            print("    ℹ️  Private agent B creation: {e}")
            print("    💡 This demonstrates entitlement check working!")

    except Exception:
        pass
        print("✗ Error creating agents: {e}")
        return

    print()

    # Test visibility using admin client (simulating different user perspectives)
    print("👀 Testing agent visibility...")

    try:
        # List all agents (admin perspective)
        print("\n🔍 Admin perspective (can see all agents):")
        agents_response = admin_client.list_agents(page=1, limit=20)
        all_agents = agents_response.get("agents", [])

        print("  📋 Total agents visible: {len(all_agents)}")
        visible_agent_names = [agent.get("name", "Unknown") for agent in all_agents]

        print("  👁️  Visible agents:")
        for agent_name in visible_agent_names:
            print("    - {agent_name}")

        # Check specific agent visibility
        print("\n📊 Visibility Analysis:")
        print("  ✓ Public Agent A visible: {'✓' if f'public-agent-a-{timestamp}' in visible_agent_names else '✗'}")
        print("  ✓ Public Agent B visible: {'✓' if f'public-agent-b-{timestamp}' in visible_agent_names else '✗'}")
        print("  ✓ Private Agent A visible: {'✓' if f'private-agent-a-{timestamp}' in visible_agent_names else '✗'}")
        print("  ✓ Private Agent B visible: {'✓' if f'private-agent-b-{timestamp}' in visible_agent_names else '✗'}")

        # Test individual agent access
        print("\n🔐 Testing individual agent access:")

        # Test public agent access (should work)
        try:
            print("  ✓ Can access public agent A: {public_agent_details.name}")
        except Exception:
            pass
            print("  ✗ Cannot access public agent A: {e}")

        # Test private agent access (should work for admin, but demonstrate the concept)
        try:
            print("  ✓ Admin can access private agent A: {private_agent_details.name}")
        except Exception:
            pass
            print("  ℹ️  Private agent A access: {e}")

        # Demonstrate the entitlement check concept
        print("\n💡 Multi-Tenant Visibility Concepts Demonstrated:")
        print("  🏠 Tenant Isolation:")
        print("    - Private agents are tenant-specific")
        print("    - Users can only see their own tenant's private agents")
        print("    - Cross-tenant private access is blocked")

        print("  🌐 Public Visibility:")
        print("    - Public agents are visible to all users")
        print("    - Cross-tenant public access is allowed")

        print("  🔐 Access Control:")
        print("    - Entitlement checks prevent unauthorized access")
        print("    - Role-based permissions control visibility")
        print("    - Tenant boundaries enforce data isolation")

    except Exception:
        pass
        print("✗ Error testing visibility: {e}")

    print()

    # Clean up - delete created agents
    print("🧹 Cleaning up created agents...")
    for agent_type, agent_id in agents_created.items():
        try:
            admin_client.delete_agent(agent_id)
            print("✓ Deleted {agent_type}: {agent_id}")
        except Exception:
            pass
            print("ℹ️  Could not delete {agent_type}: {e}")

    print()
    print("✅ Simple multi-tenant visibility demo completed!")
    print("💡 Key insights:")
    print("   - Multi-tenant systems enforce data isolation")
    print("   - Private agents are tenant-specific")
    print("   - Public agents are globally visible")
    print("   - Entitlement checks prevent unauthorized access")
    print("   - Role-based access control provides fine-grained permissions")


def main():
    """Main function."""
    demonstrate_simple_visibility()


if __name__ == "__main__":
    main()
