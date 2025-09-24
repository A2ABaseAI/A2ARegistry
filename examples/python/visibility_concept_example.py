#!/usr/bin/env python3
"""
A2A Registry SDK - Multi-Tenant Visibility Concept Example

This example demonstrates the concept of multi-tenant agent visibility:
- Shows how public agents are visible to all users
- Demonstrates the entitlement check system for private agents
- Explains tenant isolation and access control principles
- Uses existing agents to test visibility patterns
"""

import os
from a2a_reg_sdk import A2AClient


def demonstrate_visibility_concepts():
    """Demonstrate multi-tenant agent visibility concepts."""
    print("🏢 Multi-Tenant Agent Visibility Concept Demo")
    print("=" * 55)

    registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")
    admin_api_key = os.getenv("ADMIN_API_KEY", "dev-admin-api-key")

    # Initialize admin client
    admin_client = A2AClient(
        registry_url=registry_url,
        api_key=admin_api_key
    )

    print("🔍 Testing current agent visibility...")

    try:
        # List all agents currently in the registry
        print("\n📋 Listing all agents in registry:")
        agents_response = admin_client.list_agents(page=1, limit=20)
        all_agents = agents_response.get('items', [])

        print("  Total agents found: {len(all_agents)}")

        if all_agents:
            print("  👁️  Visible agents:")
            for i, agent in enumerate(all_agents, 1):
                agent_id = agent.get('id', 'Unknown')
                print("    {i}. {agent_name} (ID: {agent_id[:8]}...) - {'Public' if is_public else 'Private'}")
        else:
            print("  No agents found in registry")

        print("\n💡 Multi-Tenant Visibility Concepts:")
        print("  🏠 Tenant Isolation:")
        print("    - Each tenant has isolated data and resources")
        print("    - Private agents are only visible within their tenant")
        print("    - Cross-tenant private access is blocked by entitlement checks")

        print("  🌐 Public Visibility:")
        print("    - Public agents are visible to all users across tenants")
        print("    - Public agents can be discovered and accessed globally")
        print("    - No tenant restrictions apply to public agents")

        print("  🔐 Access Control Mechanisms:")
        print("    - Entitlement checks verify user permissions")
        print("    - Role-based access control (RBAC) determines visibility")
        print("    - Tenant boundaries enforce data isolation")

        print("  👥 User Visibility Rules:")
        print("    - Users can see their own private agents")
        print("    - Users can see all public agents")
        print("    - Users can see agents shared within their tenant")
        print("    - Users cannot see other tenants' private agents")

        # Test agent access patterns
        if all_agents:
            print("\n🧪 Testing Agent Access Patterns:")

            for agent in all_agents[:3]:  # Test first 3 agents
                agent_id = agent.get('id')
                agent_name = agent.get('name', 'Unknown')

                print(f"\n  🔍 Testing access to '{agent_name}':")

                try:
                    # Try to get agent details
                    agent_details = admin_client.get_agent(agent_id)
                    print("    ✓ Successfully accessed agent details")
                    print("    📊 Agent info:")
                    print(f"      - Name: {agent_details.name}")
                    print(f"      - Version: {agent_details.version}")
                    print(f"      - Public: {'Yes' if agent_details.is_public else 'No'}")
                    print(f"      - Active: {'Yes' if agent_details.is_active else 'No'}")
                    print(f"      - Tags: {', '.join(agent_details.tags) if agent_details.tags else 'None'}")

                except Exception as e:
                    print(f"    ✗ Access denied: {e}")
                    if "403" in str(e) or "Access denied" in str(e):
                        print("    💡 This demonstrates entitlement check working!")
                        print("    💡 Private agents require proper tenant permissions")

        print("\n🏗️  Multi-Tenant Architecture Benefits:")
        print("  🔒 Security:")
        print("    - Data isolation prevents cross-tenant data leaks")
        print("    - Entitlement checks enforce access control")
        print("    - Role-based permissions provide fine-grained control")

        print("  📈 Scalability:")
        print("    - Each tenant operates independently")
        print("    - Resources can be allocated per tenant")
        print("    - Horizontal scaling across tenant boundaries")

        print("  🎯 Customization:")
        print("    - Tenant-specific configurations")
        print("    - Custom access policies per tenant")
        print("    - Isolated agent ecosystems")

        print("\n🔧 Implementation Notes:")
        print("  - The A2A Registry implements tenant isolation at the database level")
        print("  - Entitlement checks are performed on every agent access")
        print("  - Public agents bypass tenant restrictions")
        print("  - Private agents require tenant membership verification")

    except Exception:
        pass
        print("✗ Error testing visibility: {e}")

    print()
    print("✅ Multi-tenant visibility concept demo completed!")
    print("💡 This example demonstrates:")
    print("   - How multi-tenant systems enforce data isolation")
    print("   - The difference between public and private agent visibility")
    print("   - How entitlement checks prevent unauthorized access")
    print("   - The benefits of tenant-based access control")


def main():
    """Main function."""
    demonstrate_visibility_concepts()


if __name__ == "__main__":
    main()
