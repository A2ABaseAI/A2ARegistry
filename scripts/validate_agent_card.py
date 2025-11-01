#!/usr/bin/env python3
"""
Validate Agent Card Script

This script validates an agent card against the A2A Card Spec schema.
"""

import sys
import json
import requests
from pathlib import Path

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from registry.schemas.agent_card_spec import AgentCardSpec
    from pydantic import ValidationError
    SCHEMA_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import validation schema: {e}")
    SCHEMA_AVAILABLE = False
    sys.exit(1)


def validate_agent_card(agent_card_url: str, api_key: str = "dev-admin-api-key") -> tuple[bool, list[str]]:
    """
    Validate an agent card from a URL against the A2A Card Spec schema.
    
    Args:
        agent_card_url: URL to fetch the agent card from
        api_key: API key for authentication (optional)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not SCHEMA_AVAILABLE:
        return False, ["Validation schema not available"]
    
    # Fetch agent card with authentication
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.get(agent_card_url, headers=headers, timeout=10)
        response.raise_for_status()
        card_data = response.json()
    except requests.RequestException as e:
        return False, [f"Failed to fetch agent card: {e}"]
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON response: {e}"]
    
    # Validate against schema
    try:
        card = AgentCardSpec.model_validate(card_data)
        return True, []
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_type = error["type"]
            errors.append(f"{field}: {message} (type: {error_type})")
        return False, errors
    except Exception as e:
        return False, [f"Validation error: {e}"]


def main():
    """Main function."""
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python validate_agent_card.py <agent_card_url> [api_key]")
        print("Example: python validate_agent_card.py http://localhost:8000/agents/03a42cc30121fcfb29a8aa68/card")
        sys.exit(1)
    
    agent_card_url = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("A2A_REGISTRY_API_KEY", "dev-admin-api-key")
    
    print(f"🔍 Validating agent card: {agent_card_url}")
    print("=" * 70)
    
    is_valid, errors = validate_agent_card(agent_card_url, api_key)
    
    if is_valid:
        print("✅ Agent card is VALID against A2A Card Spec schema!")
        print("\nCard structure:")
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            response = requests.get(agent_card_url, headers=headers, timeout=10)
            card_data = response.json()
            print(json.dumps(card_data, indent=2))
        except Exception:
            pass
        return 0
    else:
        print("❌ Agent card validation FAILED!")
        print(f"\nFound {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

