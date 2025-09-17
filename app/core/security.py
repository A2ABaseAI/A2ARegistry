"""Production security utilities and middleware."""

import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.logging import get_logger

logger = get_logger(__name__)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


# Rate limiting
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = 100  # requests per minute
        self.limit_by_endpoint = {
            "/agents/search": 20,
            "/oauth/token": 10,
            "/peers/sync-all": 5,
        }

    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = self._get_client_id(request)

        # Get rate limit for endpoint
        limit = self.limit_by_endpoint.get(request.url.path, self.default_limit)

        # Check rate limit
        if not await self._check_rate_limit(client_id, request.url.path, limit):
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_id": client_id,
                    "endpoint": request.url.path,
                    "limit": limit,
                },
            )
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get client ID from token
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.auth import verify_token

                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                if payload:
                    return payload.get("sub", "anonymous")
            except Exception:
                pass

        # Fallback to IP address
        return request.client.host if request.client else "unknown"

    async def _check_rate_limit(
        self, client_id: str, endpoint: str, limit: int
    ) -> bool:
        """Check if client is within rate limit."""
        key = f"rate_limit:{client_id}:{endpoint}"

        try:
            # Use sliding window counter
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, 60)  # 1 minute window

            return current <= limit
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request if Redis is down


# Input validation and sanitization
class InputValidator:
    """Input validation utilities."""

    @staticmethod
    def validate_agent_card(agent_card: Dict[str, Any]) -> List[str]:
        """Validate agent card data."""
        errors = []

        # Required fields
        required_fields = [
            "id",
            "name",
            "version",
            "description",
            "capabilities",
            "provider",
        ]
        for field in required_fields:
            if not agent_card.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate capabilities
        capabilities = agent_card.get("capabilities", {})
        if not capabilities.get("a2a_version"):
            errors.append("Missing a2a_version in capabilities")

        if not capabilities.get("supported_protocols"):
            errors.append("Missing supported_protocols in capabilities")

        # Validate auth schemes
        auth_schemes = agent_card.get("auth_schemes", [])
        if not auth_schemes:
            errors.append("At least one auth_scheme is required")

        for scheme in auth_schemes:
            if not scheme.get("type"):
                errors.append("Auth scheme missing type")

        # Validate location
        location = agent_card.get("location", {})
        if not location.get("url"):
            errors.append("Missing location URL")

        return errors

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return str(value)

        # Remove null bytes and control characters
        sanitized = "".join(char for char in value if ord(char) >= 32)

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        import re

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None


# API key management
class APIKeyManager:
    """Manage API keys for external integrations."""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def generate_api_key(self, client_id: str, scopes: List[str]) -> str:
        """Generate a new API key."""
        key = f"ak_{secrets.token_urlsafe(32)}"

        # Store key metadata
        key_data = {
            "client_id": client_id,
            "scopes": scopes,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
        }

        self.redis_client.hset(f"api_key:{key}", mapping=key_data)
        self.redis_client.expire(f"api_key:{key}", 365 * 24 * 3600)  # 1 year

        return key

    def validate_api_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key."""
        key_data = self.redis_client.hgetall(f"api_key:{key}")
        if not key_data:
            return None

        # Update last used timestamp
        self.redis_client.hset(
            f"api_key:{key}", "last_used", datetime.utcnow().isoformat()
        )

        return {
            "client_id": key_data.get("client_id"),
            "scopes": (
                key_data.get("scopes", "").split(",") if key_data.get("scopes") else []
            ),
            "created_at": key_data.get("created_at"),
            "last_used": key_data.get("last_used"),
        }

    def revoke_api_key(self, key: str) -> bool:
        """Revoke an API key."""
        return bool(self.redis_client.delete(f"api_key:{key}"))


# Content Security Policy
class CSPMiddleware(BaseHTTPMiddleware):
    """Content Security Policy middleware."""

    def __init__(self, app, policy: str = None):
        super().__init__(app)
        self.policy = policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = self.policy
        return response


# Request size limiting
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size."""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return Response(
                content='{"error": "Request body too large"}',
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                media_type="application/json",
            )

        return await call_next(request)


# Security audit logging
class SecurityAuditLogger:
    """Log security-related events."""

    def __init__(self):
        self.logger = get_logger("security")

    def log_auth_attempt(self, client_id: str, success: bool, ip_address: str = None):
        """Log authentication attempt."""
        self.logger.info(
            "Authentication attempt",
            extra={
                "client_id": client_id,
                "success": success,
                "ip_address": ip_address,
                "event_type": "auth_attempt",
            },
        )

    def log_rate_limit_exceeded(
        self, client_id: str, endpoint: str, ip_address: str = None
    ):
        """Log rate limit exceeded."""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                "client_id": client_id,
                "endpoint": endpoint,
                "ip_address": ip_address,
                "event_type": "rate_limit_exceeded",
            },
        )

    def log_suspicious_activity(self, activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        self.logger.warning(
            "Suspicious activity detected",
            extra={
                "activity": activity,
                "details": details,
                "event_type": "suspicious_activity",
            },
        )
