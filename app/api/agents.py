"""Agent API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional, require_auth
from ..core.logging import get_logger
from ..database import get_db
from ..schemas.agent import (
    AgentCard,
    AgentCreate,
    AgentResponse,
    AgentSearchRequest,
    AgentSearchResponse,
    AgentUpdate,
)
from ..schemas.common import PaginatedResponse
from ..services.agent_service import AgentService
from ..services.search_service import SearchService

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/public")
async def get_public_agents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all publicly available agents."""
    try:
        agent_service = AgentService(db)
        agents = agent_service.get_public_agents()

        # Calculate pagination
        total = len(agents)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_agents = agents[start_idx:end_idx]

        # Return in the format expected by frontend
        return {
            "agents": [agent.to_agent_response() for agent in paginated_agents],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error(f"Error retrieving public agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve public agents",
        )


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get an agent by ID."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Simplified access control - only check if agent is public
    if not agent.is_public and not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required to access private agents",
        )

    return agent.to_agent_response()


@router.get("/{agent_id}/card", response_model=AgentCard)
async def get_agent_card(
    agent_id: str,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get an agent's card data."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Check if agent is public or if client has access
    if not agent.is_public:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authentication required to access private agents",
            )

        # Simplified access control - authenticated users can access private agents

    return agent.agent_card


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a new agent."""
    agent_service = AgentService(db)

    # Check if agent with same name already exists
    existing_agent = agent_service.get_agent_by_name(agent_data.agent_card.name)
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent with this name already exists",
        )

    # Use user ID from token as owner_id
    owner_id = current_user.get("sub", "anonymous")
    agent = agent_service.create_agent(agent_data, owner_id)
    return agent.to_agent_response()


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_client=Depends(require_scope("agent:write")),
    db: Session = Depends(get_db),
):
    """Update an agent."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Check ownership
    if agent.client_id != current_client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the agent owner can update it",
        )

    updated_agent = agent_service.update_agent(agent_id, agent_data)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Update search index
    search_service = SearchService(db)
    search_service.index_agent(updated_agent)

    return updated_agent.to_agent_response()


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_client=Depends(require_scope("agent:write")),
    db: Session = Depends(get_db),
):
    """Delete an agent."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Check ownership
    if agent.client_id != current_client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the agent owner can delete it",
        )

    # Remove from search index
    search_service = SearchService(db)
    search_service.remove_agent(agent_id)

    success = agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )


@router.get("/", response_model=PaginatedResponse[AgentResponse])
async def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """List agents with optional filters."""
    agent_service = AgentService(db)

    # Determine if we should show public agents only
    is_public_only = current_client is None

    agents = agent_service.list_agents(
        client_id=current_client.id if current_client else None,
        is_public=is_public_only,
        provider=provider,
        tags=tags,
        limit=per_page,
        offset=(page - 1) * per_page,
    )

    total_count = agent_service.get_agent_count(
        client_id=current_client.id if current_client else None
    )

    agent_responses = [agent.to_agent_response() for agent in agents]

    return PaginatedResponse(
        items=agent_responses,
        pagination={"page": page, "per_page": per_page, "total_count": total_count},
        total_count=total_count,
    )


@router.get("/entitled", response_model=List[AgentResponse])
async def get_entitled_agents(
    current_client=Depends(get_current_client), db: Session = Depends(get_db)
):
    """Get agents that the current client is entitled to access."""
    agent_service = AgentService(db)
    agents = agent_service.get_entitled_agents(current_client.id)

    return [agent.to_agent_response() for agent in agents]


@router.post("/search", response_model=AgentSearchResponse)
async def search_agents(
    search_request: AgentSearchRequest,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Search for agents using various criteria."""
    search_service = SearchService(db)

    # Ensure search index exists
    search_service.create_index()

    client_id = current_client.id if current_client else None
    return search_service.search_agents(search_request, client_id)
