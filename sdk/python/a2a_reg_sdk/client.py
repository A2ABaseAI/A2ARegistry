"""
A2A Registry Client

Main client class for interacting with the A2A Agent Registry.
"""

import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import requests

from .exceptions import A2AError, AuthenticationError, ValidationError, NotFoundError
from .models import Agent, AgentCard


class A2AClient:
    """Client for interacting with the A2A Agent Registry."""

    def __init__(
        self,
        registry_url: str = "http://localhost:8000",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        scope: str = "read write",
    ):
        """
        Initialize the A2A client.

        Args:
            registry_url: Base URL of the A2A registry
            client_id: OAuth client ID for authentication
            client_secret: OAuth client secret for authentication
            timeout: Request timeout in seconds
            api_key: API key for authentication (alternative to OAuth)
            api_key_header: HTTP header name for API key
            scope: OAuth scope for token (e.g., "read", "write", "admin", "read write admin")
        """
        self.registry_url = registry_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._access_token = None
        self._token_expires_at = None
        self._api_key = api_key
        self._api_key_header = api_key_header
        self.scope = scope

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "A2A-Python-SDK/1.0.0", "Content-Type": "application/json"})
        # If API key is provided, set as Bearer token
        if self._api_key:
            self.session.headers["Authorization"] = f"Bearer {self._api_key}"

    def set_api_key(self, api_key: str, header_name: str = "X-API-Key") -> None:
        """
        Configure API key authentication on the client session.

        Args:
            api_key: API key value
            header_name: HTTP header name to send the API key with
        """
        self._api_key = api_key
        self._api_key_header = header_name
        self.session.headers["Authorization"] = f"Bearer {self._api_key}"

    def authenticate(self, scope: Optional[str] = None) -> None:
        """
        Authenticate with the A2A registry using OAuth 2.0 client credentials flow.

        Args:
            scope: OAuth scope for the token (e.g., "read", "write", "admin", "read write admin").
                  If None, uses the scope from the constructor.

        Raises:
            AuthenticationError: If authentication fails
        """
        # If API key auth is configured, skip OAuth flow
        if self._api_key:
            return

        if not self.client_id or not self.client_secret:
            raise AuthenticationError("Client ID and secret are required for authentication")

        # Use provided scope or fall back to constructor scope
        auth_scope = scope if scope is not None else self.scope

        try:
            response = self.session.post(
                urljoin(self.registry_url, "/auth/oauth/token"),
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": auth_scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in - 60  # Refresh 1 minute early

            access_token = self._access_token
            if access_token is None:
                raise AuthenticationError("No access token received")

            # Set authorization header with the valid token
            self._set_auth_header(access_token)  # type: ignore[unreachable]

        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {e}")

    def _set_auth_header(self, access_token: str) -> None:
        """Set the authorization header with the access token."""
        self.session.headers["Authorization"] = f"Bearer {access_token}"

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        # If API key is configured, no token is required
        if self._api_key:
            return

        if not self._access_token:
            self.authenticate(self.scope)
        elif self._token_expires_at and time.time() >= self._token_expires_at:  # type: ignore[unreachable]
            self.authenticate(self.scope)

    def _convert_to_card_spec(self, agent_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Agent model to AgentCardSpec format."""
        # Extract capabilities
        capabilities = agent_dict.get("capabilities", {})
        card_capabilities = {
            "streaming": capabilities.get("streaming", False),
            "pushNotifications": capabilities.get("pushNotifications", False),
            "stateTransitionHistory": capabilities.get("stateTransitionHistory", False),
            "supportsAuthenticatedExtendedCard": capabilities.get("supportsAuthenticatedExtendedCard", False),
        }

        # Convert auth schemes to security schemes
        security_schemes = []
        for auth_scheme in agent_dict.get("auth_schemes", []):
            security_scheme = {
                "type": auth_scheme.get("type", "apiKey"),
                "location": "header",
                "name": auth_scheme.get("header_name", "Authorization"),
            }
            security_schemes.append(security_scheme)

        # Convert skills
        skills = []
        agent_skills = agent_dict.get("skills")
        if agent_skills:
            # Handle different skill formats
            if isinstance(agent_skills, dict):
                # Convert from AgentSkills format
                examples = agent_skills.get("examples", [])
                if examples:
                    skills.append(
                        {
                            "id": "main_skill",
                            "name": "Main Skill",
                            "description": agent_dict.get("description", "Agent skill"),
                            "tags": agent_dict.get("tags", []),
                            "examples": examples,
                            "inputModes": ["text/plain"],
                            "outputModes": ["text/plain"],
                        }
                    )
            elif isinstance(agent_skills, list):
                skills = agent_skills

        # Build interface
        interface: Dict[str, Any] = {
            "preferredTransport": "jsonrpc",
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["text/plain"],
        }

        # Add additional interfaces if location_url is provided
        if agent_dict.get("location_url"):
            interface["additionalInterfaces"] = [{"transport": "http", "url": agent_dict["location_url"]}]

        # Build the card spec
        card_spec = {
            "name": agent_dict.get("name", "Unnamed Agent"),
            "description": agent_dict.get("description", "Agent description"),
            "url": agent_dict.get("location_url", "https://example.com"),
            "version": agent_dict.get("version", "1.0.0"),
            "capabilities": card_capabilities,
            "securitySchemes": security_schemes,
            "skills": skills,
            "interface": interface,
        }

        # Add provider if available
        if agent_dict.get("provider"):
            card_spec["provider"] = {
                "organization": agent_dict["provider"],
                "url": agent_dict.get("location_url", "https://example.com"),
            }

        return card_spec

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            A2AError: For various API errors
        """
        try:
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Authentication required or token expired")
            elif response.status_code == 403:
                raise AuthenticationError("Access denied")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    raise ValidationError(f"Validation error: {error_data.get('detail', str(e))}")
                except ValueError:
                    raise ValidationError(f"Validation error: {e}")
            else:
                try:
                    error_data = response.json()
                    raise A2AError(f"API error: {error_data.get('detail', str(e))}")
                except ValueError:
                    raise A2AError(f"API error: {e}")

    def get_health(self) -> Dict[str, Any]:
        """
        Get registry health status.

        Returns:
            Health status information
        """
        try:
            response = self.session.get(urljoin(self.registry_url, "/health"), timeout=self.timeout)
            return self._handle_response(response)  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise A2AError(f"Failed to get health status: {e}")

    def list_agents(self, page: int = 1, limit: int = 20, public_only: bool = True) -> Dict[str, Any]:
        """
        List agents from the registry.

        Args:
            page: Page number (1-based)
            limit: Number of agents per page
            public_only: Whether to only return public agents

        Returns:
            Dictionary containing agents list and pagination info
        """
        try:
            endpoint = "/agents/public" if public_only else "/agents/entitled"
            response = self.session.get(
                urljoin(self.registry_url, endpoint),
                params={"page": page, "limit": limit},
                timeout=self.timeout,
            )
            return self._handle_response(response)  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise A2AError(f"Failed to list agents: {e}")

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get a specific agent by ID.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            Agent object
        """
        try:
            response = self.session.get(urljoin(self.registry_url, f"/agents/{agent_id}"), timeout=self.timeout)
            agent_data = self._handle_response(response)
            return Agent.from_dict(agent_data)
        except requests.RequestException as e:
            raise A2AError(f"Failed to get agent {agent_id}: {e}")

    def get_agent_card(self, agent_id: str) -> AgentCard:
        """
        Get an agent's card (detailed metadata).

        Args:
            agent_id: The agent's unique identifier

        Returns:
            AgentCard object
        """
        try:
            response = self.session.get(
                urljoin(self.registry_url, f"/agents/{agent_id}/card"),
                timeout=self.timeout,
            )
            card_data = self._handle_response(response)
            return AgentCard.from_dict(card_data)
        except requests.RequestException as e:
            raise A2AError(f"Failed to get agent card for {agent_id}: {e}")

    def search_agents(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        semantic: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Search for agents in the registry.

        Args:
            query: Search query string
            filters: Search filters (tags, capabilities, etc.)
            semantic: Whether to use semantic search
            page: Page number (1-based)
            limit: Number of results per page

        Returns:
            Search results with agents and pagination info
        """
        try:
            search_data = {
                "query": query,
                "filters": filters or {},
                "semantic": semantic,
                "page": page,
                "limit": limit,
            }

            response = self.session.post(
                urljoin(self.registry_url, "/agents/search"),
                json=search_data,
                timeout=self.timeout,
            )
            return self._handle_response(response)  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise A2AError(f"Failed to search agents: {e}")

    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Registry statistics
        """
        try:
            response = self.session.get(urljoin(self.registry_url, "/stats"), timeout=self.timeout)
            return self._handle_response(response)  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise A2AError(f"Failed to get registry stats: {e}")

    def publish_agent(self, agent_data: Union[Dict[str, Any], Agent]) -> Agent:
        """
        Publish a new agent to the registry.

        Args:
            agent_data: Agent data as dict or Agent object

        Returns:
            Published Agent object
        """
        self._ensure_authenticated()

        try:
            if isinstance(agent_data, Agent):
                agent_dict = agent_data.to_dict()
            else:
                agent_dict = agent_data

            # Convert Agent model to AgentCardSpec format
            card_data = self._convert_to_card_spec(agent_dict)

            # Format the request body according to the API spec
            request_body = {"public": agent_dict.get("is_public", True), "card": card_data}

            response = self.session.post(
                urljoin(self.registry_url, "/agents/publish"),
                json=request_body,
                timeout=self.timeout,
            )
            published_data = self._handle_response(response)

            # The API returns a different format, so we need to fetch the full agent data
            if "agentId" in published_data:
                agent_id = published_data["agentId"]
                # Fetch the full agent data
                full_agent = self.get_agent(agent_id)
                return full_agent
            else:
                return Agent.from_dict(published_data)
        except requests.RequestException as e:
            raise A2AError(f"Failed to publish agent: {e}")

    def update_agent(self, agent_id: str, agent_data: Union[Dict[str, Any], Agent]) -> Agent:
        """
        Update an existing agent.

        Args:
            agent_id: The agent's unique identifier
            agent_data: Updated agent data as dict or Agent object

        Returns:
            Updated Agent object
        """
        self._ensure_authenticated()

        try:
            if isinstance(agent_data, Agent):
                agent_dict = agent_data.to_dict()
            else:
                agent_dict = agent_data

            response = self.session.put(
                urljoin(self.registry_url, f"/agents/{agent_id}"),
                json=agent_dict,
                timeout=self.timeout,
            )
            updated_data = self._handle_response(response)
            return Agent.from_dict(updated_data)
        except requests.RequestException as e:
            raise A2AError(f"Failed to update agent {agent_id}: {e}")

    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent from the registry.

        Args:
            agent_id: The agent's unique identifier
        """
        self._ensure_authenticated()

        try:
            response = self.session.delete(urljoin(self.registry_url, f"/agents/{agent_id}"), timeout=self.timeout)
            self._handle_response(response)
        except requests.RequestException as e:
            raise A2AError(f"Failed to delete agent {agent_id}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Registry statistics
        """
        try:
            response = self.session.get(urljoin(self.registry_url, "/stats"), timeout=self.timeout)
            return self._handle_response(response)  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise A2AError(f"Failed to get registry stats: {e}")

    def generate_api_key(self, scopes: List[str], expires_days: Optional[int] = None) -> tuple[str, Dict[str, Any]]:
        """
        Generate a new API key using the backend security service.

        Args:
            scopes: List of scopes for the API key
            expires_days: Number of days until expiration (None for no expiration)

        Returns:
            Tuple of (api_key_string, key_info_dict)

        Raises:
            A2AError: If API key generation fails
        """
        self._ensure_authenticated()

        try:
            payload = {"scopes": scopes, "expires_days": expires_days}

            response = self.session.post(urljoin(self.registry_url, "/security/api-keys"), json=payload, timeout=self.timeout)

            response_data = self._handle_response(response)

            # Return API key and info
            return response_data["api_key"], {
                "key_id": response_data["key_id"],
                "scopes": response_data["scopes"],
                "created_at": response_data["created_at"],
                "expires_at": response_data.get("expires_at"),
            }

        except Exception as e:
            raise A2AError(f"Failed to generate API key: {e}")

    def generate_api_key_and_authenticate(self, scopes: List[str], expires_days: Optional[int] = None) -> tuple[str, Dict[str, Any]]:
        """
        Generate a new API key and automatically authenticate the client with it.

        Args:
            scopes: List of scopes for the API key
            expires_days: Number of days until expiration (None for no expiration)

        Returns:
            Tuple of (api_key_string, key_info_dict)

        Raises:
            A2AError: If API key generation or authentication fails
        """
        try:
            # Generate API key
            api_key, key_info = self.generate_api_key(scopes, expires_days)

            # Authenticate with the new API key
            self.set_api_key(api_key)

            return api_key, key_info

        except Exception as e:
            raise A2AError(f"Failed to generate and authenticate with API key: {e}")

    def validate_api_key(self, api_key: str, required_scopes: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using the backend security service.

        Args:
            api_key: The API key to validate
            required_scopes: Optional list of required scopes

        Returns:
            Key info dict if valid, None if invalid
        """
        try:
            payload = {"api_key": api_key, "required_scopes": required_scopes}

            response = self.session.post(urljoin(self.registry_url, "/security/api-keys/validate"), json=payload, timeout=self.timeout)

            if response.status_code == 401:
                return None

            response_data = self._handle_response(response)
            return response_data  # type: ignore[no-any-return]

        except Exception:
            # Log error but don't raise - validation failure should return None
            return None

    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key using the backend security service.

        Args:
            key_id: The ID of the API key to revoke

        Returns:
            True if revoked successfully, False otherwise
        """
        self._ensure_authenticated()

        try:
            response = self.session.delete(urljoin(self.registry_url, f"/security/api-keys/{key_id}"), timeout=self.timeout)

            if response.status_code == 404:
                return False

            self._handle_response(response)
            return True

        except Exception:
            # Log error but don't raise - revocation failure should return False
            return False

    def list_api_keys(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all API keys using the backend security service.

        Args:
            active_only: If True, only return active keys

        Returns:
            List of key info dictionaries
        """
        self._ensure_authenticated()

        try:
            params = {"active_only": active_only}

            response = self.session.get(urljoin(self.registry_url, "/security/api-keys"), params=params, timeout=self.timeout)

            return self._handle_response(response)  # type: ignore[no-any-return]

        except Exception as e:
            raise A2AError(f"Failed to list API keys: {e}")

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
