"""
Utility functions for the A2A Host Orchestrator.
"""

from typing import Any, Dict, List, Optional

from a2a_reg_sdk import Agent

from .models import A2AAgentCard


def merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with updates taking precedence."""
    result = base.copy()
    result.update(updates)
    return result


def agent_to_card(agent: Agent) -> A2AAgentCard:
    """
    Convert SDK Agent to runner A2AAgentCard.

    Extracts skills from agent's skills list (using tags from skills).
    Uses agent tags for additional routing keywords.
    """
    # Extract skills/tags for routing
    skills: List[str] = []

    # Add tags from agent
    if agent.tags:
        skills.extend(agent.tags)

    # Add tags from skills
    if agent.skills:
        for skill in agent.skills:
            if skill.tags:
                skills.extend(skill.tags)

    # Extract domain from tags or provider
    domain = None
    if agent.tags:
        # Try to infer domain from tags (first tag is often domain-like)
        for tag in agent.tags:
            if tag.lower() in ["ecommerce", "logistics", "support", "finance", "healthcare", "education"]:
                domain = tag.lower()
                break

    # Extract endpoint from location_url or agent_card
    endpoint = agent.location_url

    # Try to get endpoint from agent_card interface
    if agent.agent_card and agent.agent_card.interface:
        if agent.agent_card.interface.additionalInterfaces:
            # Use first additional interface URL with http transport
            for iface in agent.agent_card.interface.additionalInterfaces:
                if isinstance(iface, dict):
                    if iface.get("transport") == "http" and iface.get("url"):
                        endpoint = iface["url"]
                        break
                else:
                    if getattr(iface, "transport", None) == "http" and getattr(iface, "url", None):
                        endpoint = getattr(iface, "url")
                        break
        # Fall back to agent_card URL
        if not endpoint and agent.agent_card.url:
            endpoint = agent.agent_card.url

    # If still no endpoint, try from agent_card.url directly
    if not endpoint and agent.agent_card and agent.agent_card.url:
        endpoint = agent.agent_card.url

    # Don't convert /api/agent to /chat - mock agents and many agents use /api/agent
    # Only convert if we explicitly know it should be /chat (e.g., from A2A protocol spec)
    # For now, keep the endpoint as-is
    # if endpoint and "/api/agent" in endpoint:
    #     endpoint = endpoint.replace("/api/agent", "/chat")
    # If endpoint still not found, try to construct from card URL
    if not endpoint and agent.agent_card and agent.agent_card.url:
        base_url = agent.agent_card.url.rstrip("/")
        # Remove /api/agent if present, replace with /chat
        if "/api/agent" in base_url:
            endpoint = base_url.replace("/api/agent", "/chat")
        else:
            # Try common A2A endpoints
            endpoint = f"{base_url}/chat"

    # Final fallback - skip if no endpoint found
    if not endpoint or endpoint == "https://example.com":
        # Don't set a default - let the caller handle it
        endpoint = ""

    # Priority based on agent metadata or default
    priority = 10
    if agent.tags:
        # Lower priority for more specialized agents (fewer tags = more specialized)
        priority = max(5, 15 - len(agent.tags))

    # Build auth dict from auth_schemes
    auth: Optional[Dict[str, Any]] = None
    if agent.auth_schemes:
        auth = {}
        for scheme in agent.auth_schemes:
            auth[scheme.type] = {
                "location": getattr(scheme, "location", "header"),
                "name": getattr(scheme, "name", "Authorization"),
            }

    # Build metadata - include full agent_card with URL for RemoteA2aAgent
    metadata: Dict[str, Any] = {
        "version": agent.version,
        "provider": agent.provider,
    }
    if agent.agent_card:
        try:
            if hasattr(agent.agent_card, "to_dict"):
                metadata["agent_card"] = agent.agent_card.to_dict()
            else:
                # Fallback for AgentCardSpec - preserve the URL from registry
                metadata["agent_card"] = {
                    "name": getattr(agent.agent_card, "name", None),
                    "description": getattr(agent.agent_card, "description", None),
                    "url": getattr(agent.agent_card, "url", None),  # This is the agent card URL from registry
                    "interface": getattr(agent.agent_card, "interface", None),
                }
        except Exception:
            metadata["agent_card"] = {}

    # Return None if no endpoint found - let caller skip this agent
    if not endpoint:
        return None

    return A2AAgentCard(
        id=agent.id or agent.name.lower().replace(" ", "-"),
        name=agent.name,
        description=agent.description,
        skills=list(set(skills)),  # Remove duplicates
        domain=domain,
        priority=priority,
        endpoint=endpoint,
        method="POST",
        metadata=metadata,
        auth=auth,
    )
