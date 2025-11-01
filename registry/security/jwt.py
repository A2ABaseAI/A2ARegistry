"""JWT creation, verification, and JWKS utilities for the A2A Agent Registry."""

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

import httpx
import jwt
from fastapi import HTTPException, status

from ..config import settings


def create_access_token(
    user_id: str,
    username: str,
    email: str,
    roles: List[str],
    tenant_id: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""

    expires = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes))

    payload: Dict[str, Any] = {
        "iss": settings.token_issuer or "a2a-registry",
        "aud": settings.token_audience or "a2a-registry",
        "sub": user_id,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "nbf": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expires.timestamp()),
        "user_id": user_id,
        "username": username,
        "email": email,
        "client_id": user_id,
        "roles": roles,
        "tenant": tenant_id,
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


def _decode_with_local_secret(token: str) -> Dict[str, Any]:
    """Decode a JWT using the configured local secret."""

    options = {
        "verify_exp": True,
        "verify_aud": bool(settings.token_audience),
        "verify_iss": bool(settings.token_issuer),
    }

    return jwt.decode(  # type: ignore[no-any-return]
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        audience=settings.token_audience or "a2a-registry",
        issuer=settings.token_issuer or "a2a-registry",
        options=options,
    )


@lru_cache(maxsize=1)
def _get_jwks() -> Dict[str, Any]:
    """Fetch JWKS data from the configured endpoint."""

    if not settings.jwks_url:
        raise RuntimeError("JWKS URL is not configured")

    response = httpx.get(settings.jwks_url, timeout=5.0)
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]


def _get_key(header: Dict[str, Any], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    jwks = _get_jwks()
    kid = header.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key  # type: ignore[no-any-return]
    return None


def _decode_with_jwks(token: str) -> Dict[str, Any]:
    """Decode a JWT using a JWKS public key."""

    if not settings.jwks_url:
        raise RuntimeError("JWKS URL is not configured")

    header = jwt.get_unverified_header(token)
    unverified = jwt.decode(token, options={"verify_signature": False})
    key = _get_key(header, unverified)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")

    # Build public key
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

    options = {
        "verify_exp": True,
        "verify_aud": bool(settings.token_audience),
        "verify_iss": bool(settings.token_issuer),
    }

    return jwt.decode(  # type: ignore[no-any-return]
        token,
        key=public_key,
        algorithms=[header.get("alg", "RS256")],
        audience=settings.token_audience,
        issuer=settings.token_issuer,
        options=options,
    )


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT access token using local secret and/or JWKS."""

    errors: List[str] = []

    if settings.secret_key:
        try:
            return _decode_with_local_secret(token)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience") from exc
        except jwt.InvalidIssuerError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer") from exc
        except jwt.InvalidTokenError as exc:
            errors.append(f"local verification failed: {exc}")
        except Exception as exc:  # pragma: no cover - unexpected edge cases
            errors.append(f"local verification unexpected error: {exc}")

    if settings.jwks_url:
        try:
            return _decode_with_jwks(token)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience") from exc
        except jwt.InvalidIssuerError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer") from exc
        except jwt.InvalidTokenError as exc:
            errors.append(f"jwks verification failed: {exc}")
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - unexpected edge cases
            errors.append(f"jwks verification unexpected error: {exc}")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
