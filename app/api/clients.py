"""Client API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_client, require_admin
from ..schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientEntitlementCreate,
    ClientEntitlementResponse
)
from ..schemas.common import PaginatedResponse
from ..services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new client."""
    client_service = ClientService(db)
    
    # Check if client with same name already exists
    existing_clients = client_service.list_clients(limit=1000)
    if any(client.name == client_data.name for client in existing_clients):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this name already exists"
        )
    
    client = client_service.create_client(client_data)
    return client.to_client_response()


@router.get("/", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    page: int = 1,
    per_page: int = 20,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all clients."""
    client_service = ClientService(db)
    clients = client_service.list_clients(limit=per_page, offset=(page - 1) * per_page)
    
    # Get total count
    all_clients = client_service.list_clients(limit=10000)  # Get all for count
    total_count = len(all_clients)
    
    client_responses = [client.to_client_response() for client in clients]
    
    return PaginatedResponse(
        items=client_responses,
        pagination={
            "page": page,
            "per_page": per_page,
            "total_count": total_count
        },
        total_count=total_count
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get a client by ID."""
    client_service = ClientService(db)
    client = client_service.get_client(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client.to_client_response()


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a client."""
    client_service = ClientService(db)
    updated_client = client_service.update_client(client_id, client_data)
    
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return updated_client.to_client_response()


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a client."""
    client_service = ClientService(db)
    success = client_service.delete_client(client_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )


@router.get("/{client_id}/entitlements", response_model=List[ClientEntitlementResponse])
async def get_client_entitlements(
    client_id: str,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all entitlements for a client."""
    client_service = ClientService(db)
    entitlements = client_service.get_client_entitlements(client_id)
    
    return [ent.to_entitlement_response() for ent in entitlements]


@router.post("/{client_id}/entitlements", response_model=ClientEntitlementResponse, status_code=status.HTTP_201_CREATED)
async def create_client_entitlement(
    client_id: str,
    entitlement_data: ClientEntitlementCreate,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create an entitlement for a client."""
    client_service = ClientService(db)
    
    # Verify client exists
    client = client_service.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Verify agent exists
    from ..services.agent_service import AgentService
    agent_service = AgentService(db)
    agent = agent_service.get_agent(entitlement_data.agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if entitlement already exists
    existing_entitlements = client_service.get_client_entitlements(client_id)
    if any(ent.agent_id == entitlement_data.agent_id for ent in existing_entitlements):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entitlement already exists for this client and agent"
        )
    
    entitlement = client_service.create_entitlement(entitlement_data)
    return entitlement.to_entitlement_response()


@router.delete("/{client_id}/entitlements/{entitlement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_entitlement(
    client_id: str,
    entitlement_id: str,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a client entitlement."""
    client_service = ClientService(db)
    success = client_service.delete_entitlement(entitlement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entitlement not found"
        )


@router.post("/{client_id}/entitlements/revoke", status_code=status.HTTP_200_OK)
async def revoke_client_entitlements(
    client_id: str,
    current_client = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revoke all entitlements for a client."""
    client_service = ClientService(db)
    count = client_service.revoke_client_entitlements(client_id)
    
    return {"message": f"Revoked {count} entitlements", "count": count}
