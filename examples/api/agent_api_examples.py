#!/usr/bin/env python3
"""
A2A Registry Agent API Examples

This example demonstrates how to interact with the A2A Registry Agent API endpoints:
- Publishing agents (by card data and by URL)
- Retrieving public agents
- Retrieving entitled agents (with authentication)
- Getting individual agent details
- Getting agent cards

Requirements:
- A2A Registry server running on localhost:8000
- Built-in authentication system (automatic user registration and login)
- Agent card data or URLs for publishing

Usage:
    python agent_api_examples.py
"""

import json
import os
import sys
from typing import Dict, Any, Optional

import httpx
from httpx import HTTPError, RequestError


class A2ARegistryClient:
    """Client for interacting with A2A Registry API."""

    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.client = httpx.Client(timeout=30.0)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get headers with authentication if token is provided."""
        headers = {"Content-Type": "application/json"}
        if include_auth and (self.token or self.access_token):
            token = self.token or self.access_token
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get tokens."""
        url = f"{self.base_url}/auth/login"
        payload = {"email_or_username": username, "password": password}

        try:
            response = self.client.post(url, json=payload, headers=self._get_headers(include_auth=False))
            response.raise_for_status()

            result = response.json()

            # Store tokens for future use
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")

            return result
        except HTTPError as e:
            print(f"HTTP Error authenticating user: {e}")
            raise
        except RequestError as e:
            print(f"Request Error authenticating user: {e}")
            raise

    def register_user(
        self, username: str, email: str, password: str, full_name: Optional[str] = None, tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """Register a new user."""
        url = f"{self.base_url}/auth/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "tenant_id": tenant_id,
        }

        try:
            response = self.client.post(url, json=payload, headers=self._get_headers(include_auth=False))
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error registering user: {e}")
            raise
        except RequestError as e:
            print(f"Request Error registering user: {e}")
            raise

    def publish_agent_by_card(self, card_data: Dict[str, Any], public: bool = True) -> Dict[str, Any]:
        """Publish an agent using card data."""
        url = f"{self.base_url}/agents/publish"
        payload = {"card": card_data, "public": public}

        try:
            response = self.client.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error publishing agent: {e}")
            if e.response.status_code == 400:
                print(f"Response: {e.response.text}")
            raise
        except RequestError as e:
            print(f"Request Error publishing agent: {e}")
            raise

    def publish_agent_by_url(self, card_url: str, public: bool = True) -> Dict[str, Any]:
        """Publish an agent using card URL."""
        url = f"{self.base_url}/agents/publish"
        payload = {"cardUrl": card_url, "public": public}

        try:
            response = self.client.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error publishing agent by URL: {e}")
            if e.response.status_code == 400:
                print(f"Response: {e.response.text}")
            raise
        except RequestError as e:
            print(f"Request Error publishing agent by URL: {e}")
            raise

    def get_public_agents(self, top: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Get public agents."""
        url = f"{self.base_url}/agents/public"
        params = {"top": top, "skip": skip}

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting public agents: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting public agents: {e}")
            raise

    def get_entitled_agents(self, top: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Get entitled agents (requires authentication)."""
        url = f"{self.base_url}/agents/entitled"
        params = {"top": top, "skip": skip}

        try:
            response = self.client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting entitled agents: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting entitled agents: {e}")
            raise

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details by ID."""
        url = f"{self.base_url}/agents/{agent_id}"

        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting agent {agent_id}: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting agent {agent_id}: {e}")
            raise

    def get_agent_card(self, agent_id: str) -> Dict[str, Any]:
        """Get agent card by ID."""
        url = f"{self.base_url}/agents/{agent_id}/card"

        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting agent card {agent_id}: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting agent card {agent_id}: {e}")
            raise

    def close(self):
        """Close the HTTP client."""
        self.client.close()


def create_sample_agent_card() -> Dict[str, Any]:
    """Create a sample agent card for testing."""
    return {
        "protocolVersion": "0.3.0",
        "name": "Python API Example Agent",
        "description": "A sample agent created via Python API examples",
        "url": "https://example.com/.well-known/agent-card.json",
        "version": "1.0.0",
        "capabilities": {
            "a2a_version": "0.3.0",
            "supported_protocols": ["text", "json"],
            "text": True,
            "streaming": True,
            "max_concurrent_requests": 10,
        },
        "skills": [
            {
                "name": "text_processing",
                "description": "Process and analyze text content",
                "parameters": {"input_type": "string", "output_type": "string"},
            }
        ],
        "jwks_uri": "https://example.com/.well-known/jwks.json",
    }


def demonstrate_agent_publishing(client: A2ARegistryClient):
    """Demonstrate agent publishing functionality."""
    print("\n" + "=" * 60)
    print("AGENT PUBLISHING EXAMPLES")
    print("=" * 60)

    # Example 1: Publish agent by card data
    print("\n1. Publishing agent by card data...")
    try:
        card_data = create_sample_agent_card()
        result = client.publish_agent_by_card(card_data, public=True)
        print("✓ Agent published successfully!")
        print(f"  Agent ID: {result.get('agentId')}")
        print(f"  Version: {result.get('version')}")
        print(f"  Public: {result.get('public')}")
        print(f"  Signature Valid: {result.get('signatureValid')}")
        return result.get("agentId")
    except Exception as e:
        print(f"✗ Failed to publish agent by card: {e}")
        return None

    # Example 2: Publish agent by URL (commented out as it requires a real URL)
    # print("\n2. Publishing agent by URL...")
    # try:
    #     card_url = "https://example.com/.well-known/agent-card.json"
    #     result = client.publish_agent_by_url(card_url, public=False)
    #     print(f"✓ Agent published from URL successfully!")
    #     print(f"  Agent ID: {result.get('agentId')}")
    #     return result.get('agentId')
    # except Exception as e:
    #     print(f"✗ Failed to publish agent by URL: {e}")
    #     return None


def demonstrate_agent_retrieval(client: A2ARegistryClient, published_agent_id: Optional[str]):
    """Demonstrate agent retrieval functionality."""
    print("\n" + "=" * 60)
    print("AGENT RETRIEVAL EXAMPLES")
    print("=" * 60)

    # Example 1: Get public agents
    print("\n1. Getting public agents...")
    try:
        result = client.get_public_agents(top=10, skip=0)
        agents = result.get("items", [])
        print(f"✓ Retrieved {len(agents)} public agents")
        print(f"  Total count: {result.get('count', 0)}")
        print(f"  Next page: {result.get('next', 'None')}")

        if agents:
            print("  Sample agents:")
            for agent in agents[:3]:  # Show first 3 agents
                print(f"    - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to get public agents: {e}")

    # Example 2: Get entitled agents (requires authentication)
    print("\n2. Getting entitled agents (requires authentication)...")
    try:
        result = client.get_entitled_agents(top=10, skip=0)
        agents = result.get("items", [])
        print(f"✓ Retrieved {len(agents)} entitled agents")
        print(f"  Total count: {result.get('count', 0)}")

        if agents:
            print("  Sample entitled agents:")
            for agent in agents[:3]:  # Show first 3 agents
                print(f"    - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to get entitled agents: {e}")

    # Example 3: Get specific agent details
    if published_agent_id:
        print(f"\n3. Getting details for agent {published_agent_id}...")
        try:
            result = client.get_agent(published_agent_id)
            print("✓ Retrieved agent details:")
            print(f"  Name: {result.get('name', 'Unknown')}")
            print(f"  Description: {result.get('description', 'Unknown')}")
            print(f"  Publisher: {result.get('publisherId', 'Unknown')}")
            print(f"  Version: {result.get('version', 'Unknown')}")
            print(f"  Protocol Version: {result.get('protocolVersion', 'Unknown')}")
        except Exception as e:
            print(f"✗ Failed to get agent details: {e}")

    # Example 4: Get agent card
    if published_agent_id:
        print(f"\n4. Getting card for agent {published_agent_id}...")
        try:
            result = client.get_agent_card(published_agent_id)
            print("✓ Retrieved agent card:")
            print(f"  Protocol Version: {result.get('protocolVersion', 'Unknown')}")
            print(f"  Name: {result.get('name', 'Unknown')}")
            print(f"  Capabilities: {json.dumps(result.get('capabilities', {}), indent=2)}")
            print(f"  Skills count: {len(result.get('skills', []))}")
        except Exception as e:
            print(f"✗ Failed to get agent card: {e}")


def demonstrate_error_handling(client: A2ARegistryClient):
    """Demonstrate error handling scenarios."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)

    # Example 1: Get non-existent agent
    print("\n1. Getting non-existent agent...")
    try:
        result = client.get_agent("non-existent-agent-id")
        print(f"✓ Unexpectedly found agent: {result}")
    except HTTPError as e:
        if e.response.status_code == 404:
            print("✓ Correctly received 404 for non-existent agent")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 2: Invalid agent card data
    print("\n2. Publishing agent with invalid card data...")
    try:
        invalid_card = {
            "name": "Invalid Agent",
            # Missing required fields like protocolVersion, description, url
        }
        result = client.publish_agent_by_card(invalid_card)
        print(f"✗ Unexpectedly published invalid agent: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for invalid card data")
            print(f"  Error details: {e.response.text}")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 3: Invalid pagination parameters
    print("\n3. Using invalid pagination parameters...")
    try:
        result = client.get_public_agents(top=0, skip=-1)  # Invalid values
        print(f"✗ Unexpectedly retrieved agents with invalid params: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for invalid pagination")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def setup_authentication(client: A2ARegistryClient) -> bool:
    """Set up authentication for the client."""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SETUP")
    print("=" * 60)

    # Check if we already have a token from environment
    if client.token:
        print("✓ Using token from environment variable")
        return True

    # Try to register and authenticate a user
    username = "agent_example_user"
    email = "agent_example@example.com"
    password = "securepassword123"

    print("\n1. Registering user for agent examples...")
    try:
        user_data = client.register_user(
            username=username, email=email, password=password, full_name="Agent Example User", tenant_id="default"
        )
        print("✓ User registered successfully!")
        print(f"  User ID: {user_data.get('id')}")
        print(f"  Username: {user_data.get('username')}")
    except HTTPError as e:
        if e.response.status_code == 409:
            print("ℹ User already exists, proceeding with login...")
        else:
            print(f"✗ Failed to register user: {e}")
            return False
    except Exception as e:
        print(f"✗ Failed to register user: {e}")
        return False

    print("\n2. Authenticating user...")
    try:
        login_result = client.authenticate_user(username, password)
        print("✓ User authenticated successfully!")
        print(f"  Access Token: {login_result.get('access_token', '')[:50]}...")
        print(f"  Token Type: {login_result.get('token_type')}")
        print(f"  Expires In: {login_result.get('expires_in')} seconds")
        return True
    except Exception as e:
        print(f"✗ Failed to authenticate user: {e}")
        return False


def main():
    """Main function to run all examples."""
    print("A2A Registry Agent API Examples")
    print("=" * 60)

    # Configuration
    base_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    token = os.getenv("A2A_TOKEN")  # Optional JWT token for authenticated endpoints

    print(f"Registry URL: {base_url}")
    print(f"External Token: {'Yes' if token else 'No'}")

    # Initialize client
    client = A2ARegistryClient(base_url, token)

    try:
        # Test connection
        print("\nTesting connection...")
        try:
            client.get_public_agents(top=1, skip=0)
            print("✓ Successfully connected to A2A Registry")
        except Exception as e:
            print(f"✗ Failed to connect to A2A Registry: {e}")
            print("Make sure the registry server is running on the specified URL")
            return

        # Set up authentication if needed
        if not token:
            auth_success = setup_authentication(client)
            if not auth_success:
                print("✗ Failed to set up authentication")
                return

        # Run examples
        published_agent_id = demonstrate_agent_publishing(client)
        demonstrate_agent_retrieval(client, published_agent_id)
        demonstrate_error_handling(client)

        print("\n" + "=" * 60)
        print("EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Use the access token for authenticated API calls")
        print("2. Implement agent publishing in your application")
        print("3. Handle authentication errors gracefully")
        print("4. Store tokens securely in your application")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
