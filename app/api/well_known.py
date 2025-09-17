"""Well-known endpoints for agent discovery."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_client_optional
from ..database import get_db
from ..schemas.agent import AgentCard
from ..services.agent_service import AgentService

router = APIRouter(tags=["well-known"])


@router.get("/.well-known/agents/index.json", response_model=Dict[str, Any])
async def get_agents_index(db: Session = Depends(get_db)):
    """Get the agents index for this registry."""
    agent_service = AgentService(db)
    public_agents = agent_service.get_public_agents()

    agents_list = []
    for agent in public_agents:
        agents_list.append(
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description or "",
                "provider": agent.provider,
                "tags": agent.tags or [],
                "location": {"url": f"/agents/{agent.id}/card", "type": "agent_card"},
            }
        )

    return {
        "registry_version": "1.0",
        "registry_name": "A2A Agent Registry",
        "agents": agents_list,
        "total_count": len(agents_list),
    }


@router.get("/.well-known/agent.json", response_model=AgentCard)
async def get_registry_agent_card(db: Session = Depends(get_db)):
    """Get the registry's own agent card."""
    # This represents the registry as an agent itself
    return AgentCard(
        id="a2a-registry",
        name="A2A Agent Registry",
        version="1.0.0",
        description="Centralized registry for A2A agent discovery and management",
        capabilities={
            "a2a_version": "1.0",
            "supported_protocols": ["http", "https"],
            "max_concurrent_requests": 1000,
            "timeout_seconds": 30,
            "rate_limit_per_minute": 10000,
        },
        skills={
            "agent_discovery": {
                "description": "Discover and search for available agents",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {"type": "object"},
                    },
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "agents": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/AgentCard"},
                        }
                    },
                },
            },
            "agent_management": {
                "description": "Manage agent registrations and entitlements",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["register", "update", "delete"],
                        },
                        "agent_data": {"type": "object"},
                    },
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "agent_id": {"type": "string"},
                    },
                },
            },
        },
        auth_schemes=[
            {
                "type": "oauth2",
                "flow": "client_credentials",
                "token_url": "/oauth/token",
                "scopes": ["agent:read", "agent:write", "client:manage"],
            },
            {"type": "apiKey", "location": "header", "name": "X-API-Key"},
        ],
        provider="A2A Community",
        tags=["registry", "discovery", "management", "federation"],
        location={"url": "/.well-known/agent.json", "type": "agent_card"},
    )


@router.get("/agents/{agent_id}/card", response_model=AgentCard)
async def get_agent_card_well_known(
    agent_id: str,
    current_client=Depends(get_current_client_optional),
    db: Session = Depends(get_db),
):
    """Get an agent card via well-known endpoint."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Check access permissions
    if not agent.is_public and not current_client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required for private agents",
        )

    if not agent.is_public and current_client:
        from ..services.client_service import ClientService

        client_service = ClientService(db)
        entitlements = client_service.get_client_entitlements(current_client.id)
        agent_entitled = any(ent.agent_id == agent_id for ent in entitlements)

        if not agent_entitled and agent.client_id != current_client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this agent",
            )

    return agent.to_agent_card()


@router.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent_info_well_known(
    agent_id: str,
    current_client=Depends(get_current_client_optional),
    db: Session = Depends(get_db),
):
    """Get basic agent information via well-known endpoint."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Check access permissions (same as card endpoint)
    if not agent.is_public and not current_client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required for private agents",
        )

    if not agent.is_public and current_client:
        from ..services.client_service import ClientService

        client_service = ClientService(db)
        entitlements = client_service.get_client_entitlements(current_client.id)
        agent_entitled = any(ent.agent_id == agent_id for ent in entitlements)

        if not agent_entitled and agent.client_id != current_client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this agent",
            )

    return {
        "id": agent.id,
        "name": agent.name,
        "version": agent.version,
        "description": agent.description or "",
        "provider": agent.provider,
        "tags": agent.tags or [],
        "is_public": agent.is_public,
        "is_active": agent.is_active,
        "location": {"url": f"/agents/{agent.id}/card", "type": "agent_card"},
        "capabilities": agent.capabilities or {},
        "auth_schemes": agent.auth_schemes or [],
        "tee_details": agent.tee_details,
    }
