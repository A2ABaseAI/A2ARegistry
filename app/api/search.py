"""Search endpoints using OpenSearch/Meilisearch."""

import hashlib
import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..security import extract_context, require_oauth
from ..core.caching import CacheManager
from ..core.logging import get_logger
from ..services.registry_service import RegistryService
from ..services.search_index import SearchIndex

logger = get_logger(__name__)


router = APIRouter(prefix="/agents", tags=["agents"])


class SearchBody(BaseModel):
    q: Optional[str] = Field(default=None)
    filters: Dict[str, Any] = Field(default_factory=dict)
    top: int = Field(default=20, ge=1, le=100)
    skip: int = Field(default=0, ge=0)


@router.post("/search")
def search_agents(body: SearchBody, payload: dict = Depends(require_oauth)) -> Dict[str, Any]:
    """
    Search for agents with caching and fallback mechanisms.

    Production-ready endpoint with comprehensive error handling,
    caching, and graceful degradation.
    """
    default_response = {"items": [], "count": 0, "error": "Search service temporarily unavailable"}

    try:
        # Extract tenant context
        ctx = extract_context(payload)
        tenant = ctx.get("tenant") or "default"

        logger.debug(f"Search request from tenant: {tenant}, query: {body.q}")

        # Validate input parameters
        if body.top < 1 or body.top > 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="top parameter must be between 1 and 100")

        if body.skip < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="skip parameter must be non-negative")

        # Generate cache key
        cache_key = _generate_cache_key(tenant, body)

        # Try cache first
        try:
            cache = CacheManager()
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for search key: {cache_key}")
                return cached  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            # Continue without cache - not critical for functionality

        # Try search backend first
        try:
            idx = SearchIndex()
            idx.ensure_index()
            items, total = idx.search(tenant, body.q, body.filters or {}, body.top, body.skip)
            resp = {"items": items, "count": total}
            logger.debug(f"Search backend returned {len(items)} items")
        except Exception as e:
            logger.warning(f"Search backend failed: {e}, falling back to database")
            # Fallback to database
            try:
                svc = RegistryService()
                items, total = svc.list_public(tenant, top=body.top, skip=body.skip)
                resp = {"items": items, "count": total}
                logger.debug(f"Database fallback returned {len(items)} items")
            except Exception as db_e:
                logger.error(f"Database fallback also failed: {db_e}")
                return default_response

        # Cache the response (non-critical)
        try:
            cache = CacheManager()  # Re-initialize cache if it failed before
            cache.set(cache_key, resp, ttl=60)
            logger.debug(f"Cached search response for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
            # Continue without caching - response is still valid

        return resp

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during search")


def _generate_cache_key(tenant: str, body: SearchBody) -> str:
    """Generate a cache key for the search request."""
    try:
        # Create a deterministic hash of the search parameters
        search_data = {"q": body.q, "filters": body.filters or {}, "top": body.top, "skip": body.skip}
        key_hash = hashlib.sha256(json.dumps(search_data, sort_keys=True).encode()).hexdigest()
        return f"agents:search:{tenant}:{key_hash}"
    except Exception as e:
        logger.warning(f"Failed to generate cache key: {e}")
        # Fallback to a simple key
        return f"agents:search:{tenant}:{body.top}:{body.skip}"
