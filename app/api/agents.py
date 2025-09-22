"""Agent API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, HttpUrl

from ..auth_jwks import extract_context, require_oauth, require_roles
from ..core.caching import AgentCache, CacheManager
from ..core.logging import get_logger
from ..services.agent_service import AgentService
from ..services.card_service import CardService
from ..services.registry_service import RegistryService

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


class PublishByUrl(BaseModel):
    cardUrl: HttpUrl
    public: bool = Field(default=True)


class PublishByCard(BaseModel):
    public: bool = Field(default=True)
    card: Dict[str, Any]


@router.get("/public")
def public_agents(top: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0)) -> Dict[str, Any]:
    """
    Get public agents with caching and fallback mechanisms.

    Returns a paginated list of public agents with proper error handling.
    Falls back to database-only response if caching fails.
    """
    # Default response structure
    default_response = {
        "items": [],
        "count": 0,
        "next": f"/agents/public?skip={skip+top}&top={top}",
    }

    # Try to get cached data first
    try:
        cache = AgentCache(CacheManager())
        cache_key = f"agents:public:{top}:{skip}"
        cached = cache.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached
    except Exception as e:
        logger.warning(f"Cache retrieval failed: {e}", exc_info=True)
        # Continue without cache - not critical for functionality

    # Try to get data from database
    try:
        svc = RegistryService()
        items, total_count = svc.list_public(tenant_id="default", top=top, skip=skip)

        # Build response with safe data extraction
        safe_items = []
        for item in items:
            try:
                safe_items.append({"id": item.get("agentId", "unknown"), "name": item.get("name", "unknown")})
            except Exception as e:
                logger.warning(f"Failed to process agent item: {e}")
                # Skip malformed items but continue processing
                continue

        resp = {
            "items": safe_items,
            "count": len(safe_items),
            "next": f"/agents/public?skip={skip+top}&top={top}",
        }

        # Try to cache the response (non-critical)
        try:
            cache = AgentCache(CacheManager())
            cache.cache.set(cache_key, resp, ttl=300)
            logger.debug(f"Cached response for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
            # Continue without caching - response is still valid

        return resp

    except Exception as e:
        logger.error(f"Database query failed: {e}", exc_info=True)
        # Return default response instead of failing completely
        return default_response


@router.get("/entitled")
async def get_entitled_agents(
    top: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0), payload=Depends(require_oauth)
):
    """
    Get entitled agents for the authenticated client with error handling.

    Returns a paginated list of agents the client is entitled to access.
    Falls back to empty list if database query fails.
    """
    # Default response structure
    default_response = {
        "items": [],
        "count": 0,
        "next": f"/agents/entitled?skip={skip+top}&top={top}",
    }

    try:
        # Extract context with error handling
        ctx = extract_context(payload)
        tenant = ctx.get("tenant") or "default"
        client_id = ctx.get("client_id") or "unknown"

        logger.debug(f"Getting entitled agents for tenant={tenant}, client_id={client_id}")

        # Query database with error handling
        registry_service = RegistryService()
        items, count = registry_service.list_entitled(tenant, client_id, top, skip)

        # Validate and sanitize response data
        safe_items = []
        if isinstance(items, list):
            for item in items:
                try:
                    # Ensure item is a dictionary and has required fields
                    if isinstance(item, dict):
                        safe_items.append(item)
                    else:
                        logger.warning(f"Invalid item type in entitled agents: {type(item)}")
                except Exception as e:
                    logger.warning(f"Failed to process entitled agent item: {e}")
                    continue

        response = {
            "items": safe_items,
            "count": count if isinstance(count, int) else len(safe_items),
            "next": f"/agents/entitled?skip={skip+top}&top={top}",
        }

        logger.debug(f"Successfully retrieved {len(safe_items)} entitled agents")
        return response

    except Exception as e:
        logger.error(f"Failed to get entitled agents: {e}", exc_info=True)
        # Return default response instead of failing completely
        return default_response


@router.get("/{agent_id}")
async def get_agent(agent_id: str, payload=Depends(require_oauth)):
    """
    Get latest agent version by ID with entitlement enforcement and error handling.

    Returns agent details with proper error handling and fallbacks.
    """
    try:
        # Extract context with error handling
        ctx = extract_context(payload)
        tenant = ctx.get("tenant") or "default"
        client_id = ctx.get("client_id")

        logger.debug(f"Getting agent {agent_id} for tenant={tenant}, client_id={client_id}")

        # Validate agent_id
        if not agent_id or not isinstance(agent_id, str):
            logger.warning(f"Invalid agent_id provided: {agent_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent ID")

        # Use service layer for database operations
        agent_service = AgentService()
        row = agent_service.get_agent_by_id(agent_id, tenant)

        if not row:
            logger.info(f"Agent {agent_id} not found for tenant {tenant}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        rec, ver = row

        # Validate retrieved data
        if not rec or not ver:
            logger.error(f"Invalid data structure returned for agent {agent_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid agent data")

        # Check entitlement for private agents
        if not ver.public:
            if not client_id:
                logger.warning(f"Client ID missing for private agent {agent_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: authentication required"
                )

            try:
                if not agent_service.check_agent_access(agent_id, tenant, client_id):
                    logger.info(f"Client {client_id} not entitled to private agent {agent_id}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: insufficient permissions"
                    )
            except Exception as e:
                logger.error(f"Entitlement check failed for agent {agent_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to verify access permissions"
                )

        # Build response with safe data extraction
        try:
            card_json = ver.card_json or {}
            response = {
                "agentId": rec.id,
                "name": card_json.get("name", "Unknown"),
                "description": card_json.get("description", ""),
                "publisherId": rec.publisher_id or "unknown",
                "version": ver.version or "unknown",
                "protocolVersion": ver.protocol_version or "unknown",
                "capabilities": card_json.get("capabilities", {}),
                "skills": card_json.get("skills", []),
            }

            logger.debug(f"Successfully retrieved agent {agent_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to build response for agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to process agent data"
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving agent {agent_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{agent_id}/card")
async def get_agent_card(agent_id: str, payload=Depends(require_oauth)):
    """
    Get an agent's card data with comprehensive error handling.

    Returns the agent card JSON with proper error handling and fallbacks.
    """
    try:
        # Validate agent_id
        if not agent_id or not isinstance(agent_id, str):
            logger.warning(f"Invalid agent_id provided for card: {agent_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent ID")

        logger.debug(f"Getting card for agent {agent_id}")

        # Use service layer for database operations
        agent_service = AgentService()
        result = agent_service.get_agent_by_id(agent_id, "default")

        if not result:
            logger.info(f"Agent {agent_id} not found for card retrieval")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        agent_record, agent_version = result

        # Validate retrieved data
        if not agent_record or not agent_version:
            logger.error(f"Invalid data structure returned for agent {agent_id} card")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid agent data")

        # Check if agent is public or if client has access
        if not agent_version.public:
            try:
                # Extract context with error handling
                ctx = extract_context(payload)
                tenant = ctx.get("tenant") or "default"
                client_id = ctx.get("client_id")

                logger.debug(
                    f"Checking entitlement for private agent {agent_id}, " f"tenant={tenant}, client_id={client_id}"
                )

                entitled = False
                if client_id:
                    # Check if client is entitled to this agent
                    try:
                        entitled = agent_service.check_agent_access(agent_id, tenant, client_id)
                    except Exception as e:
                        logger.error(f"Entitlement check failed for agent {agent_id}: {e}")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unable to verify access permissions",
                        )

                if not entitled:
                    logger.info(f"Client {client_id} not entitled to private agent {agent_id} card")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                logger.error(f"Failed to check entitlement for agent {agent_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to verify access permissions"
                )

        # Return card data with validation
        try:
            card_json = agent_version.card_json
            if card_json is None:
                logger.warning(f"Agent {agent_id} has no card data")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent card data not available")

            # Validate that card_json is a dictionary
            if not isinstance(card_json, dict):
                logger.error(f"Invalid card data type for agent {agent_id}: {type(card_json)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid card data format"
                )

            logger.debug(f"Successfully retrieved card for agent {agent_id}")
            return card_json

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Failed to process card data for agent {agent_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to process card data")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving card for agent {agent_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/publish", status_code=status.HTTP_201_CREATED)
def publish_agent(body: Dict[str, Any], ctx=Depends(require_roles("Administrator", "CatalogManager"))):
    """
    Publish an agent with comprehensive error handling.

    Supports publishing agents by providing card data directly or by URL.
    Includes validation, idempotency, and search indexing.
    """
    try:
        # Extract and validate input
        public = body.get("public", True)
        tenant_id = ctx.get("tenant") or "default"
        logger.debug(f"Publishing agent with public={public} for tenant {tenant_id}")

        # Parse and validate card data using service layer
        card_data, card_url, card_hash = CardService.parse_and_validate_card(body)

        # Use agent service for database operations
        agent_service = AgentService()
        result = agent_service.publish_agent(card_data, card_url, public, tenant_id)

        logger.info(f"Successfully published agent: {result['agentId']} v{result['version']}")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:
        logger.error(f"Unexpected error publishing agent: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from exc
