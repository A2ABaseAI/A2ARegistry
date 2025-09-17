"""Agent service for managing agents and agent cards."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.agent import Agent
from ..models.client import ClientEntitlement
from ..schemas.agent import AgentCreate, AgentUpdate, AgentSearchRequest
from ..config import settings


class AgentService:
    """Service for agent management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent(self, agent_data: AgentCreate, client_id: Optional[str] = None) -> Agent:
        """Create a new agent."""
        agent_card = agent_data.agent_card
        
        # Extract data from agent card
        agent = Agent(
            id=str(uuid.uuid4()),
            name=agent_card.name,
            version=agent_card.version,
            description=agent_card.description,
            provider=agent_card.provider,
            agent_card=agent_card.dict(),
            is_public=agent_data.is_public,
            client_id=client_id,
            location_url=agent_card.location.get("url"),
            location_type=agent_card.location.get("type", "agent_card"),
            tags=agent_card.tags,
            capabilities=agent_card.capabilities.dict(),
            auth_schemes=[scheme.dict() for scheme in agent_card.auth_schemes],
            tee_details=agent_card.tee_details.dict() if agent_card.tee_details else None,
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def update_agent(self, agent_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
        """Update an existing agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        if agent_data.agent_card:
            agent_card = agent_data.agent_card
            agent.name = agent_card.name
            agent.version = agent_card.version
            agent.description = agent_card.description
            agent.provider = agent_card.provider
            agent.agent_card = agent_card.dict()
            agent.location_url = agent_card.location.get("url")
            agent.location_type = agent_card.location.get("type", "agent_card")
            agent.tags = agent_card.tags
            agent.capabilities = agent_card.capabilities.dict()
            agent.auth_schemes = [scheme.dict() for scheme in agent_card.auth_schemes]
            agent.tee_details = agent_card.tee_details.dict() if agent_card.tee_details else None
        
        if agent_data.is_public is not None:
            agent.is_public = agent_data.is_public
        
        if agent_data.is_active is not None:
            agent.is_active = agent_data.is_active
        
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        return True
    
    def list_agents(
        self,
        client_id: Optional[str] = None,
        is_public: Optional[bool] = None,
        is_active: Optional[bool] = None,
        provider: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Agent]:
        """List agents with optional filters."""
        query = self.db.query(Agent)
        
        if client_id:
            query = query.filter(Agent.client_id == client_id)
        
        if is_public is not None:
            query = query.filter(Agent.is_public == is_public)
        
        if is_active is not None:
            query = query.filter(Agent.is_active == is_active)
        
        if provider:
            query = query.filter(Agent.provider == provider)
        
        if tags:
            # Filter by tags (PostgreSQL array contains)
            for tag in tags:
                query = query.filter(Agent.tags.contains([tag]))
        
        return query.offset(offset).limit(limit).all()
    
    def get_entitled_agents(self, client_id: str) -> List[Agent]:
        """Get agents that a client is entitled to access."""
        query = self.db.query(Agent).join(ClientEntitlement).filter(
            and_(
                ClientEntitlement.client_id == client_id,
                ClientEntitlement.is_active == True,
                Agent.is_active == True
            )
        )
        return query.all()
    
    def get_public_agents(self) -> List[Agent]:
        """Get all public agents."""
        return self.db.query(Agent).filter(
            and_(Agent.is_public == True, Agent.is_active == True)
        ).all()
    
    def search_agents(
        self,
        search_request: AgentSearchRequest,
        client_id: Optional[str] = None
    ) -> List[Agent]:
        """Search agents with various criteria."""
        query = self.db.query(Agent).filter(Agent.is_active == True)
        
        # Apply client entitlements if client_id provided
        if client_id:
            query = query.join(ClientEntitlement).filter(
                and_(
                    ClientEntitlement.client_id == client_id,
                    ClientEntitlement.is_active == True
                )
            )
        elif not search_request.semantic:  # Only public agents for non-authenticated search
            query = query.filter(Agent.is_public == True)
        
        # Text search
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.filter(
                or_(
                    Agent.name.ilike(search_term),
                    Agent.description.ilike(search_term),
                    Agent.provider.ilike(search_term)
                )
            )
        
        # Apply filters
        if search_request.filters:
            if "provider" in search_request.filters:
                query = query.filter(Agent.provider == search_request.filters["provider"])
            
            if "tags" in search_request.filters:
                tags = search_request.filters["tags"]
                if isinstance(tags, list):
                    for tag in tags:
                        query = query.filter(Agent.tags.contains([tag]))
            
            if "capabilities" in search_request.filters:
                capabilities = search_request.filters["capabilities"]
                if isinstance(capabilities, dict):
                    for key, value in capabilities.items():
                        query = query.filter(Agent.capabilities[key].astext == str(value))
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.per_page
        return query.offset(offset).limit(search_request.per_page).all()
    
    def get_agent_count(self, client_id: Optional[str] = None) -> int:
        """Get total count of agents."""
        query = self.db.query(Agent)
        
        if client_id:
            query = query.filter(Agent.client_id == client_id)
        
        return query.count()
    
    def get_agent_by_location(self, location_url: str) -> Optional[Agent]:
        """Get agent by location URL."""
        return self.db.query(Agent).filter(Agent.location_url == location_url).first()
