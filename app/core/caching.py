"""Redis caching utilities for production."""

from typing import Any, Dict, Optional

import orjson
import redis

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager."""

    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=False)
        self.default_ttl = 3600  # 1 hour

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return orjson.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = orjson.dumps(value)
            return bool(self.redis_client.setex(key, ttl, serialized_value))
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = self.get(key)
        if value is None:
            value = factory_func()
            self.set(key, value, ttl)
        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return int(self.redis_client.delete(*keys))
            return 0
        except Exception as e:
            logger.error(f"Cache pattern invalidation error for {pattern}: {e}")
            return 0


class AgentCache:
    """Agent-specific caching operations."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent from cache."""
        return self.cache.get(f"agent:{agent_id}")

    def set_agent(self, agent_id: str, agent_data: Dict, ttl: int = 3600) -> bool:
        """Cache agent data."""
        return self.cache.set(f"agent:{agent_id}", agent_data, ttl)

    def invalidate_agent(self, agent_id: str) -> bool:
        """Invalidate agent cache."""
        return self.cache.delete(f"agent:{agent_id}")

    def invalidate_all_agents(self) -> int:
        """Invalidate all agent caches."""
        return self.cache.invalidate_pattern("agent:*")

    def get_agent_search_results(self, query_hash: str) -> Optional[Dict]:
        """Get cached search results."""
        return self.cache.get(f"search:{query_hash}")

    def set_agent_search_results(self, query_hash: str, results: Dict, ttl: int = 300) -> bool:
        """Cache search results."""
        return self.cache.set(f"search:{query_hash}", results, ttl)

    def get_entitled_agents(self, client_id: str) -> Optional[list]:
        """Get cached entitled agents for client."""
        return self.cache.get(f"entitled:{client_id}")

    def set_entitled_agents(self, client_id: str, agents: list, ttl: int = 1800) -> bool:
        """Cache entitled agents for client."""
        return self.cache.set(f"entitled:{client_id}", agents, ttl)

    def invalidate_client_entitlements(self, client_id: str) -> bool:
        """Invalidate client entitlements cache."""
        return self.cache.delete(f"entitled:{client_id}")


class ClientCache:
    """Client-specific caching operations."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client from cache."""
        return self.cache.get(f"client:{client_id}")

    def set_client(self, client_id: str, client_data: Dict, ttl: int = 3600) -> bool:
        """Cache client data."""
        return self.cache.set(f"client:{client_id}", client_data, ttl)

    def invalidate_client(self, client_id: str) -> bool:
        """Invalidate client cache."""
        return self.cache.delete(f"client:{client_id}")

    def get_client_by_oauth_id(self, oauth_client_id: str) -> Optional[Dict]:
        """Get client by OAuth ID from cache."""
        return self.cache.get(f"client_oauth:{oauth_client_id}")

    def set_client_by_oauth_id(self, oauth_client_id: str, client_data: Dict, ttl: int = 3600) -> bool:
        """Cache client by OAuth ID."""
        return self.cache.set(f"client_oauth:{oauth_client_id}", client_data, ttl)

    def invalidate_client_by_oauth_id(self, oauth_client_id: str) -> bool:
        """Invalidate client cache by OAuth ID."""
        return self.cache.delete(f"client_oauth:{oauth_client_id}")


class PeerCache:
    """Peer registry caching operations."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def get_peer_agents(self, peer_id: str) -> Optional[list]:
        """Get cached peer agents."""
        return self.cache.get(f"peer_agents:{peer_id}")

    def set_peer_agents(self, peer_id: str, agents: list, ttl: int = 1800) -> bool:
        """Cache peer agents."""
        return self.cache.set(f"peer_agents:{peer_id}", agents, ttl)

    def invalidate_peer_agents(self, peer_id: str) -> bool:
        """Invalidate peer agents cache."""
        return self.cache.delete(f"peer_agents:{peer_id}")

    def get_peer_sync_status(self, peer_id: str) -> Optional[Dict]:
        """Get cached peer sync status."""
        return self.cache.get(f"peer_sync:{peer_id}")

    def set_peer_sync_status(self, peer_id: str, status: Dict, ttl: int = 300) -> bool:
        """Cache peer sync status."""
        return self.cache.set(f"peer_sync:{peer_id}", status, ttl)


# Cache decorators
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cache_manager = CacheManager()
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache
            cache_manager = CacheManager()
            cache_manager.invalidate_pattern(pattern)

            return result

        return wrapper

    return decorator


# Cache warming utilities
class CacheWarmer:
    """Warm up caches with frequently accessed data."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.agent_cache = AgentCache(cache_manager)
        self.client_cache = ClientCache(cache_manager)

    async def warm_agent_caches(self, db_session):
        """Warm up agent caches."""
        from app.services.registry_service import RegistryService

        registry_service = RegistryService(db_session)

        # Cache public agents
        public_agents, _ = registry_service.list_public(tenant_id="default", top=100, skip=0)
        for agent in public_agents:
            agent_id = agent.get("id") if isinstance(agent, dict) else agent.id
            agent_name = agent.get("latest_version") if isinstance(agent, dict) else agent.latest_version
            if agent_id:
                self.agent_cache.set_agent(str(agent_id), {"id": str(agent_id), "name": str(agent_name)})

        # Cache agent counts
        total_count = len(public_agents)
        active_count = total_count

        self.cache.set("agent_counts", {"total": total_count, "active": active_count})

        logger.info(f"Warmed agent caches: {len(public_agents)} agents")

    async def warm_client_caches(self, db_session):
        """Warm up client caches."""
        from app.services.client_service import ClientService

        client_service = ClientService(db_session)

        # Cache active clients
        clients = client_service.list_clients(limit=1000)
        for client in clients:
            self.client_cache.set_client(client.id, client.to_client_response())
            self.client_cache.set_client_by_oauth_id(client.client_id, client.to_client_response())

        logger.info(f"Warmed client caches: {len(clients)} clients")
