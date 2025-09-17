"""Peering API endpoints for federation."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..schemas.common import PaginatedResponse
from ..schemas.peering import (
    PeerRegistryCreate,
    PeerRegistryResponse,
    PeerRegistryUpdate,
)
from ..services.peering_service import PeeringService

router = APIRouter(prefix="/peers", tags=["peering"])


@router.post(
    "/", response_model=PeerRegistryResponse, status_code=status.HTTP_201_CREATED
)
async def create_peer(
    peer_data: PeerRegistryCreate,
    current_client=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new peer registry."""
    peering_service = PeeringService(db)

    # Check if peer with same URL already exists
    existing_peer = peering_service.get_peer_by_url(str(peer_data.base_url))
    if existing_peer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Peer registry with this URL already exists",
        )

    peer = peering_service.create_peer(peer_data)
    return peer.to_peer_response()


@router.get("/", response_model=PaginatedResponse[PeerRegistryResponse])
async def list_peers(
    page: int = 1,
    per_page: int = 20,
    active_only: bool = True,
    current_client=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List peer registries."""
    peering_service = PeeringService(db)
    peers = peering_service.list_peers(active_only=active_only)

    # Apply pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_peers = peers[start_idx:end_idx]

    peer_responses = [peer.to_peer_response() for peer in paginated_peers]

    return PaginatedResponse(
        items=peer_responses,
        pagination={"page": page, "per_page": per_page, "total_count": len(peers)},
        total_count=len(peers),
    )


@router.get("/{peer_id}", response_model=PeerRegistryResponse)
async def get_peer(
    peer_id: str, current_client=Depends(require_admin), db: Session = Depends(get_db)
):
    """Get a peer registry by ID."""
    peering_service = PeeringService(db)
    peer = peering_service.get_peer(peer_id)

    if not peer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Peer registry not found"
        )

    return peer.to_peer_response()


@router.put("/{peer_id}", response_model=PeerRegistryResponse)
async def update_peer(
    peer_id: str,
    peer_data: PeerRegistryUpdate,
    current_client=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a peer registry."""
    peering_service = PeeringService(db)
    updated_peer = peering_service.update_peer(peer_id, peer_data)

    if not updated_peer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Peer registry not found"
        )

    return updated_peer.to_peer_response()


@router.delete("/{peer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_peer(
    peer_id: str, current_client=Depends(require_admin), db: Session = Depends(get_db)
):
    """Delete a peer registry."""
    peering_service = PeeringService(db)
    success = peering_service.delete_peer(peer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Peer registry not found"
        )


@router.post("/{peer_id}/sync", status_code=status.HTTP_200_OK)
async def sync_peer(
    peer_id: str, current_client=Depends(require_admin), db: Session = Depends(get_db)
):
    """Synchronize with a peer registry."""
    peering_service = PeeringService(db)
    sync = peering_service.sync_with_peer(peer_id)

    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer registry not found or inactive",
        )

    return {
        "message": f"Sync {sync.status}",
        "sync_id": sync.id,
        "status": sync.status,
        "agents_synced": sync.agents_synced,
        "agents_added": sync.agents_added,
        "agents_updated": sync.agents_updated,
        "agents_removed": sync.agents_removed,
        "error_message": sync.error_message,
    }


@router.post("/sync-all", status_code=status.HTTP_200_OK)
async def sync_all_peers(
    current_client=Depends(require_admin), db: Session = Depends(get_db)
):
    """Synchronize with all active peer registries."""
    peering_service = PeeringService(db)
    syncs = peering_service.sync_all_peers()

    return {
        "message": f"Initiated sync with {len(syncs)} peers",
        "syncs": [
            {
                "sync_id": sync.id,
                "peer_id": sync.peer_registry_id,
                "status": sync.status,
            }
            for sync in syncs
        ],
    }


@router.get("/{peer_id}/sync-history", response_model=List[dict])
async def get_peer_sync_history(
    peer_id: str,
    limit: int = 50,
    current_client=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get synchronization history for a peer."""
    peering_service = PeeringService(db)

    # Verify peer exists
    peer = peering_service.get_peer(peer_id)
    if not peer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Peer registry not found"
        )

    syncs = peering_service.get_sync_history(peer_id, limit)
    return [sync.to_sync_response() for sync in syncs]


@router.get("/sync-history", response_model=List[dict])
async def get_all_sync_history(
    limit: int = 50,
    current_client=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get synchronization history for all peers."""
    peering_service = PeeringService(db)
    syncs = peering_service.get_sync_history(limit=limit)
    return [sync.to_sync_response() for sync in syncs]
