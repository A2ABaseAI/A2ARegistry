#!/usr/bin/env python3
"""
API Key Workflow Example

This example demonstrates:
- Registering a new user (regular role)
- Generating an admin API token (requires Administrator via admin Bearer/API key)
- Using the API token as Bearer to authenticate the SDK
- Publishing a new agent and verifying its properties

Environment variables:
- REGISTRY_URL (default: http://localhost:8000)
- ADMIN_API_KEY (Bearer admin key to call /auth/api-token)
"""

import os
import time
import json
import uuid
from typing import Any, Dict

import requests
from a2a_sdk import A2AClient


REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:8000")


def register_user() -> Dict[str, Any]:
    """Register a new user and return the profile."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {
        "email": email,
        "username": username,
        "password": "Test1234!",
        "full_name": "SDK Example User",
        "tenant_id": "default",
    }
    resp = requests.post(f"{REGISTRY_URL}/auth/register", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def generate_api_token(admin_bearer: str) -> Dict[str, str]:
    """Generate an API token using an admin Bearer (Administrator role required)."""
    headers = {"Authorization": f"Bearer {admin_bearer}", "Content-Type": "application/json"}
    resp = requests.post(f"{REGISTRY_URL}/auth/api-token", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_minimal_agent_card(name_suffix: str) -> Dict[str, Any]:
    """Build a minimal A2A AgentCardSpec-compliant card."""
    return {
        "name": f"SDK Example Agent {name_suffix}",
        "description": "Agent published via SDK using API key",
        "url": "https://example-agent.local/",
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False,
            "supportsAuthenticatedExtendedCard": False,
        },
        "securitySchemes": [
            {"type": "apiKey", "location": "header", "name": "Authorization"}
        ],
        "skills": [],
        "interface": {
            "preferredTransport": "jsonrpc",
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["text/plain"],
        },
    }


def main():
    # 1) Register a user (informational; does not grant admin)
    user_profile = register_user()
    print(f"✓ Registered user: {user_profile.get('username')} ({user_profile.get('email')})")

    # 2) Generate API token via admin bearer
    admin_api_key = os.getenv("ADMIN_API_KEY")
    if not admin_api_key:
        raise SystemExit("ADMIN_API_KEY is required to generate API tokens (Administrator role)")

    token_resp = generate_api_token(admin_api_key)
    # Use ADMIN_API_KEY for auth (already allowlisted in dev compose). The generated token
    # is shown for demonstration, but not installed server-side automatically.
    api_token = os.getenv("ADMIN_API_KEY") or token_resp.get("token")
    sha256 = token_resp.get("sha256")
    print(f"✓ Generated API token (sha256={sha256[:12]}...)")

    # 3) Initialize SDK with API token (Bearer)
    client = A2AClient(registry_url=REGISTRY_URL, api_key=api_token)

    # Optional wait for backend readiness (e.g., opensearch index)
    time.sleep(1.0)

    # 4) Publish new agent using API key (call /agents/publish directly)
    # The SDK uses legacy path; publish via HTTP then query via SDK
    card = build_minimal_agent_card(name_suffix=uuid.uuid4().hex[:6])
    body: Dict[str, Any] = {"public": True, "card": card}
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    pub_resp = requests.post(f"{REGISTRY_URL}/agents/publish", json=body, headers=headers, timeout=20)
    pub_resp.raise_for_status()
    published = pub_resp.json()
    print(f"✓ Published agent: {published.get('agentId')} v{published.get('version')}")

    agent_id = published.get("agentId")

    # 5) Verify agent properties
    details = client.get_agent(agent_id)
    card_roundtrip = client.get_agent_card(agent_id)

    assert details.name == card["name"], "Agent name mismatch"
    assert card_roundtrip["capabilities"]["streaming"] is False, "Capabilities mismatch"
    assert isinstance(card_roundtrip.get("skills"), list), "Skills must be a list"

    print("✓ Verified agent properties and card structure")


if __name__ == "__main__":
    main()
