#!/usr/bin/env python3
"""
Basic A2A SDK Usage Example (Fixed)

This example demonstrates basic usage of the A2A Python SDK for:
- Connecting to the registry with OAuth
- Performing read operations (list, search, stats)
- Understanding role-based access control
"""

import os
from a2a_reg_sdk import A2AClient


def main():
    print("🚀 Basic A2A SDK Usage Example")
    print("=" * 40)

    # Initialize the client with OAuth credentials
    client_id = os.getenv("A2A_REG_CLIENT_ID")
    client_secret = os.getenv("A2A_REG_CLIENT_SECRET")
    registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")

    if not client_id or not client_secret:
        print("❌ Missing OAuth credentials!")
        print("Please set the following environment variables:")
        print("  export A2A_REG_CLIENT_ID='your-client-id'")
        print("  export A2A_REG_CLIENT_SECRET='your-client-secret'")
        return

    print("📡 Connecting to registry: {registry_url}")
    print("👤 Using client ID: {client_id}")

    # Initialize the client with READ scope for basic operations
    # Note: Regular users with "User" role can only request "read" scope
    # For publishing agents, you need "CatalogManager" or "Administrator" role
    client = A2AClient(registry_url=registry_url, client_id=client_id, client_secret=client_secret, scope="read")  # User role only allows read operations

    # Authenticate with OAuth
    try:
        print("🔐 Authenticating with OAuth...")
        client.authenticate()
        print("✓ OAuth authentication successful")
    except Exception as e:
        print(f"✗ OAuth authentication failed: {e}")
        return

    print("✓ Client initialized and authenticated successfully")
    print()

    try:
        # List public agents (read operation)
        print("📋 Listing public agents...")
        agents_response = client.list_agents(page=1, limit=10)
        agents = agents_response.get("items", [])
        print("✓ Found {len(agents)} public agents")

        if agents:
            print("   Sample agents:")
            for agent in agents[:3]:  # Show first 3 agents
                print("   - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')[:8]}...)")

        print()

        # Test individual agent access
        if agents:
            print("🔍 Testing agent access...")
            try:
                first_agent = agents[0]
                agent_details = client.get_agent(first_agent["id"])
                print(f"✓ Successfully accessed agent: {agent_details.name}")
                print(f"  - Version: {agent_details.version}")
                print(f"  - Public: {'Yes' if agent_details.is_public else 'No'}")
                print(f"  - Active: {'Yes' if agent_details.is_active else 'No'}")
            except Exception as e:
                print(f"ℹ️  Agent access test: {e}")

        print()

        # Note: Search endpoint requires different authentication
        print("📊 Search functionality requires elevated permissions")

        print()

        # Note: Publishing, updating, and deleting agents require write permissions
        # which are only available to users with "CatalogManager" or "Administrator" roles
        print("ℹ️  Note: Write operations (publish, update, delete) require elevated permissions")
        print("   Users with 'User' role can only perform read operations")
        print("   To publish agents, you need 'CatalogManager' or 'Administrator' role")

    except Exception as e:
        print(f"✗ Operation failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close the client
        print()
        print("🔚 Closing client connection...")
        client.close()
        print("✓ Client closed successfully")

    print()
    print("✅ Basic usage example completed successfully!")


if __name__ == "__main__":
    main()
