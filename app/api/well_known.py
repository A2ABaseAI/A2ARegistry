"""Well-known endpoints for agent discovery."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth_jwks import extract_context, require_oauth
from ..core.logging import get_logger
from ..services.registry_service import RegistryService

logger = get_logger(__name__)

router = APIRouter(tags=["well-known"])


@router.get("/agents/index.json", response_model=Dict[str, Any])
async def get_agents_index(
    top: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """
    Get the agents index for this registry.

    Production-ready endpoint with comprehensive error handling
    and graceful degradation.
    """
    default_response = {
        "registry_version": "1.0",
        "registry_name": "A2A Agent Registry",
        "agents": [],
        "count": 0,
        "total_count": 0,
        "next": None,
        "error": "Service temporarily unavailable",
    }

    try:
        logger.debug(f"Agents index request: top={top}, skip={skip}")

        # Validate input parameters
        if top < 1 or top > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="top parameter must be between 1 and 100"
            )

        if skip < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="skip parameter must be non-negative")

        # Get agents from registry service
        try:
            registry_service = RegistryService()
            agents, total = registry_service.list_public(tenant_id="default", top=top, skip=skip)
            logger.debug(f"Retrieved {len(agents)} agents from registry")
        except Exception as e:
            logger.error(f"Failed to retrieve agents from registry: {e}")
            return default_response

        # Build agents list with safe data extraction
        agents_list = []
        for agent in agents:
            try:
                agents_list.append(
                    {
                        "id": agent.get("agentId", "unknown"),
                        "name": agent.get("name") or "unknown",
                        "description": agent.get("description") or "Agent from registry",
                        "provider": agent.get("publisherId"),
                        "tags": [],
                        "location": {"url": f"/agents/{agent.get('agentId', 'unknown')}/card", "type": "agent_card"},
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to process agent: {e}")
                # Skip malformed agents but continue processing
                continue

        response = {
            "registry_version": "1.0",
            "registry_name": "A2A Agent Registry",
            "agents": agents_list,
            "count": len(agents_list),
            "total_count": total,
            "next": (f"/.well-known/agents/index.json?skip={skip+top}&top={top}" if skip + top < total else None),
        }

        logger.debug(f"Returning agents index with {len(agents_list)} agents")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in agents index endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving agents index",
        )


@router.get("/agents/{agent_id}/card")
async def get_agent_card_well_known(
    agent_id: str,
    payload=Depends(require_oauth),
):
    """
    Get an agent card via well-known endpoint.

    Production-ready endpoint with comprehensive error handling,
    access control, and graceful degradation.
    """
    try:
        logger.debug(f"Agent card request for agent_id: {agent_id}")

        # Validate agent_id
        if not agent_id or not agent_id.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent ID is required")

        # Get agent from registry service
        try:
            registry_service = RegistryService()
            result = registry_service.get_latest("default", agent_id)
        except Exception as e:
            logger.error(f"Failed to retrieve agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while retrieving agent"
            )

        if not result:
            logger.info(f"Agent {agent_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        agent_record, agent_version = result

        # Validate agent data structure
        if not agent_record or not agent_version:
            logger.error(f"Invalid data structure for agent {agent_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid agent data")

        # Check access permissions (public, owner, or entitled)
        if not agent_version.public:
            logger.debug(f"Agent {agent_id} is private, checking access permissions")

            try:
                ctx = extract_context(payload)
                tenant = ctx.get("tenant") or "default"
                client_id = ctx.get("client_id")

                entitled = False
                if client_id:
                    try:
                        entitled = registry_service.is_entitled(tenant, client_id, agent_id)
                        logger.debug(f"Entitlement check for {client_id} on {agent_id}: {entitled}")
                    except Exception as e:
                        logger.warning(f"Entitlement check failed: {e}")
                        # If entitlement check fails, deny access for security
                        entitled = False

                if not entitled:
                    logger.info(f"Access denied for client {client_id} to private agent {agent_id}")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error checking access permissions: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error while checking permissions",
                )

        # Validate card data
        card_json = agent_version.card_json
        if card_json is None:
            logger.warning(f"Agent {agent_id} has no card data")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent card data not available")

        if not isinstance(card_json, dict):
            logger.error(f"Invalid card data type for agent {agent_id}: {type(card_json)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid card data format")

        logger.debug(f"Successfully retrieved card for agent {agent_id}")
        return card_json

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in agent card endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving agent card",
        )
