"""Health check and monitoring endpoints."""

from typing import Any, Dict

import redis
from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..core.logging import get_logger
from ..core.monitoring import HealthChecker, get_metrics_response
from ..database import get_db

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "a2a-registry",
        "version": settings.app_version,
        "timestamp": "2025-01-16T10:00:00Z",
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies all dependencies are available."""

    health_status = {
        "status": "ready",
        "service": "a2a-registry",
        "version": settings.app_version,
        "checks": {},
    }

    all_healthy = True

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    # Check Elasticsearch
    try:
        es_client = Elasticsearch([settings.elasticsearch_url])
        es_client.ping()
        health_status["checks"]["elasticsearch"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["elasticsearch"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        all_healthy = False

    if not all_healthy:
        health_status["status"] = "not_ready"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """Liveness check - verifies the application is running."""
    return {
        "status": "alive",
        "service": "a2a-registry",
        "version": settings.app_version,
        "uptime": "running",
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with comprehensive system status."""

    # Initialize health checker
    redis_client = redis.from_url(settings.redis_url)
    es_client = Elasticsearch([settings.elasticsearch_url])
    health_checker = HealthChecker(
        db_session_factory=lambda: db,
        redis_client=redis_client,
        elasticsearch_client=es_client,
    )

    # Perform comprehensive health checks
    health_status = await health_checker.check_all()

    # Add additional application-specific checks
    try:
        # Check agent count
        from ..services.agent_service import AgentService

        agent_service = AgentService(db)
        agent_count = agent_service.get_agent_count()
        health_status["metrics"] = {
            "total_agents": agent_count,
            "active_agents": len(
                agent_service.list_agents(is_active=True, limit=10000)
            ),
            "public_agents": len(agent_service.get_public_agents()),
        }
    except Exception as e:
        health_status["metrics"] = {"error": str(e)}

    # Add system information
    import psutil

    health_status["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }

    return health_status


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return get_metrics_response()


@router.get("/status", response_model=Dict[str, Any])
async def status_check(db: Session = Depends(get_db)):
    """Status check with business logic validation."""

    status_info = {
        "status": "operational",
        "service": "a2a-registry",
        "version": settings.app_version,
        "features": {
            "federation": settings.enable_federation,
            "search": True,
            "authentication": True,
        },
    }

    # Check if core functionality is working
    try:
        from ..services.agent_service import AgentService
        from ..services.client_service import ClientService

        agent_service = AgentService(db)
        client_service = ClientService(db)

        # Verify we can perform basic operations
        agent_count = agent_service.get_agent_count()
        client_count = len(client_service.list_clients(limit=1))

        status_info["operational_metrics"] = {
            "agents_registered": agent_count,
            "clients_registered": client_count,
            "search_index_available": True,
        }

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        status_info["status"] = "degraded"
        status_info["issues"] = [str(e)]

    return status_info
