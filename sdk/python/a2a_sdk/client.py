"""
A2A Registry Client

Main client class for interacting with the A2A Agent Registry.
"""

import json
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
    ):
        """
        Initialize the A2A client.

        Args:
            registry_url: Base URL of the A2A registry
            client_id: OAuth client ID for authentication
            client_secret: OAuth client secret for authentication
            timeout: Request timeout in seconds
        """
        self.registry_url = registry_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._access_token = None
        self._token_expires_at = None
        self._api_key = api_key
        self._api_key_header = api_key_header

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "A2A-Python-SDK/1.0.0", "Content-Type": "application/json"})
        # If API key is provided, set it on the session headers so SDK can be used without OAuth login
        if self._api_key:
            self.session.headers[self._api_key_header] = self._api_key

    def set_api_key(self, api_key: str, header_name: str = "X-API-Key") -> None:
        """
        Configure API key authentication on the client session.

        Args:
            api_key: API key value
            header_name: HTTP header name to send the API key with
        """
        self._api_key = api_key
        self._api_key_header = header_name
        self.session.headers[self._api_key_header] = self._api_key

    def authenticate(self) -> None:
        """
        Authenticate with the A2A registry using OAuth 2.0 client credentials flow.

        Raises:
            AuthenticationError: If authentication fails
        """
        # If API key auth is configured, skip OAuth flow
        if self._api_key:
            return

        if not self.client_id or not self.client_secret:
            raise AuthenticationError("Client ID and secret are required for authentication")

        try:
            response = self.session.post(
                urljoin(self.registry_url, "/oauth/token"),
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in - 60  # Refresh 1 minute early

            if self._access_token:
                self.session.headers["Authorization"] = f"Bearer {self._access_token}"
            else:
                raise AuthenticationError("No access token received")

        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {e}")

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        # If API key is configured, no token is required
        if self._api_key:
            return

        if not self._access_token or (self._token_expires_at and time.time() >= self._token_expires_at):
            self.authenticate()

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
            return self._handle_response(response)
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
            endpoint = "/agents/public" if public_only else "/agents"
            response = self.session.get(
                urljoin(self.registry_url, endpoint),
                params={"page": page, "limit": limit},
                timeout=self.timeout,
            )
            return self._handle_response(response)
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
            return self._handle_response(response)
        except requests.RequestException as e:
            raise A2AError(f"Failed to search agents: {e}")

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

            response = self.session.post(
                urljoin(self.registry_url, "/agents"),
                json=agent_dict,
                timeout=self.timeout,
            )
            published_data = self._handle_response(response)
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
            return self._handle_response(response)
        except requests.RequestException as e:
            raise A2AError(f"Failed to get registry stats: {e}")

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
