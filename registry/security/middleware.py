"""Security middleware for rate limiting and request size enforcement."""

import logging
import os
from typing import Any, Optional, Tuple

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings
from .jwt import verify_access_token

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with tenant-aware keys."""

    def __init__(self, app, redis_client: Optional[Any] = None):
        super().__init__(app)
        self.redis_client = redis_client

        test_mode = os.environ.get("TEST_MODE", "false").lower() == "true" or settings.test_mode
        if test_mode:
            self.default_limit = 1000
            self.limit_by_endpoint = {
                "/agents/search": 2000,
                "/agents/publish": 1000,
                "/agents/public": 2000,
                "/.well-known/agents/index.json": 2000,
                "/auth/login": 1000,
                "/auth/register": 1000,
                "/auth/oauth/token": 500,
            }
        else:
            self.default_limit = 100
            self.limit_by_endpoint = {
                "/agents/search": 200,
                "/agents/publish": 50,
                "/agents/public": 200,
                "/.well-known/agents/index.json": 200,
                "/auth/login": 20,
                "/auth/register": 10,
                "/auth/oauth/token": 50,
            }

    async def dispatch(self, request: Request, call_next):
        client_id, tenant = self._get_client_and_tenant(request)
        limit = self.limit_by_endpoint.get(request.url.path, self.default_limit)

        allowed = await self._check_rate_limit(tenant or "default", client_id, request.url.path, limit)
        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                extra={"client_id": client_id, "tenant": tenant, "endpoint": request.url.path, "limit": limit},
            )
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)

    def _get_client_and_tenant(self, request: Request) -> Tuple[str, Optional[str]]:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = verify_access_token(token)
                client_id = payload.get("client_id") or payload.get("sub") or "anonymous"
                tenant = payload.get("tenant")
                return client_id, tenant
            except Exception:  # nosec B110 - Best-effort token extraction, fallback to IP
                pass

        client_ip = request.client.host if request.client else "unknown"
        return client_ip, None

    async def _check_rate_limit(
        self,
        tenant: str,
        client_id: str,
        endpoint: str,
        limit: int,
    ) -> bool:
        redis_client = self.redis_client
        if not redis_client:
            return True

        try:
            redis_client.ping()
        except Exception:
            return True

        key = f"rl:{tenant}:{client_id}:{endpoint}"

        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            current = pipe.execute()[0]
            return bool(current <= limit)
        except Exception as exc:  # pragma: no cover - redis edge cases
            logger.error("Rate limit check failed", extra={"error": str(exc)})
            return True


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing a maximum request body size."""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return Response(
                content='{"error": "Request too large"}',
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                media_type="application/json",
            )

        return await call_next(request)
