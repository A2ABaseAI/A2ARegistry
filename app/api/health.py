"""Health check and monitoring endpoints."""

from typing import Any, Dict
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ..config import settings
from ..core.logging import get_logger
from ..core.monitoring import HealthChecker, get_metrics_response

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "a2a-registry",
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check():
    """Readiness check - verifies all dependencies are available."""
    
    # Initialize health checker (manages its own connections)
    health_checker = HealthChecker()

    # Perform health checks
    health_status = await health_checker.check_all()
    
    # Add service metadata
    health_status.update({
        "service": "a2a-registry",
        "version": settings.app_version,
    })

    # Check if all components are healthy
    if health_status["status"] != "healthy":
        health_status["status"] = "not_ready"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    health_status["status"] = "ready"
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
async def detailed_health_check():
    """Detailed health check with comprehensive system status."""

    # Initialize health checker (manages its own connections)
    health_checker = HealthChecker()

    # Perform comprehensive health checks
    health_status = await health_checker.check_all()

    # Add additional application-specific checks
    try:
        # Check agent count
        from ..services.registry_service import RegistryService

        registry_service = RegistryService()
        agents, _ = registry_service.list_public(tenant_id="default", top=1, skip=0)
        agent_count = len(agents)
        health_status["metrics"] = {
            "total_agents": agent_count,
            "active_agents": agent_count,
            "public_agents": agent_count,
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
async def status_check():
    """Status check with business logic validation."""

    status_info = {
        "status": "operational",
        "service": "a2a-registry",
        "version": settings.app_version,
        "features": {
            "federation": False,  # Federation not implemented yet
            "search": True,
            "authentication": True,
        },
    }

    # Check system health using HealthChecker
    try:
        health_checker = HealthChecker()
        health_status = await health_checker.check_all()
        
        # If any component is unhealthy, mark as degraded
        if health_status["status"] != "healthy":
            status_info["status"] = "degraded"
            status_info["health_issues"] = health_status["components"]

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status_info["status"] = "degraded"
        status_info["health_issues"] = {"error": str(e)}

    # Check if core functionality is working
    try:
        from ..services.registry_service import RegistryService
        registry_service = RegistryService()

        # Verify we can perform basic operations
        agents, _ = registry_service.list_public(tenant_id="default", top=1, skip=0)
        agent_count = len(agents)

        status_info["operational_metrics"] = {
            "agents_registered": agent_count,
            "search_index_available": True,
        }

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        status_info["status"] = "degraded"
        status_info["issues"] = [str(e)]

    return status_info
