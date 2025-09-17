"""Production monitoring and metrics."""

import time
from typing import Any, Dict, Optional

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus metrics
REQUEST_COUNT = Counter(
    "a2a_registry_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "a2a_registry_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_CONNECTIONS = Gauge(
    "a2a_registry_active_connections", "Number of active connections"
)

AGENT_COUNT = Gauge(
    "a2a_registry_agents_total", "Total number of registered agents", ["status"]
)

CLIENT_COUNT = Gauge(
    "a2a_registry_clients_total", "Total number of registered clients", ["status"]
)

SEARCH_QUERIES = Counter(
    "a2a_registry_search_queries_total",
    "Total number of search queries",
    ["query_type"],
)

SEARCH_DURATION = Histogram(
    "a2a_registry_search_duration_seconds", "Search duration in seconds", ["query_type"]
)

PEER_SYNCS = Counter(
    "a2a_registry_peer_syncs_total",
    "Total number of peer synchronizations",
    ["peer_id", "status"],
)

DATABASE_CONNECTIONS = Gauge(
    "a2a_registry_database_connections_active", "Number of active database connections"
)

ELASTICSEARCH_CONNECTIONS = Gauge(
    "a2a_registry_elasticsearch_connections_active",
    "Number of active Elasticsearch connections",
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract endpoint from path
        endpoint = self._extract_endpoint(request.url.path)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status_code=response.status_code
        ).inc()

        REQUEST_DURATION.labels(method=request.method, endpoint=endpoint).observe(
            duration
        )

        return response

    def _extract_endpoint(self, path: str) -> str:
        """Extract endpoint pattern from path."""
        # Replace dynamic segments with placeholders
        import re

        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{id}",
            path,
        )

        # Replace other common patterns
        path = re.sub(r"/\d+", "/{id}", path)

        return path


class HealthChecker:
    """Health check service for monitoring system components."""

    def __init__(self, db_session_factory, redis_client, elasticsearch_client):
        self.db_session_factory = db_session_factory
        self.redis_client = redis_client
        self.elasticsearch_client = elasticsearch_client

    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            db = self.db_session_factory()
            db.execute(text("SELECT 1"))
            db.close()
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            return {"status": "healthy", "response_time_ms": response_time}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_elasticsearch(self) -> Dict[str, Any]:
        """Check Elasticsearch connectivity."""
        try:
            start_time = time.time()
            self.elasticsearch_client.ping()
            response_time = (time.time() - start_time) * 1000
            return {"status": "healthy", "response_time_ms": response_time}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_all(self) -> Dict[str, Any]:
        """Check all system components."""
        db_health = await self.check_database()
        redis_health = await self.check_redis()
        es_health = await self.check_elasticsearch()

        overall_status = (
            "healthy"
            if all(
                health["status"] == "healthy"
                for health in [db_health, redis_health, es_health]
            )
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "components": {
                "database": db_health,
                "redis": redis_health,
                "elasticsearch": es_health,
            },
        }


def get_metrics_response() -> Response:
    """Get Prometheus metrics response."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsCollector:
    """Collector for application-specific metrics."""

    @staticmethod
    def record_search(query_type: str, duration: float) -> None:
        """Record search metrics."""
        SEARCH_QUERIES.labels(query_type=query_type).inc()
        SEARCH_DURATION.labels(query_type=query_type).observe(duration)

    @staticmethod
    def record_peer_sync(peer_id: str, status: str) -> None:
        """Record peer sync metrics."""
        PEER_SYNCS.labels(peer_id=peer_id, status=status).inc()

    @staticmethod
    def update_agent_count(active_count: int, total_count: int) -> None:
        """Update agent count metrics."""
        AGENT_COUNT.labels(status="active").set(active_count)
        AGENT_COUNT.labels(status="total").set(total_count)

    @staticmethod
    def update_client_count(active_count: int, total_count: int) -> None:
        """Update client count metrics."""
        CLIENT_COUNT.labels(status="active").set(active_count)
        CLIENT_COUNT.labels(status="total").set(total_count)
