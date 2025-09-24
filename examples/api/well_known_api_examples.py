#!/usr/bin/env python3
"""
A2A Registry Well-Known API Examples

This example demonstrates how to interact with the A2A Registry Well-Known API endpoints:
- Getting the agents index (.well-known/agents/index.json)
- Getting agent cards via well-known endpoints
- Public vs private agent access
- Authentication requirements

Requirements:
- A2A Registry server running on localhost:8000
- Built-in authentication system (automatic user registration and login)
- Some agents published in the registry

Usage:
    python well_known_api_examples.py
"""

import os
import sys
from typing import Dict, Any, Optional

import httpx
from httpx import HTTPError, RequestError


class A2AWellKnownClient:
    """Client for interacting with A2A Registry Well-Known API."""

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

    def register_user(self, username: str, email: str, password: str, full_name: Optional[str] = None, tenant_id: str = "default") -> Dict[str, Any]:
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

    def get_agents_index(self, top: int = 20, skip: int = 0) -> Dict[str, Any]:
        """
        Get the agents index via well-known endpoint.

        Args:
            top: Number of results to return (1 - 100)
            skip: Number of results to skip for pagination
        """
        url = f"{self.base_url}/.well-known/agents/index.json"
        params = {"top": top, "skip": skip}

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting agents index: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting agents index: {e}")
            raise

    def get_agent_card(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent card via well-known endpoint.

        Args:
            agent_id: The agent identifier
        """
        url = f"{self.base_url}/.well-known/agents/{agent_id}/card"

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


def demonstrate_agents_index(client: A2AWellKnownClient):
    """Demonstrate agents index functionality."""
    print("\n" + "=" * 60)
    print("AGENTS INDEX EXAMPLES")
    print("=" * 60)

    # Example 1: Get agents index
    print("\n1. Getting agents index...")
    try:
        result = client.get_agents_index(top=10, skip=0)
        agents = result.get("agents", [])
        print("✓ Retrieved agents index successfully")
        print(f"  Registry version: {result.get('registry_version', 'Unknown')}")
        print(f"  Registry name: {result.get('registry_name', 'Unknown')}")
        print(f"  Agents count: {result.get('count', 0)}")
        print(f"  Total count: {result.get('total_count', 0)}")
        print(f"  Next page: {result.get('next', 'None')}")

        if agents:
            print("  Sample agents:")
            for i, agent in enumerate(agents[:5]):
                print(f"    {i + 1}. {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')})")
                print(f"       Description: {agent.get('description', 'No description')}")
                print(f"       Provider: {agent.get('provider', 'Unknown')}")
                print(f"       Location: {agent.get('location', {}).get('url', 'Unknown')}")
    except Exception as e:
        print(f"✗ Failed to get agents index: {e}")

    # Example 2: Pagination
    print("\n2. Testing pagination...")
    try:
        # First page
        result1 = client.get_agents_index(top=5, skip=0)
        agents1 = result1.get("agents", [])
        print(f"✓ First page: {len(agents1)} agents")

        # Second page
        result2 = client.get_agents_index(top=5, skip=5)
        agents2 = result2.get("agents", [])
        print(f"✓ Second page: {len(agents2)} agents")

        # Check if results are different
        if agents1 and agents2:
            ids1 = {agent.get("id") for agent in agents1}
            ids2 = {agent.get("id") for agent in agents2}
            if ids1.isdisjoint(ids2):
                print("✓ Pagination working correctly (no overlap between pages)")
            else:
                print("ℹ Some overlap between pages (may be expected)")
    except Exception as e:
        print(f"✗ Failed to test pagination: {e}")

    # Example 3: Large page size
    print("\n3. Testing large page size...")
    try:
        result = client.get_agents_index(top=50, skip=0)
        agents = result.get("agents", [])
        print(f"✓ Large page size: {len(agents)} agents")
    except Exception as e:
        print(f"✗ Failed to test large page size: {e}")


def demonstrate_agent_cards(client: A2AWellKnownClient):
    """Demonstrate agent card functionality."""
    print("\n" + "=" * 60)
    print("AGENT CARD EXAMPLES")
    print("=" * 60)

    # First, get some agent IDs from the index
    print("\n1. Getting agent IDs from index...")
    try:
        index_result = client.get_agents_index(top=10, skip=0)
        agents = index_result.get("agents", [])

        if not agents:
            print("ℹ No agents found in index, skipping agent card examples")
            return

        agent_ids = [agent.get("id") for agent in agents if agent.get("id")]
        print(f"✓ Found {len(agent_ids)} agent IDs")

        # Example 2: Get agent cards
        print("\n2. Getting agent cards...")
        for i, agent_id in enumerate(agent_ids[:3]):  # Test first 3 agents
            try:
                card = client.get_agent_card(agent_id)
                print(f"✓ Agent {i + 1} ({agent_id}):")
                print(f"  Protocol Version: {card.get('protocolVersion', 'Unknown')}")
                print(f"  Name: {card.get('name', 'Unknown')}")
                print(f"  Description: {card.get('description', 'No description')}")
                print(f"  Version: {card.get('version', 'Unknown')}")

                capabilities = card.get("capabilities", {})
                if capabilities:
                    print("  Capabilities:")
                    for key, value in capabilities.items():
                        print(f"    {key}: {value}")

                skills = card.get("skills", [])
                if skills:
                    print(f"  Skills: {len(skills)} skills")
                    for skill in skills[:2]:  # Show first 2 skills
                        print(f"    - {skill.get('name', 'Unknown')}: {skill.get('description', 'No description')}")

            except HTTPError as e:
                if e.response.status_code == 403:
                    print(f"ℹ Agent {agent_id}: Access denied (private agent)")
                elif e.response.status_code == 404:
                    print(f"ℹ Agent {agent_id}: Not found")
                else:
                    print(f"✗ Agent {agent_id}: Error {e.response.status_code}")
            except Exception as e:
                print(f"✗ Agent {agent_id}: {e}")

    except Exception as e:
        print(f"✗ Failed to get agent IDs: {e}")


def demonstrate_public_vs_private_access(client: A2AWellKnownClient):
    """Demonstrate public vs private agent access."""
    print("\n" + "=" * 60)
    print("PUBLIC VS PRIVATE ACCESS EXAMPLES")
    print("=" * 60)

    # Example 1: Access without authentication
    print("\n1. Accessing agents without authentication...")
    try:
        # Agents index should be accessible without auth
        index_result = client.get_agents_index(top=10, skip=0)
        agents = index_result.get("agents", [])
        print(f"✓ Agents index accessible without authentication: {len(agents)} agents")

        # Try to access agent cards without auth
        if agents:
            agent_id = agents[0].get("id")
            if agent_id:
                try:
                    client.get_agent_card(agent_id)
                    print(f"✓ Agent card {agent_id} accessible without authentication")
                except HTTPError as e:
                    if e.response.status_code == 403:
                        print(f"ℹ Agent card {agent_id} requires authentication (private agent)")
                    else:
                        print(f"✗ Agent card {agent_id} error: {e.response.status_code}")
    except Exception as e:
        print(f"✗ Failed to test unauthenticated access: {e}")

    # Example 2: Access with authentication (if token provided)
    if client.token:
        print("\n2. Accessing agents with authentication...")
        try:
            index_result = client.get_agents_index(top=10, skip=0)
            agents = index_result.get("agents", [])
            print(f"✓ Agents index accessible with authentication: {len(agents)} agents")

            # Try to access agent cards with auth
            if agents:
                agent_id = agents[0].get("id")
                if agent_id:
                    try:
                        client.get_agent_card(agent_id)
                        print(f"✓ Agent card {agent_id} accessible with authentication")
                    except HTTPError as e:
                        print(f"✗ Agent card {agent_id} error: {e.response.status_code}")
        except Exception as e:
            print(f"✗ Failed to test authenticated access: {e}")
    else:
        print("\n2. Skipping authenticated access test (no token provided)")


def demonstrate_error_handling(client: A2AWellKnownClient):
    """Demonstrate error handling scenarios."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)

    # Example 1: Invalid pagination parameters
    print("\n1. Invalid pagination parameters...")
    try:
        result = client.get_agents_index(top=0, skip=-1)  # Invalid values
        print(f"✗ Unexpectedly succeeded with invalid params: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for invalid pagination")
            print(f"  Error details: {e.response.text}")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 2: Non-existent agent
    print("\n2. Non-existent agent...")
    try:
        result = client.get_agent_card("non-existent-agent-id")
        print(f"✗ Unexpectedly found non-existent agent: {result}")
    except HTTPError as e:
        if e.response.status_code == 404:
            print("✓ Correctly received 404 for non-existent agent")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 3: Empty agent ID
    print("\n3. Empty agent ID...")
    try:
        result = client.get_agent_card("")
        print(f"✗ Unexpectedly succeeded with empty agent ID: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for empty agent ID")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_well_known_structure(client: A2AWellKnownClient):
    """Demonstrate well-known endpoint structure and standards compliance."""
    print("\n" + "=" * 60)
    print("WELL-KNOWN STRUCTURE EXAMPLES")
    print("=" * 60)

    # Example 1: Agents index structure
    print("\n1. Agents index structure validation...")
    try:
        result = client.get_agents_index(top=5, skip=0)

        # Check required fields
        required_fields = ["registry_version", "registry_name", "agents", "count", "total_count"]
        missing_fields = [field for field in required_fields if field not in result]

        if not missing_fields:
            print("✓ All required fields present in agents index")
        else:
            print(f"✗ Missing required fields: {missing_fields}")

        # Check agents structure
        agents = result.get("agents", [])
        if agents:
            agent = agents[0]
            agent_required_fields = ["id", "name", "description", "location"]
            agent_missing_fields = [field for field in agent_required_fields if field not in agent]

            if not agent_missing_fields:
                print("✓ Agent structure is valid")
            else:
                print(f"✗ Agent missing required fields: {agent_missing_fields}")

            # Check location structure
            location = agent.get("location", {})
            if "url" in location and "type" in location:
                print("✓ Agent location structure is valid")
            else:
                print("✗ Agent location structure is invalid")

    except Exception as e:
        print(f"✗ Failed to validate agents index structure: {e}")

    # Example 2: Agent card structure
    print("\n2. Agent card structure validation...")
    try:
        index_result = client.get_agents_index(top=1, skip=0)
        agents = index_result.get("agents", [])

        if agents:
            agent_id = agents[0].get("id")
            if agent_id:
                try:
                    card = client.get_agent_card(agent_id)

                    # Check required fields
                    card_required_fields = ["protocolVersion", "name", "description", "url"]
                    card_missing_fields = [field for field in card_required_fields if field not in card]

                    if not card_missing_fields:
                        print("✓ Agent card has all required fields")
                    else:
                        print(f"✗ Agent card missing required fields: {card_missing_fields}")

                    # Check capabilities structure
                    capabilities = card.get("capabilities", {})
                    if capabilities:
                        print("✓ Agent card has capabilities section")
                    else:
                        print("ℹ Agent card has no capabilities section")

                    # Check skills structure
                    skills = card.get("skills", [])
                    if skills:
                        print(f"✓ Agent card has {len(skills)} skills")
                    else:
                        print("ℹ Agent card has no skills")

                except HTTPError as e:
                    if e.response.status_code == 403:
                        print("ℹ Agent card requires authentication (private agent)")
                    else:
                        print(f"✗ Failed to get agent card: {e}")
        else:
            print("ℹ No agents available for card structure validation")

    except Exception as e:
        print(f"✗ Failed to validate agent card structure: {e}")


def setup_authentication(client: A2AWellKnownClient) -> bool:
    """Set up authentication for the client."""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SETUP")
    print("=" * 60)

    # Check if we already have a token from environment
    if client.token:
        print("✓ Using token from environment variable")
        return True

    # Try to register and authenticate a user
    username = "wellknown_example_user"
    email = "wellknown_example@example.com"
    password = "securepassword123"

    print("\n1. Registering user for well-known examples...")
    try:
        user_data = client.register_user(username=username, email=email, password=password, full_name="Well-Known Example User", tenant_id="default")
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
    print("A2A Registry Well-Known API Examples")
    print("=" * 60)

    # Configuration
    base_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    token = os.getenv("A2A_TOKEN")  # Optional JWT token for accessing private agents

    print(f"Registry URL: {base_url}")
    print(f"External Token: {'Yes' if token else 'No'}")

    # Initialize client
    client = A2AWellKnownClient(base_url, token)

    try:
        # Test connection
        print("\nTesting connection...")
        try:
            client.get_agents_index(top=1, skip=0)
            print("✓ Successfully connected to A2A Registry Well-Known API")
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
        demonstrate_agents_index(client)
        demonstrate_agent_cards(client)
        demonstrate_public_vs_private_access(client)
        demonstrate_error_handling(client)
        demonstrate_well_known_structure(client)

        print("\n" + "=" * 60)
        print("WELL-KNOWN API EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Use the access token for accessing private agents")
        print("2. Implement well-known endpoints in your application")
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
