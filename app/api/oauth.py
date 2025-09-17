"""OAuth2 endpoints for authentication."""

from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import create_access_token, verify_password
from ..config import settings
from ..database import get_db
from ..services.client_service import ClientService

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/token")
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Get OAuth2 access token using client credentials flow."""
    client_service = ClientService(db)

    # Get client by client_id (username in OAuth2PasswordRequestForm)
    client = client_service.get_client_by_oauth_id(form_data.username)

    if not client or not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify client_secret (password in OAuth2PasswordRequestForm)
    if not verify_password(form_data.password, client.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": client.client_id, "scopes": client.scopes},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "scope": " ".join(client.scopes),
    }


@router.post("/introspect")
async def introspect_token(token: str = Form(...), db: Session = Depends(get_db)):
    """Introspect an access token (RFC 7662)."""
    from ..auth import verify_token

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    client_service = ClientService(db)
    client = client_service.get_client_by_oauth_id(payload.get("sub"))

    if not client or not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client"
        )

    return {
        "active": True,
        "client_id": client.client_id,
        "scope": " ".join(client.scopes),
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
        "sub": client.client_id,
    }
