"""Registry read services over AgentRecord/AgentVersion."""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from ..models.agent_core import AgentRecord, AgentVersion, Entitlement


def _get_db_session():
    """Get a database session. Can be overridden in tests."""
    from ..database import SessionLocal

    return SessionLocal()


def _latest_visible_versions_query(db: Session, tenant_id: str):
    # Join AgentRecord with its latest AgentVersion by matching latest_version
    return (
        db.query(AgentRecord, AgentVersion)
        .join(
            AgentVersion,
            and_(
                AgentVersion.agent_id == AgentRecord.id,
                AgentVersion.version == AgentRecord.latest_version,
            ),
        )
        .filter(AgentRecord.tenant_id == tenant_id)
    )


def _to_item(record: AgentRecord, version: AgentVersion) -> Dict[str, Any]:
    skills = version.card_json.get("skills") or []
    return {
        "agentId": record.id,
        "name": version.card_json.get("name"),
        "description": version.card_json.get("description"),
        "publisherId": record.publisher_id,
        "version": version.version,
        "protocolVersion": version.protocol_version,
        "capabilities": version.card_json.get("capabilities", {}),
        "skills": skills,
    }


class RegistryService:
    def __init__(self, db_session=None):
        if db_session is not None:
            self.db = db_session
            self._owns_session = False
        else:
            # Create a new session using the factory function
            self.db = _get_db_session()
            self._owns_session = True

    def __del__(self):
        """Clean up database session if we own it."""
        if hasattr(self, "_owns_session") and self._owns_session and hasattr(self, "db") and self.db:
            self.db.close()

    def list_public(self, tenant_id: str, top: int, skip: int) -> Tuple[List[Dict[str, Any]], int]:
        q = _latest_visible_versions_query(self.db, tenant_id).filter(AgentVersion.public.is_(True)).order_by(desc(AgentVersion.created_at))
        items = q.offset(skip).limit(top).all()
        data = [_to_item(r, v) for r, v in items]
        return data, len(data)

    def list_entitled(self, tenant_id: str, client_id: str, top: int, skip: int) -> Tuple[List[Dict[str, Any]], int]:
        # Public
        q_pub = _latest_visible_versions_query(self.db, tenant_id).filter(AgentVersion.public.is_(True))

        # Entitled: exists entitlement for (tenant, client_id, agent_id)
        q_ent = (
            _latest_visible_versions_query(self.db, tenant_id)
            .join(Entitlement, Entitlement.agent_id == AgentRecord.id)
            .filter(
                and_(
                    Entitlement.tenant_id == tenant_id,
                    Entitlement.client_id == client_id,
                )
            )
        )

        items = q_pub.union(q_ent).order_by(desc(AgentVersion.created_at)).offset(skip).limit(top).all()
        data = [_to_item(r, v) for r, v in items]
        return data, len(data)

    def get_latest(self, tenant_id: str, agent_id: str) -> Optional[Tuple[AgentRecord, AgentVersion]]:
        q = _latest_visible_versions_query(self.db, tenant_id).filter(AgentRecord.id == agent_id)
        row = q.first()
        return row  # type: ignore[no-any-return]

    def is_entitled(self, tenant_id: str, client_id: str, agent_id: str) -> bool:
        exists = (
            self.db.query(Entitlement)
            .filter(
                and_(
                    Entitlement.tenant_id == tenant_id,
                    Entitlement.client_id == client_id,
                    Entitlement.agent_id == agent_id,
                )
            )
            .first()
        )
        return exists is not None
