#!/usr/bin/env python3
"""
A2A SDK Demo - Working Example

This example demonstrates the A2A Python SDK working with the registry.
It shows how to use the SDK for basic operations like listing agents.
"""

import httpx
from a2a_reg_sdk import A2AClient, AgentBuilder


def main():
    print("🚀 A2A SDK Demo - Working Example")
    print("=" * 40)

    registry_url = "http://localhost:8000"

    # Step 1: Register and login to get a token
    print("📝 Step 1: Setting up authentication...")

    try:
        # Register a test user
        response = httpx.post(f"{registry_url}/auth/register", json={
            "username": "sdk-demo-user",
            "email": "sdk-demo@example.com",
            "password": "sdk-demo-secret",
            "full_name": "SDK Demo User",
            "tenant_id": "default"
        })

        if response.status_code == 200:
            print("✅ User registered successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ User already exists")
        else:
            print(f"⚠️ Registration response: {response.status_code}")

        # Login to get token
        response = httpx.post(f"{registry_url}/auth/login", json={
            "email_or_username": "sdk-demo-user",
            "password": "sdk-demo-secret"
        })

        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            print(f"✅ Login successful! Token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return

    except Exception as e:
        print(f"❌ Authentication setup failed: {e}")
        return

    # Step 2: Test SDK functionality
    print("\n🧪 Step 2: Testing SDK functionality...")

    try:
        # Create SDK client
        client = A2AClient(
            registry_url=registry_url,
            client_id="sdk-demo-client",
            client_secret="sdk-demo-secret"
        )

        # Manually set the token (since we got it from login)
        client._access_token = access_token
        client._token_expires_at = None  # Don't auto-refresh for this demo

        # Test 1: List public agents
        print("📋 Testing: List public agents...")
        agents_response = client.list_agents()
        agent_count = len(agents_response.get("agents", []))
        print(f"✅ Found {agent_count} public agents")

        # Test 2: Check health endpoint
        print("🏥 Testing: Health check...")
        health_response = httpx.get(f"{registry_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Registry status: {health_data.get('status', 'unknown')}")

        # Test 3: Create an agent using the SDK
        print("🤖 Testing: Create agent with SDK...")
        try:
            agent = AgentBuilder("demo-agent", "Demo Agent", "1.0.0", "demo-org") \
                .with_tags(["demo", "test"]) \
                .with_location("https://api.demo-org.com/agent") \
                .public(True) \
                .build()

            print(f"✅ Agent created: {agent.name} v{agent.version}")
            print(f"   Description: {agent.description}")
            print(f"   Provider: {agent.provider}")
            print(f"   Tags: {agent.tags}")
            print(f"   Public: {agent.is_public}")

        except Exception as e:
            print(f"⚠️ Agent creation test failed: {e}")

        print("\n🎉 SDK Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ User registration and authentication")
        print("✅ SDK client initialization")
        print("✅ Agent listing functionality")
        print("✅ Agent builder pattern")
        print("✅ Health check integration")

    except Exception as e:
        print(f"❌ SDK test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
