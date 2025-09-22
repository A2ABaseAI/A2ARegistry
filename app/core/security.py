"""Security utilities for authentication and authorization."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2."""
    salt = secrets.token_bytes(32)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = kdf.derive(password.encode())
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        kdf.verify(password.encode(), key)
        return True
    except Exception:
        return False


def create_access_token(
    user_id: str, username: str, email: str, roles: List[str], tenant_id: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    # Create token payload
    payload = {
        "iss": settings.token_issuer or "a2a-registry",
        "aud": settings.token_audience or "a2a-registry",
        "sub": user_id,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "nbf": int(datetime.now(timezone.utc).timestamp()),
        # A2A Registry specific claims
        "user_id": user_id,
        "username": username,
        "email": email,
        "client_id": user_id,
        "roles": roles,
        "tenant": tenant_id,
    }

    # Create token with HS256 (simpler for internal use)
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    return token


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            audience=settings.token_audience or "a2a-registry",
            issuer=settings.token_issuer or "a2a-registry",
            options={
                "verify_exp": True,
                "verify_aud": bool(settings.token_audience),
                "verify_iss": bool(settings.token_issuer),
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


def require_oauth(credentials: Optional[HTTPBearer] = None) -> Dict[str, Any]:
    """Require OAuth authentication."""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return verify_access_token(credentials.credentials)


def extract_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract context from JWT payload."""
    roles = payload.get(settings.role_claim, [])
    tenant = payload.get(settings.tenant_claim)
    client_id = (
        payload.get(settings.client_id_claim)
        or payload.get("client_id")
        or payload.get("sub")
        or payload.get("user_id")
    )
    return {"roles": roles, "tenant": tenant, "client_id": client_id}


def require_roles(*required_roles: str):
    """Require specific roles for access."""

    def _dep(payload: Dict[str, Any] = Depends(require_oauth)) -> Dict[str, Any]:
        ctx = extract_context(payload)
        roles = set(ctx.get("roles") or [])
        if not roles.intersection(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return ctx

    return _dep


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, redis_client: Optional[Any] = None):
        super().__init__(app)
        self.redis_client = redis_client
        # Default limits (req/min) - tighten/write-heavy endpoints
        self.default_limit = 200
        self.limit_by_endpoint = {
            "/agents/search": 120,
            "/agents/publish": 30,
            "/.well-known/agents/index.json": 300,
            "/auth/login": 10,  # Stricter limit for login
            "/auth/register": 5,  # Very strict limit for registration
        }

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (tenant-aware) for fair limiting
        client_id, tenant = self._get_client_and_tenant(request)

        # Get rate limit for endpoint
        limit = self.limit_by_endpoint.get(request.url.path, self.default_limit)

        # Check rate limit
        if not await self._check_rate_limit(tenant or "default", client_id, request.url.path, limit, request):
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_id": client_id,
                    "tenant": tenant,
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

    def _get_client_and_tenant(self, request: Request) -> tuple[str, Optional[str]]:
        """Extract client ID and tenant from request."""
        # Try to get from Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header[7:]
                payload = verify_access_token(token)
                ctx = extract_context(payload)
                return ctx.get("client_id", "anonymous"), ctx.get("tenant")
            except Exception:
                pass

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return client_ip, None

    async def _check_rate_limit(self, tenant: str, client_id: str, endpoint: str, limit: int, request: Request) -> bool:
        """Check if client is within rate limit (per-tenant, per-endpoint)."""
        # Use the Redis client passed to the middleware constructor
        redis_client = self.redis_client
        if not redis_client:
            return True  # Allow request if Redis is not available

        # Check if Redis client is actually connected
        try:
            redis_client.ping()
        except Exception:
            return True  # Allow request if Redis is not connected

        key = f"rl:{tenant}:{client_id}:{endpoint}"

        try:
            # Fixed window counter (1 minute)
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            results = pipe.execute()
            current = results[0]  # First result is the incremented value
            if current == 1:
                # TTL already set above; keep branch for clarity
                pass

            return current <= limit
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request if Redis is down


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Request size limiting middleware."""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
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

        response = await call_next(request)
        return response
