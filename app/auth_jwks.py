"""JWT (client-credentials) verification via JWKS with role/tenant extraction."""

import json
from functools import lru_cache
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

security = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _get_jwks() -> Dict[str, Any]:
    resp = httpx.get(settings.jwks_url, timeout=5.0)
    resp.raise_for_status()
    return resp.json()


def _get_key(header: Dict[str, Any], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    jwks = _get_jwks()
    kid = header.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def verify_access_token(token: str) -> Dict[str, Any]:
    try:
        header = jwt.get_unverified_header(token)
        unverified = jwt.decode(token, options={"verify_signature": False})
        key = _get_key(header, unverified)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")

        # Build public key
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=[header.get("alg", "RS256")],
            audience=settings.token_audience,
            issuer=settings.token_issuer,
            options={k: v for k, v in {"verify_aud": bool(settings.token_audience)}.items()},
        )
        return payload
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def require_oauth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return verify_access_token(credentials.credentials)


def extract_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    roles = payload.get(settings.role_claim, [])
    tenant = payload.get(settings.tenant_claim)
    client_id = payload.get(settings.client_id_claim) or payload.get("client_id") or payload.get("sub")
    return {"roles": roles, "tenant": tenant, "client_id": client_id}


def require_roles(*required_roles: str):
    def _dep(payload: Dict[str, Any] = Depends(require_oauth)) -> Dict[str, Any]:
        ctx = extract_context(payload)
        roles = set(ctx.get("roles") or [])
        if not roles.intersection(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return ctx

    return _dep
