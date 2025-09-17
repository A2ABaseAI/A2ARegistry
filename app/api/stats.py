from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.agent import Agent
from ..models.client import Client
from ..models.peering import PeerRegistry

router = APIRouter()


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get registry statistics."""
    try:
        # Count agents
        total_agents = db.query(Agent).count()
        active_agents = db.query(Agent).filter(Agent.location_url.isnot(None)).count()

        # Count clients
        total_clients = db.query(Client).count()

        # Count peer registries
        total_peers = db.query(PeerRegistry).count()

        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_registrations = (
            db.query(Agent).filter(Agent.created_at >= yesterday).count()
        )

        # Mock search queries for today (in a real app, you'd track this)
        search_queries_today = 0

        return {
            "total_agents": total_agents,
            "total_clients": total_clients,
            "total_peers": total_peers,
            "active_agents": active_agents,
            "recent_registrations": recent_registrations,
            "search_queries_today": search_queries_today,
        }
    except Exception as e:
        # Return mock data if there's an error
        return {
            "total_agents": 0,
            "total_clients": 0,
            "total_peers": 0,
            "active_agents": 0,
            "recent_registrations": 0,
            "search_queries_today": 0,
        }
