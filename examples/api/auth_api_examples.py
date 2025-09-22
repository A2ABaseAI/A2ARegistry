#!/usr/bin/env python3
"""
A2A Registry Authentication API Examples

This example demonstrates how to use the A2A Registry's built-in authentication system:
- User registration
- User login and token generation
- Token refresh
- User profile management
- Password changes
- Logout

Requirements:
- A2A Registry server running on localhost:8000
- Database with user tables created (run migrations)

Usage:
    python auth_api_examples.py
"""

import os
import sys
from typing import Dict, Any, Optional

import httpx
from httpx import HTTPError, RequestError


class A2AAuthClient:
    """Client for interacting with A2A Registry Authentication API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=30.0)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get headers with optional authentication."""
        headers = {"Content-Type": "application/json"}
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """Register a new user."""
        url = f"{self.base_url}/auth/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "tenant_id": tenant_id
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._get_headers(include_auth=False)
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error registering user: {e}")
            if e.response.status_code == 409:
                print(f"Response: {e.response.text}")
            raise
        except RequestError as e:
            print(f"Request Error registering user: {e}")
            raise

    def login_user(
        self,
        email_or_username: str,
        password: str
    ) -> Dict[str, Any]:
        """Login user and get tokens."""
        url = f"{self.base_url}/auth/login"
        payload = {
            "email_or_username": email_or_username,
            "password": password
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._get_headers(include_auth=False)
            )
            response.raise_for_status()

            result = response.json()

            # Store tokens for future use
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")

            return result
        except HTTPError as e:
            print(f"HTTP Error logging in: {e}")
            if e.response.status_code == 401:
                print(f"Response: {e.response.text}")
            raise
        except RequestError as e:
            print(f"Request Error logging in: {e}")
            raise

    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        url = f"{self.base_url}/auth/refresh"
        payload = {
            "refresh_token": self.refresh_token
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._get_headers(include_auth=False)
            )
            response.raise_for_status()

            result = response.json()

            # Update access token
            self.access_token = result.get("access_token")

            return result
        except HTTPError as e:
            print(f"HTTP Error refreshing token: {e}")
            raise
        except RequestError as e:
            print(f"Request Error refreshing token: {e}")
            raise

    def get_current_user(self) -> Dict[str, Any]:
        """Get current user profile."""
        url = f"{self.base_url}/auth/me"

        try:
            response = self.client.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error getting user profile: {e}")
            raise
        except RequestError as e:
            print(f"Request Error getting user profile: {e}")
            raise

    def change_password(
        self,
        current_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Change user password."""
        url = f"{self.base_url}/auth/change-password"
        payload = {
            "current_password": current_password,
            "new_password": new_password
        }

        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP Error changing password: {e}")
            raise
        except RequestError as e:
            print(f"Request Error changing password: {e}")
            raise

    def logout_user(self) -> Dict[str, Any]:
        """Logout user and invalidate session."""
        url = f"{self.base_url}/auth/logout"

        try:
            response = self.client.post(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()

            # Clear tokens
            self.access_token = None
            self.refresh_token = None

            return response.json()
        except HTTPError as e:
            print(f"HTTP Error logging out: {e}")
            raise
        except RequestError as e:
            print(f"Request Error logging out: {e}")
            raise

    def close(self):
        """Close the HTTP client."""
        self.client.close()


def demonstrate_user_registration(client: A2AAuthClient):
    """Demonstrate user registration."""
    print("\n" + "="*60)
    print("USER REGISTRATION EXAMPLES")
    print("="*60)

    # Example 1: Register a new user
    print("\n1. Registering a new user...")
    try:
        user_data = client.register_user(
            username="testuser123",
            email="testuser@example.com",
            password="securepassword123",
            full_name="Test User",
            tenant_id="default"
        )
        print("✓ User registered successfully!")
        print(f"  User ID: {user_data.get('id')}")
        print(f"  Username: {user_data.get('username')}")
        print(f"  Email: {user_data.get('email')}")
        print(f"  Tenant: {user_data.get('tenant_id')}")
        print(f"  Roles: {user_data.get('roles')}")
        return user_data
    except Exception as e:
        print(f"✗ Failed to register user: {e}")
        return None

    # Example 2: Try to register duplicate user
    print("\n2. Attempting to register duplicate user...")
    try:
        client.register_user(
            username="testuser123",  # Same username
            email="different@example.com",
            password="password123"
        )
        print("✗ Unexpectedly registered duplicate user")
    except HTTPError as e:
        if e.response.status_code == 409:
            print("✓ Correctly rejected duplicate username")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_user_login(client: A2AAuthClient, user_data: Optional[Dict[str, Any]]):
    """Demonstrate user login."""
    print("\n" + "="*60)
    print("USER LOGIN EXAMPLES")
    print("="*60)

    if not user_data:
        print("ℹ Skipping login examples (no user data)")
        return

    # Example 1: Login with email
    print("\n1. Logging in with email...")
    try:
        login_result = client.login_user(
            email_or_username="testuser@example.com",
            password="securepassword123"
        )
        print("✓ Login successful!")
        print(f"  Access Token: {login_result.get('access_token', '')[:50]}...")
        print(f"  Refresh Token: {login_result.get('refresh_token', '')[:20]}...")
        print(f"  Token Type: {login_result.get('token_type')}")
        print(f"  Expires In: {login_result.get('expires_in')} seconds")

        user_info = login_result.get('user', {})
        print(f"  User: {user_info.get('username')} ({user_info.get('email')})")
        print(f"  Roles: {user_info.get('roles')}")
        return login_result
    except Exception as e:
        print(f"✗ Failed to login: {e}")
        return None

    # Example 2: Login with username
    print("\n2. Logging in with username...")
    try:
        login_result = client.login_user(
            email_or_username="testuser123",
            password="securepassword123"
        )
        print("✓ Login with username successful!")
        print(f"  User: {login_result.get('user', {}).get('username')}")
    except Exception as e:
        print(f"✗ Failed to login with username: {e}")

    # Example 3: Login with wrong password
    print("\n3. Attempting login with wrong password...")
    try:
        client.login_user(
            email_or_username="testuser@example.com",
            password="wrongpassword"
        )
        print("✗ Unexpectedly logged in with wrong password")
    except HTTPError as e:
        if e.response.status_code == 401:
            print("✓ Correctly rejected wrong password")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_token_management(client: A2AAuthClient):
    """Demonstrate token management."""
    print("\n" + "="*60)
    print("TOKEN MANAGEMENT EXAMPLES")
    print("="*60)

    # Example 1: Get current user profile
    print("\n1. Getting current user profile...")
    try:
        user_profile = client.get_current_user()
        print("✓ Retrieved user profile successfully!")
        print(f"  Username: {user_profile.get('username')}")
        print(f"  Email: {user_profile.get('email')}")
        print(f"  Full Name: {user_profile.get('full_name')}")
        print(f"  Tenant: {user_profile.get('tenant_id')}")
        print(f"  Roles: {user_profile.get('roles')}")
        print(f"  Active: {user_profile.get('is_active')}")
        print(f"  Created: {user_profile.get('created_at')}")
    except Exception as e:
        print(f"✗ Failed to get user profile: {e}")

    # Example 2: Refresh access token
    print("\n2. Refreshing access token...")
    try:
        refresh_result = client.refresh_access_token()
        print("✓ Token refreshed successfully!")
        print(f"  New Access Token: {refresh_result.get('access_token', '')[:50]}...")
        print(f"  Expires In: {refresh_result.get('expires_in')} seconds")
    except Exception as e:
        print(f"✗ Failed to refresh token: {e}")

    # Example 3: Try to access protected endpoint without token
    print("\n3. Testing access without token...")
    # Temporarily clear token
    original_token = client.access_token
    client.access_token = None

    try:
        client.get_current_user()
        print("✗ Unexpectedly accessed protected endpoint without token")
    except HTTPError as e:
        if e.response.status_code == 401:
            print("✓ Correctly rejected request without token")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Restore token
    client.access_token = original_token


def demonstrate_password_management(client: A2AAuthClient):
    """Demonstrate password management."""
    print("\n" + "="*60)
    print("PASSWORD MANAGEMENT EXAMPLES")
    print("="*60)

    # Example 1: Change password
    print("\n1. Changing password...")
    try:
        result = client.change_password(
            current_password="securepassword123",
            new_password="newpassword456"
        )
        print("✓ Password changed successfully!")
        print(f"  Message: {result.get('message')}")

        # Update the stored password for subsequent tests
        return "newpassword456"
    except Exception as e:
        print(f"✗ Failed to change password: {e}")
        return "securepassword123"

    # Example 2: Try to change password with wrong current password
    print("\n2. Attempting to change password with wrong current password...")
    try:
        client.change_password(
            current_password="wrongpassword",
            new_password="anotherpassword"
        )
        print("✗ Unexpectedly changed password with wrong current password")
    except HTTPError as e:
        if e.response.status_code == 400:
            print("✓ Correctly rejected wrong current password")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_logout(client: A2AAuthClient):
    """Demonstrate user logout."""
    print("\n" + "="*60)
    print("LOGOUT EXAMPLES")
    print("="*60)

    # Example 1: Logout user
    print("\n1. Logging out user...")
    try:
        result = client.logout_user()
        print("✓ Logout successful!")
        print(f"  Message: {result.get('message')}")
        print(f"  Tokens cleared: {client.access_token is None}")
    except Exception as e:
        print(f"✗ Failed to logout: {e}")

    # Example 2: Try to access protected endpoint after logout
    print("\n2. Testing access after logout...")
    try:
        client.get_current_user()
        print("✗ Unexpectedly accessed protected endpoint after logout")
    except HTTPError as e:
        if e.response.status_code == 401:
            print("✓ Correctly rejected request after logout")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_integration_with_agent_api(client: A2AAuthClient):
    """Demonstrate integration with agent API."""
    print("\n" + "="*60)
    print("INTEGRATION WITH AGENT API EXAMPLES")
    print("="*60)

    # Example 1: Access entitled agents endpoint
    print("\n1. Accessing entitled agents endpoint...")
    try:
        url = f"{client.base_url}/agents/entitled"
        response = client.client.get(
            url,
            headers=client._get_headers()
        )
        response.raise_for_status()
        result = response.json()
        print("✓ Successfully accessed entitled agents endpoint!")
        print(f"  Found {len(result.get('items', []))} entitled agents")
    except HTTPError as e:
        if e.response.status_code == 401:
            print("ℹ Entitled agents endpoint requires authentication (expected)")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Example 2: Access public agents endpoint (no auth required)
    print("\n2. Accessing public agents endpoint...")
    try:
        url = f"{client.base_url}/agents/public"
        response = client.client.get(url)
        response.raise_for_status()
        result = response.json()
        print("✓ Successfully accessed public agents endpoint!")
        print(f"  Found {len(result.get('items', []))} public agents")
    except Exception as e:
        print(f"✗ Failed to access public agents: {e}")


def main():
    """Main function to run all examples."""
    print("A2A Registry Authentication API Examples")
    print("=" * 60)

    # Configuration
    base_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    print(f"Registry URL: {base_url}")

    # Initialize client
    client = A2AAuthClient(base_url)

    try:
        # Test connection
        print("\nTesting connection...")
        try:
            response = client.client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✓ Successfully connected to A2A Registry")
            else:
                print(f"ℹ Registry responded with status {response.status_code}")
        except Exception as e:
            print(f"✗ Failed to connect to A2A Registry: {e}")
            print("Make sure the registry server is running on the specified URL")
            return

        # Run examples
        user_data = demonstrate_user_registration(client)
        login_result = demonstrate_user_login(client, user_data)

        if login_result:
            demonstrate_token_management(client)
            new_password = demonstrate_password_management(client)

            # Re-login with new password for logout test
            try:
                client.login_user("testuser@example.com", new_password)
                demonstrate_logout(client)
            except Exception as e:
                print(f"ℹ Could not re-login for logout test: {e}")

            demonstrate_integration_with_agent_api(client)

        print("\n" + "="*60)
        print("AUTHENTICATION EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Use the access token for authenticated API calls")
        print("2. Implement token refresh in your application")
        print("3. Handle authentication errors gracefully")
        print("4. Store tokens securely in your application")
        print("5. Run other API examples:")
        print("   - agent_api_examples.py")
        print("   - search_api_examples.py")
        print("   - well_known_api_examples.py")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
