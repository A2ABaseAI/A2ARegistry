#!/usr/bin/env python3
"""
A2A Registry Search API Examples

This example demonstrates how to interact with the A2A Registry Search API endpoint:
- Basic text search
- Advanced filtering
- Pagination
- Complex queries with multiple filters
- Error handling

Requirements:
- A2A Registry server running on localhost:8000
- Built-in authentication system (automatic user registration and login)
- Some agents published in the registry for meaningful search results

Usage:
    python search_api_examples.py
"""

import os
import sys
from typing import Dict, Any, Optional

import httpx
from httpx import HTTPError, RequestError


class A2ASearchClient:
    """Client for interacting with A2A Registry Search API."""

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

    def search_agents(
        self, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, top: int = 20, skip: int = 0
    ) -> Dict[str, Any]:
        """
        Search for agents with optional filters and pagination.

        Args:
            query: Text search query
            filters: Dictionary of filters to apply
            top: Number of results to return (1 - 100)
            skip: Number of results to skip for pagination
        """
        url = f"{self.base_url}/agents/search"
        payload = {"q": query, "filters": filters or {}, "top": top, "skip": skip}

        try:
            response = self.client.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error searching agents: {e}")
            if e.response.status_code == 400:
                print(f"Response: {e.response.text}")
            raise
        except RequestError as e:
            print(f"Request Error searching agents: {e}")
            raise

    def close(self):
        """Close the HTTP client."""
        self.client.close()


def demonstrate_basic_search(client: A2ASearchClient):
    """Demonstrate basic search functionality."""
    print("\n" + "=" * 60)
    print("BASIC SEARCH EXAMPLES")
    print("=" * 60)

    # Example 1: Simple text search
    print("\n1. Simple text search...")
    try:
        result = client.search_agents(query="test")
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents matching 'test'")
        print(f"  Total count: {result.get('count', 0)}")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                print(f"    - {item.get('name', 'Unknown')} (ID: {item.get('agentId', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to search for 'test': {e}")

    # Example 2: Search with empty query (should return all agents)
    print("\n2. Search with empty query (all agents)...")
    try:
        result = client.search_agents(query="")
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents with empty query")
        print(f"  Total count: {result.get('count', 0)}")
    except Exception as e:
        print(f"✗ Failed to search with empty query: {e}")

    # Example 3: Search with None query (should return all agents)
    print("\n3. Search with None query (all agents)...")
    try:
        result = client.search_agents(query=None)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents with None query")
        print(f"  Total count: {result.get('count', 0)}")
    except Exception as e:
        print(f"✗ Failed to search with None query: {e}")


def demonstrate_advanced_filtering(client: A2ASearchClient):
    """Demonstrate advanced filtering functionality."""
    print("\n" + "=" * 60)
    print("ADVANCED FILTERING EXAMPLES")
    print("=" * 60)

    # Example 1: Filter by protocol version
    print("\n1. Filter by protocol version...")
    try:
        filters = {"protocolVersion": "0.3.0"}
        result = client.search_agents(query="", filters=filters)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents with protocol version 0.3.0")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                print(f"    - {item.get('name', 'Unknown')} (Protocol: {item.get('protocolVersion', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to filter by protocol version: {e}")

    # Example 2: Filter by publisher
    print("\n2. Filter by publisher...")
    try:
        filters = {"publisherId": "test-publisher"}
        result = client.search_agents(query="", filters=filters)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents from publisher 'test-publisher'")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                print(f"    - {item.get('name', 'Unknown')} (Publisher: {item.get('publisherId', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to filter by publisher: {e}")

    # Example 3: Multiple filters
    print("\n3. Multiple filters (protocol version + publisher)...")
    try:
        filters = {"protocolVersion": "0.3.0", "publisherId": "test-publisher"}
        result = client.search_agents(query="", filters=filters)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents matching both filters")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                name = item.get("name", "Unknown")
                protocol = item.get("protocolVersion", "Unknown")
                publisher = item.get("publisherId", "Unknown")
                print(f"    - {name} (Protocol: {protocol}, Publisher: {publisher})")
    except Exception as e:
        print(f"✗ Failed to apply multiple filters: {e}")

    # Example 4: Complex filters with capabilities
    print("\n4. Complex filters with capabilities...")
    try:
        filters = {"capabilities.text": True, "capabilities.streaming": True}
        result = client.search_agents(query="", filters=filters)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents with text and streaming capabilities")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                capabilities = item.get("capabilities", {})
                name = item.get("name", "Unknown")
                text_cap = capabilities.get("text", False)
                stream_cap = capabilities.get("streaming", False)
                print(f"    - {name} (Text: {text_cap}, Streaming: {stream_cap})")
    except Exception as e:
        print(f"✗ Failed to filter by capabilities: {e}")


def demonstrate_pagination(client: A2ASearchClient):
    """Demonstrate pagination functionality."""
    print("\n" + "=" * 60)
    print("PAGINATION EXAMPLES")
    print("=" * 60)

    # Example 1: First page
    print("\n1. First page (top=5, skip=0)...")
    try:
        result = client.search_agents(query="", top=5, skip=0)
        items = result.get("items", [])
        print(f"✓ Retrieved {len(items)} agents on first page")
        print(f"  Total count: {result.get('count', 0)}")

        if items:
            print("  Agents on first page:")
            for i, item in enumerate(items):
                print(f"    {i+1}. {item.get('name', 'Unknown')} (ID: {item.get('agentId', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to get first page: {e}")
        return

    # Example 2: Second page
    print("\n2. Second page (top=5, skip=5)...")
    try:
        result = client.search_agents(query="", top=5, skip=5)
        items = result.get("items", [])
        print(f"✓ Retrieved {len(items)} agents on second page")

        if items:
            print("  Agents on second page:")
            for i, item in enumerate(items):
                print(f"    {i+6}. {item.get('name', 'Unknown')} (ID: {item.get('agentId', 'Unknown')})")
    except Exception as e:
        print(f"✗ Failed to get second page: {e}")

    # Example 3: Large page size
    print("\n3. Large page size (top=50)...")
    try:
        result = client.search_agents(query="", top=50, skip=0)
        items = result.get("items", [])
        print(f"✓ Retrieved {len(items)} agents with large page size")
    except Exception as e:
        print(f"✗ Failed to get large page: {e}")


def demonstrate_combined_search(client: A2ASearchClient):
    """Demonstrate combined search functionality."""
    print("\n" + "=" * 60)
    print("COMBINED SEARCH EXAMPLES")
    print("=" * 60)

    # Example 1: Text search + filters + pagination
    print("\n1. Text search with filters and pagination...")
    try:
        filters = {"protocolVersion": "0.3.0", "capabilities.text": True}
        result = client.search_agents(query="agent", filters=filters, top=10, skip=0)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents matching 'agent' with filters")
        print(f"  Total count: {result.get('count', 0)}")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                capabilities = item.get("capabilities", {})
                name = item.get("name", "Unknown")
                protocol = item.get("protocolVersion", "Unknown")
                text_cap = capabilities.get("text", False)
                print(f"    - {name} (Protocol: {protocol}, Text: {text_cap})")
    except Exception as e:
        print(f"✗ Failed to perform combined search: {e}")

    # Example 2: Search with skill filters
    print("\n2. Search with skill filters...")
    try:
        filters = {"skills.name": "text_processing"}
        result = client.search_agents(query="", filters=filters, top=10, skip=0)
        items = result.get("items", [])
        print(f"✓ Found {len(items)} agents with 'text_processing' skill")

        if items:
            print("  Sample results:")
            for item in items[:3]:
                skills = item.get("skills", [])
                skill_names = [skill.get("name", "Unknown") for skill in skills]
                print(f"    - {item.get('name', 'Unknown')} (Skills: {', '.join(skill_names)})")
    except Exception as e:
        print(f"✗ Failed to search by skills: {e}")


def demonstrate_error_handling(client: A2ASearchClient):
    """Demonstrate error handling scenarios."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)

    # Example 1: Invalid pagination parameters
    print("\n1. Invalid pagination parameters...")
    try:
        result = client.search_agents(query="", top=0, skip=-1)  # Invalid values
        print(f"✗ Unexpectedly succeeded with invalid params: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for invalid pagination")
            print(f"  Error details: {e.response.text}")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 2: Too large page size
    print("\n2. Too large page size...")
    try:
        result = client.search_agents(query="", top=1000, skip=0)  # Too large
        print(f"✗ Unexpectedly succeeded with large page size: {result}")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for too large page size")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 3: Invalid filter format
    print("\n3. Invalid filter format...")
    try:
        filters = {"invalid_field": "invalid_value", "another_invalid": ["list", "value"]}
        result = client.search_agents(query="", filters=filters)
        print("✓ Search succeeded with invalid filters (may be ignored)")
        print(f"  Results: {len(result.get('items', []))} agents")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly received 400 for invalid filters")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_performance_testing(client: A2ASearchClient):
    """Demonstrate performance testing scenarios."""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTING EXAMPLES")
    print("=" * 60)

    import time

    # Example 1: Multiple searches to test caching
    print("\n1. Testing search performance and caching...")
    try:
        # First search
        start_time = time.time()
        result1 = client.search_agents(query="test", top=20, skip=0)
        first_search_time = time.time() - start_time

        # Second identical search (should be faster due to caching)
        start_time = time.time()
        result2 = client.search_agents(query="test", top=20, skip=0)
        second_search_time = time.time() - start_time

        print(f"✓ First search: {first_search_time:.3f}s")
        print(f"✓ Second search: {second_search_time:.3f}s")
        print(f"✓ Results consistent: {len(result1.get('items', [])) == len(result2.get('items', []))}")

        if second_search_time < first_search_time:
            print("✓ Caching appears to be working (second search faster)")
        else:
            print("ℹ Caching may not be active or search is too fast to measure")

    except Exception as e:
        print(f"✗ Failed to test search performance: {e}")

    # Example 2: Different query patterns
    print("\n2. Testing different query patterns...")
    queries = ["", "test", "agent", "python", "api"]

    for query in queries:
        try:
            start_time = time.time()
            result = client.search_agents(query=query, top=10, skip=0)
            search_time = time.time() - start_time
            items_count = len(result.get("items", []))
            print(f"✓ Query '{query}': {search_time:.3f}s, {items_count} results")
        except Exception as e:
            print(f"✗ Query '{query}' failed: {e}")


def setup_authentication(client: A2ASearchClient) -> bool:
    """Set up authentication for the client."""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SETUP")
    print("=" * 60)

    # Check if we already have a token from environment
    if client.token:
        print("✓ Using token from environment variable")
        return True

    # Try to register and authenticate a user
    username = "search_example_user"
    email = "search_example@example.com"
    password = "securepassword123"

    print("\n1. Registering user for search examples...")
    try:
        user_data = client.register_user(
            username=username, email=email, password=password, full_name="Search Example User", tenant_id="default"
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
    print("A2A Registry Search API Examples")
    print("=" * 60)

    # Configuration
    base_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    token = os.getenv("A2A_TOKEN")  # Optional JWT token for authenticated searches

    print(f"Registry URL: {base_url}")
    print(f"External Token: {'Yes' if token else 'No'}")

    # Initialize client
    client = A2ASearchClient(base_url, token)

    try:
        # Test connection
        print("\nTesting connection...")
        try:
            client.search_agents(query="", top=1, skip=0)
            print("✓ Successfully connected to A2A Registry Search API")
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
        demonstrate_basic_search(client)
        demonstrate_advanced_filtering(client)
        demonstrate_pagination(client)
        demonstrate_combined_search(client)
        demonstrate_error_handling(client)
        demonstrate_performance_testing(client)

        print("\n" + "=" * 60)
        print("SEARCH EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Use the access token for authenticated searches")
        print("2. Implement advanced search in your application")
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
