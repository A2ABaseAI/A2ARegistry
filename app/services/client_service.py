"""Client service for managing clients and entitlements."""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.client import Client, ClientEntitlement
from ..schemas.client import ClientCreate, ClientUpdate, ClientEntitlementCreate
from ..auth import generate_client_credentials


class ClientService:
    """Service for client management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_client(self, client_data: ClientCreate) -> Client:
        """Create a new client."""
        client_id, client_secret = generate_client_credentials()
        
        client = Client(
            id=str(uuid.uuid4()),
            name=client_data.name,
            description=client_data.description,
            contact_email=client_data.contact_email,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uris=client_data.redirect_uris,
            scopes=client_data.scopes,
        )
        
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        return self.db.query(Client).filter(Client.id == client_id).first()
    
    def get_client_by_oauth_id(self, oauth_client_id: str) -> Optional[Client]:
        """Get a client by OAuth client ID."""
        return self.db.query(Client).filter(Client.client_id == oauth_client_id).first()
    
    def update_client(self, client_id: str, client_data: ClientUpdate) -> Optional[Client]:
        """Update an existing client."""
        client = self.get_client(client_id)
        if not client:
            return None
        
        if client_data.name is not None:
            client.name = client_data.name
        
        if client_data.description is not None:
            client.description = client_data.description
        
        if client_data.contact_email is not None:
            client.contact_email = client_data.contact_email
        
        if client_data.redirect_uris is not None:
            client.redirect_uris = client_data.redirect_uris
        
        if client_data.scopes is not None:
            client.scopes = client_data.scopes
        
        if client_data.is_active is not None:
            client.is_active = client_data.is_active
        
        self.db.commit()
        self.db.refresh(client)
        return client
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client."""
        client = self.get_client(client_id)
        if not client:
            return False
        
        self.db.delete(client)
        self.db.commit()
        return True
    
    def list_clients(self, limit: int = 100, offset: int = 0) -> List[Client]:
        """List all clients."""
        return self.db.query(Client).offset(offset).limit(limit).all()
    
    def create_entitlement(self, entitlement_data: ClientEntitlementCreate) -> ClientEntitlement:
        """Create a client entitlement."""
        entitlement = ClientEntitlement(
            id=str(uuid.uuid4()),
            client_id=entitlement_data.client_id,
            agent_id=entitlement_data.agent_id,
            scopes=entitlement_data.scopes,
            expires_at=entitlement_data.expires_at,
        )
        
        self.db.add(entitlement)
        self.db.commit()
        self.db.refresh(entitlement)
        return entitlement
    
    def get_entitlement(self, entitlement_id: str) -> Optional[ClientEntitlement]:
        """Get an entitlement by ID."""
        return self.db.query(ClientEntitlement).filter(ClientEntitlement.id == entitlement_id).first()
    
    def get_client_entitlements(self, client_id: str) -> List[ClientEntitlement]:
        """Get all entitlements for a client."""
        return self.db.query(ClientEntitlement).filter(
            and_(
                ClientEntitlement.client_id == client_id,
                ClientEntitlement.is_active == True
            )
        ).all()
    
    def get_agent_entitlements(self, agent_id: str) -> List[ClientEntitlement]:
        """Get all entitlements for an agent."""
        return self.db.query(ClientEntitlement).filter(
            and_(
                ClientEntitlement.agent_id == agent_id,
                ClientEntitlement.is_active == True
            )
        ).all()
    
    def update_entitlement(
        self,
        entitlement_id: str,
        scopes: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[ClientEntitlement]:
        """Update an entitlement."""
        entitlement = self.get_entitlement(entitlement_id)
        if not entitlement:
            return None
        
        if scopes is not None:
            entitlement.scopes = scopes
        
        if is_active is not None:
            entitlement.is_active = is_active
        
        self.db.commit()
        self.db.refresh(entitlement)
        return entitlement
    
    def delete_entitlement(self, entitlement_id: str) -> bool:
        """Delete an entitlement."""
        entitlement = self.get_entitlement(entitlement_id)
        if not entitlement:
            return False
        
        self.db.delete(entitlement)
        self.db.commit()
        return True
    
    def revoke_client_entitlements(self, client_id: str) -> int:
        """Revoke all entitlements for a client."""
        count = self.db.query(ClientEntitlement).filter(
            ClientEntitlement.client_id == client_id
        ).update({"is_active": False})
        
        self.db.commit()
        return count
    
    def revoke_agent_entitlements(self, agent_id: str) -> int:
        """Revoke all entitlements for an agent."""
        count = self.db.query(ClientEntitlement).filter(
            ClientEntitlement.agent_id == agent_id
        ).update({"is_active": False})
        
        self.db.commit()
        return count
