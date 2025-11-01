"""Security API endpoints for API key management and telemetry."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..core.logging import get_logger
from . import get_security_service, require_roles

logger = get_logger(__name__)


router = APIRouter(prefix="/security", tags=["security"])


class CreateApiKeyRequest(BaseModel):
    """Request payload for API key creation."""

    scopes: list[str] = Field(..., description="List of scopes for the API key")
    expires_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until expiration (1-365). Omit for no expiration.",
    )


class ApiKeyResponse(BaseModel):
    """Response payload for API key creation and retrieval."""

    api_key: str = Field(..., description="Generated API key (only returned once)")
    key_id: str = Field(..., description="Unique identifier for the key")
    scopes: list[str] = Field(..., description="Scopes assigned to the key")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class ValidateApiKeyRequest(BaseModel):
    """Request payload for API key validation."""

    api_key: str = Field(..., min_length=16, description="API key to validate")
    required_scopes: Optional[list[str]] = Field(None, description="Scopes that must be present")


class ApiKeyInfoResponse(BaseModel):
    """Response payload for API key information."""

    key_id: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    scopes: list[str]
    is_active: bool


class SecurityEventResponse(BaseModel):
    """Response payload for security events."""

    event_id: str
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    user_id: Optional[str]
    agent_id: Optional[str]
    details: dict
    resolved: bool


class SecuritySummaryResponse(BaseModel):
    """Response payload for aggregate security telemetry."""

    api_keys: dict
    jwt_keys: dict
    security_events: dict
    policies: dict
    threat_patterns: dict


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    payload: CreateApiKeyRequest,
    context: dict = Depends(require_roles("Administrator")),
):
    """Create a new API key (Administrator only)."""

    try:
        service = get_security_service()
        api_key, info = service.create_api_key(
            scopes=payload.scopes,
            expires_days=payload.expires_days,
            user_id=context.get("client_id"),
        )

        return ApiKeyResponse(
            api_key=api_key,
            key_id=info.key_id,
            scopes=info.scopes,
            created_at=info.created_at,
            expires_at=info.expires_at,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.error("Failed to create API key", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create API key") from exc


@router.post("/api-keys/validate", response_model=ApiKeyInfoResponse)
async def validate_api_key(payload: ValidateApiKeyRequest):
    """Validate an API key and return its metadata."""

    service = get_security_service()
    info = service.validate_api_key(payload.api_key, payload.required_scopes)

    if not info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key or insufficient scopes")

    return ApiKeyInfoResponse(
        key_id=info.key_id,
        created_at=info.created_at,
        expires_at=info.expires_at,
        last_used=info.last_used,
        usage_count=info.usage_count,
        scopes=info.scopes,
        is_active=info.is_active,
    )


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    context: dict = Depends(require_roles("Administrator")),
):
    """Revoke an API key (Administrator only)."""

    service = get_security_service()
    if service.revoke_api_key(key_id):
        return {"message": "API key revoked successfully"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")


@router.get("/api-keys", response_model=list[ApiKeyInfoResponse])
async def list_api_keys(
    active_only: bool = True,
    context: dict = Depends(require_roles("Administrator")),
):
    """List API keys (Administrator only)."""

    service = get_security_service()
    items = service.list_api_keys(active_only=active_only)

    return [
        ApiKeyInfoResponse(
            key_id=item.key_id,
            created_at=item.created_at,
            expires_at=item.expires_at,
            last_used=item.last_used,
            usage_count=item.usage_count,
            scopes=item.scopes,
            is_active=item.is_active,
        )
        for item in items
    ]


@router.get("/api-keys/{key_id}", response_model=ApiKeyInfoResponse)
async def get_api_key(
    key_id: str,
    context: dict = Depends(require_roles("Administrator")),
):
    """Get API key details (Administrator only)."""

    service = get_security_service()
    info = service.get_api_key_info(key_id)

    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    return ApiKeyInfoResponse(
        key_id=info.key_id,
        created_at=info.created_at,
        expires_at=info.expires_at,
        last_used=info.last_used,
        usage_count=info.usage_count,
        scopes=info.scopes,
        is_active=info.is_active,
    )


@router.get("/events", response_model=list[SecurityEventResponse])
async def get_security_events(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    context: dict = Depends(require_roles("Administrator")),
):
    """Retrieve recent security events (Administrator only)."""

    service = get_security_service()
    events = service.get_security_events(event_type=event_type, severity=severity, limit=limit)

    return [
        SecurityEventResponse(
            event_id=event.event_id,
            timestamp=event.timestamp,
            event_type=event.event_type,
            severity=event.severity,
            source=event.source,
            user_id=event.user_id,
            agent_id=event.agent_id,
            details=event.details,
            resolved=event.resolved,
        )
        for event in events
    ]


@router.get("/summary", response_model=SecuritySummaryResponse)
async def get_security_summary(context: dict = Depends(require_roles("Administrator"))):
    """Return aggregate security telemetry (Administrator only)."""

    service = get_security_service()
    summary = service.get_security_summary()
    return SecuritySummaryResponse(**summary)
