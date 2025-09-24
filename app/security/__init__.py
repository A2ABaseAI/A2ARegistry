"""Unified security utilities for the A2A Agent Registry.

This module consolidates password hashing, JWT/JWKS verification, API-key
authentication, rate limiting, and higher-level security services.
"""

from .dependencies import extract_context, require_oauth, require_roles
from .jwt import create_access_token, verify_access_token
from .middleware import RateLimitMiddleware, RequestSizeLimitMiddleware
from .passwords import hash_password, verify_password
from .service import (
    ApiKeyInfo,
    AuthMethod,
    JwtTokenInfo,
    SecurityEvent,
    SecurityLevel,
    SecurityService,
    get_security_service,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_access_token",
    "require_oauth",
    "require_roles",
    "extract_context",
    "RateLimitMiddleware",
    "RequestSizeLimitMiddleware",
    "SecurityService",
    "ApiKeyInfo",
    "SecurityEvent",
    "AuthMethod",
    "SecurityLevel",
    "JwtTokenInfo",
    "get_security_service",
]
