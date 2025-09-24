"""FastAPI dependencies for authentication and authorization."""

import secrets
import hashlib
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings
from .jwt import verify_access_token
from .service import get_security_service

_bearer_scheme = HTTPBearer(auto_error=False)


def _build_api_key_context(source: str) -> Dict[str, Any]:
    client_id = "api-key-client"
    tenant = settings.api_key_default_tenant

    roles = list(settings.api_key_default_roles or [])

    return {
        "user_id": client_id,
        "username": client_id,
        "email": None,
        "roles": roles,
        "tenant": tenant,
        "client_id": client_id,
    }


def _validate_api_key(token: str) -> Optional[Dict[str, Any]]:
    # Plaintext keys
    for configured in settings.api_keys or []:
        if secrets.compare_digest(token, configured):
            return _build_api_key_context(source="plaintext")

    # SHA-256 hashed keys
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if settings.api_key_hashes and token_hash in settings.api_key_hashes:
        return _build_api_key_context(source="sha256")

    # Check with security service
    service = get_security_service()
    info = service.validate_api_key(token)
    if info:
        return _build_api_key_context(source="storage")

    return None


def require_oauth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """FastAPI dependency enforcing Bearer authentication via API key or JWT."""

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported authorization scheme")

    token = credentials.credentials

    api_context = _validate_api_key(token)
    if api_context:
        return api_context

    return verify_access_token(token)


def extract_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract common context fields from a JWT or API key payload."""

    roles = payload.get(settings.role_claim) or payload.get("roles") or []
    tenant = payload.get(settings.tenant_claim) or payload.get("tenant")
    client_id = payload.get(settings.client_id_claim) or payload.get("client_id") or payload.get("sub") or payload.get("user_id")

    return {"roles": roles, "tenant": tenant, "client_id": client_id}


def require_roles(*required_roles: str):
    """FastAPI dependency enforcing that the caller has at least one role."""

    def _dependency(payload: Dict[str, Any] = Depends(require_oauth)) -> Dict[str, Any]:
        context = extract_context(payload)
        roles = set(context.get("roles") or [])

        if not roles.intersection(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        return context

    return _dependency
