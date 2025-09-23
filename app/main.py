"""Main FastAPI application."""

from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from opensearchpy import OpenSearch

from .api import agents, auth, health, well_known
from .api.search import router as search_router
from .config import settings
from .core import (
    MetricsMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    RequestSizeLimitMiddleware,
    get_logger,
    handle_generic_exception,
    setup_logging,
)
from .core.otel import setup_tracing
from .database import SessionLocal, create_tables
from .models.tenant import Tenant
from .services.search_index import SearchIndex

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    setup_tracing(settings.app_name)

    # Create database tables (dev-only). Use Alembic in production.
    if settings.auto_create_tables:
        create_tables()
        # Ensure default tenant exists for dev/demo
        try:
            db = SessionLocal()
            if not db.query(Tenant).filter(Tenant.id == "default").first():
                db.add(Tenant(id="default", slug="default"))
                db.commit()
        except Exception as e:
            logger.warning(f"Failed to ensure default tenant: {e}")
        finally:
            try:
                db.close()
            except Exception:
                pass

    # Initialize search index (dev-only). Use infra provisioning in production.
    if settings.auto_create_index:
        try:
            SearchIndex().ensure_index()
        except Exception as e:
            logger.warning(f"Failed to create search index: {e}")

    # Initialize Redis and Elasticsearch connections
    redis_client = redis.from_url(settings.redis_url)
    es_client = OpenSearch([settings.opensearch_url])

    # Store clients in app state for middleware
    app.state.redis_client = redis_client
    app.state.es_client = es_client

    yield

    # Shutdown
    redis_client.close()
    es_client.close()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=("A2A Agent Registry - Centralized agent discovery and management system"),
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

# Add production middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB

# Add rate limiting middleware
redis_client = redis.from_url(settings.redis_url)
app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(well_known.router, prefix="/.well-known")
app.include_router(health.router)
app.include_router(search_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with registry information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": ("A2A Agent Registry - Centralized agent discovery and management"),
        "endpoints": {
            "agents": "/agents",
            "well_known": "/.well-known",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
        "registry_info": {
            "base_url": settings.registry_base_url,
            "federation_enabled": settings.enable_federation,
            "max_agents_per_client": settings.max_agents_per_client,
        },
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "federation_enabled": settings.enable_federation,
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    request_id = request.headers.get("X-Request-ID")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    request_id = request.headers.get("X-Request-ID")
    http_exc = handle_generic_exception(exc, request_id or "")
    return JSONResponse(status_code=http_exc.status_code, content=http_exc.detail)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
