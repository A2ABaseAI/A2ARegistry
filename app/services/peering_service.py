"""Peering service for federation between registries."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..config import settings
from ..models.peering import PeerRegistry, PeerSync
from ..schemas.peering import PeerRegistryCreate, PeerRegistryUpdate


class PeeringService:
    """Service for registry peering and federation operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_peer(self, peer_data: PeerRegistryCreate) -> PeerRegistry:
        """Create a new peer registry."""
        peer = PeerRegistry(
            id=str(uuid.uuid4()),
            name=peer_data.name,
            base_url=str(peer_data.base_url),
            description=peer_data.description,
            auth_token=peer_data.auth_token,
            sync_enabled=peer_data.sync_enabled,
            sync_interval_minutes=peer_data.sync_interval_minutes,
        )

        self.db.add(peer)
        self.db.commit()
        self.db.refresh(peer)
        return peer

    def get_peer(self, peer_id: str) -> Optional[PeerRegistry]:
        """Get a peer registry by ID."""
        return self.db.query(PeerRegistry).filter(PeerRegistry.id == peer_id).first()

    def get_peer_by_url(self, base_url: str) -> Optional[PeerRegistry]:
        """Get a peer registry by base URL."""
        return (
            self.db.query(PeerRegistry)
            .filter(PeerRegistry.base_url == base_url)
            .first()
        )

    def update_peer(
        self, peer_id: str, peer_data: PeerRegistryUpdate
    ) -> Optional[PeerRegistry]:
        """Update a peer registry."""
        peer = self.get_peer(peer_id)
        if not peer:
            return None

        if peer_data.name is not None:
            peer.name = peer_data.name

        if peer_data.base_url is not None:
            peer.base_url = str(peer_data.base_url)

        if peer_data.description is not None:
            peer.description = peer_data.description

        if peer_data.auth_token is not None:
            peer.auth_token = peer_data.auth_token

        if peer_data.sync_enabled is not None:
            peer.sync_enabled = peer_data.sync_enabled

        if peer_data.sync_interval_minutes is not None:
            peer.sync_interval_minutes = peer_data.sync_interval_minutes

        if peer_data.is_active is not None:
            peer.is_active = peer_data.is_active

        self.db.commit()
        self.db.refresh(peer)
        return peer

    def delete_peer(self, peer_id: str) -> bool:
        """Delete a peer registry."""
        peer = self.get_peer(peer_id)
        if not peer:
            return False

        self.db.delete(peer)
        self.db.commit()
        return True

    def list_peers(self, active_only: bool = True) -> List[PeerRegistry]:
        """List peer registries."""
        query = self.db.query(PeerRegistry)

        if active_only:
            query = query.filter(PeerRegistry.is_active == True)

        return query.all()

    def sync_with_peer(self, peer_id: str) -> Optional[PeerSync]:
        """Synchronize with a peer registry."""
        peer = self.get_peer(peer_id)
        if not peer or not peer.is_active:
            return None

        # Create sync record
        sync = PeerSync(
            id=str(uuid.uuid4()),
            peer_registry_id=peer_id,
            sync_type="manual",
            status="in_progress",
            started_at=datetime.utcnow(),
        )

        self.db.add(sync)
        self.db.commit()

        try:
            # Fetch agents from peer
            agents_data = self._fetch_peer_agents(peer)

            if agents_data:
                # Process and store agents
                added, updated, removed = self._process_peer_agents(agents_data, peer)

                sync.agents_synced = len(agents_data)
                sync.agents_added = added
                sync.agents_updated = updated
                sync.agents_removed = removed
                sync.status = "success"
            else:
                sync.status = "failed"
                sync.error_message = "Failed to fetch agents from peer"

        except Exception as e:
            sync.status = "failed"
            sync.error_message = str(e)

        sync.completed_at = datetime.utcnow()
        peer.last_sync_at = sync.completed_at

        self.db.commit()
        self.db.refresh(sync)
        return sync

    def _fetch_peer_agents(self, peer: PeerRegistry) -> Optional[List[Dict[str, Any]]]:
        """Fetch agents from a peer registry."""
        try:
            headers = {}
            if peer.auth_token:
                headers["Authorization"] = f"Bearer {peer.auth_token}"

            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{peer.base_url}/agents/public", headers=headers)
                response.raise_for_status()

                data = response.json()
                return data.get("resources", [])

        except Exception as e:
            print(f"Error fetching agents from peer {peer.name}: {e}")
            return None

    def _process_peer_agents(
        self, agents_data: List[Dict[str, Any]], peer: PeerRegistry
    ) -> tuple[int, int, int]:
        """Process and store agents from peer."""
        from .agent_service import AgentService

        agent_service = AgentService(self.db)
        added = 0
        updated = 0
        removed = 0

        # Get existing peer agents
        existing_agents = {
            agent.location_url: agent
            for agent in agent_service.list_agents(
                provider=f"peer:{peer.name}", limit=1000
            )
        }

        current_agent_urls = set()

        for agent_data in agents_data:
            location_url = agent_data.get("location", {}).get("url")
            if not location_url:
                continue

            current_agent_urls.add(location_url)

            # Check if agent already exists
            existing_agent = existing_agents.get(location_url)

            if existing_agent:
                # Update existing agent
                # Note: In a real implementation, you'd want to compare and update
                # only if there are actual changes
                updated += 1
            else:
                # Create new agent
                try:
                    # Convert peer agent data to our format
                    agent_card = {
                        "id": f"peer_{peer.name}_{agent_data['id']}",
                        "name": agent_data["name"],
                        "version": agent_data.get("version", "1.0.0"),
                        "description": agent_data.get("description", ""),
                        "capabilities": agent_data.get("capabilities", {}),
                        "skills": agent_data.get("skills", {}),
                        "auth_schemes": agent_data.get("auth_schemes", []),
                        "tee_details": agent_data.get("tee_details"),
                        "provider": f"peer:{peer.name}",
                        "tags": agent_data.get("tags", []),
                        "location": agent_data.get("location", {}),
                    }

                    # Create agent (simplified - in real implementation, use proper schema)
                    from ..models.agent import Agent

                    agent = Agent(
                        id=agent_card["id"],
                        name=agent_card["name"],
                        version=agent_card["version"],
                        description=agent_card["description"],
                        provider=agent_card["provider"],
                        agent_card=agent_card,
                        is_public=True,  # Peer agents are public
                        location_url=location_url,
                        location_type="agent_card",
                        tags=agent_card["tags"],
                        capabilities=agent_card["capabilities"],
                        auth_schemes=agent_card["auth_schemes"],
                        tee_details=agent_card["tee_details"],
                    )

                    self.db.add(agent)
                    added += 1

                except Exception as e:
                    print(f"Error creating peer agent: {e}")

        # Remove agents that are no longer in peer
        for url, agent in existing_agents.items():
            if url not in current_agent_urls:
                self.db.delete(agent)
                removed += 1

        self.db.commit()
        return added, updated, removed

    def get_sync_history(
        self, peer_id: Optional[str] = None, limit: int = 50
    ) -> List[PeerSync]:
        """Get synchronization history."""
        query = self.db.query(PeerSync)

        if peer_id:
            query = query.filter(PeerSync.peer_registry_id == peer_id)

        return query.order_by(PeerSync.started_at.desc()).limit(limit).all()

    def get_peers_due_for_sync(self) -> List[PeerRegistry]:
        """Get peers that are due for synchronization."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=60)  # Default sync interval

        return (
            self.db.query(PeerRegistry)
            .filter(
                and_(
                    PeerRegistry.is_active == True,
                    PeerRegistry.sync_enabled == True,
                    or_(
                        PeerRegistry.last_sync_at == None,
                        PeerRegistry.last_sync_at < cutoff_time,
                    ),
                )
            )
            .all()
        )

    def sync_all_peers(self) -> List[PeerSync]:
        """Synchronize with all active peers."""
        peers = self.get_peers_due_for_sync()
        syncs = []

        for peer in peers:
            sync = self.sync_with_peer(peer.id)
            if sync:
                syncs.append(sync)

        return syncs
