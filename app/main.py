"""Main FastAPI application."""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import redis
from elasticsearch import Elasticsearch

from .config import settings
from .database import create_tables
from .api import agents, clients, peering, well_known, oauth, health, static, stats
from .services.search_service import SearchService
from .database import get_db
from .core import (
    setup_logging,
    RequestLoggingMiddleware,
    MetricsMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    CSPMiddleware,
    RequestSizeLimitMiddleware,
    handle_a2a_exception,
    handle_generic_exception
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    
    # Create database tables
    create_tables()
    
    # Initialize search index
    db = next(get_db())
    try:
        search_service = SearchService(db)
        search_service.create_index()
    finally:
        db.close()
    
    # Initialize Redis and Elasticsearch connections
    redis_client = redis.from_url(settings.redis_url)
    es_client = Elasticsearch([settings.elasticsearch_url])
    
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
    description="A2A Agent Registry - Centralized agent discovery and management system",
    lifespan=lifespan
)

# Add production middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSPMiddleware)
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
app.include_router(agents.router)
app.include_router(clients.router)
app.include_router(peering.router)
app.include_router(well_known.router)
app.include_router(oauth.router)
app.include_router(health.router)
app.include_router(stats.router)
app.include_router(static.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with registry information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "A2A Agent Registry - Centralized agent discovery and management",
        "endpoints": {
            "agents": "/agents",
            "clients": "/clients", 
            "peers": "/peers",
            "oauth": "/oauth",
            "well_known": "/.well-known",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "registry_info": {
            "base_url": settings.registry_base_url,
            "federation_enabled": settings.enable_federation,
            "max_agents_per_client": settings.max_agents_per_client
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "federation_enabled": settings.enable_federation
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
            "request_id": request_id
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    request_id = request.headers.get("X-Request-ID")
    http_exc = handle_generic_exception(exc, request_id)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
