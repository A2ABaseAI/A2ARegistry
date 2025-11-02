"""Agent service layer for database operations."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status

from ..core.logging import get_logger
from ..models.agent_core import AgentRecord, AgentVersion
from ..schemas.agent_card_spec import AgentCardSpec
from .search_index import SearchIndex


def _get_db_session():
    """Get a database session. Can be overridden in tests."""
    from ..database import SessionLocal

    return SessionLocal()


logger = get_logger(__name__)


def _canonical_json(data: Dict[str, Any]) -> str:
    """Generate canonical JSON representation."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


class AgentService:
    """Service for agent-related database operations."""

    def __init__(self):
        """Initialize with database session."""
        # Create a new session using the factory function
        self.db = _get_db_session()

    def __del__(self):
        """Clean up database session."""
        if hasattr(self, "db") and self.db:
            self.db.close()

    def create_or_update_agent_record(
        self, card_data: Dict[str, Any], card_hash: str, tenant_id: str, publisher_id: str, agent_key: str, version: str
    ) -> AgentRecord:
        """
        Create or update agent record in database.

        Args:
            card_data: Parsed card data
            card_hash: Computed card hash
            tenant_id: Tenant identifier
            publisher_id: Publisher identifier
            agent_key: Agent key
            version: Agent version

        Returns:
            AgentRecord instance

        Raises:
            HTTPException: For database errors
        """
        try:
            # Find existing record
            rec = (
                self.db.query(AgentRecord)
                .filter(
                    AgentRecord.tenant_id == tenant_id,
                    AgentRecord.publisher_id == publisher_id,
                    AgentRecord.agent_key == agent_key,
                )
                .first()
            )

            if rec is None:
                # Create new record
                rec = AgentRecord(
                    id=card_hash[:24],
                    tenant_id=tenant_id,
                    publisher_id=publisher_id,
                    agent_key=agent_key,
                    latest_version=version,
                )
                self.db.add(rec)
                self.db.flush()
                logger.debug(f"Created new agent record: {rec.id}")
            else:
                # Update existing record
                rec.latest_version = version
                logger.debug(f"Updated existing agent record: {rec.id}")

            return rec  # type: ignore[no-any-return]

        except Exception as exc:
            logger.error(f"Failed to create/update agent record: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist agent record") from exc

    def create_agent_version(
        self,
        rec: AgentRecord,
        card_data: Dict[str, Any],
        card_hash: str,
        card_url: Optional[str],
        version: str,
        public: bool,
    ) -> AgentVersion:
        """
        Create agent version record with idempotency check.

        Args:
            rec: Agent record
            card_data: Parsed card data
            card_hash: Computed card hash
            card_url: Card URL (if applicable)
            version: Agent version
            public: Whether agent is public

        Returns:
            AgentVersion instance

        Raises:
            HTTPException: For database errors
        """
        try:
            # Check for existing version (idempotency)
            existing = self.db.query(AgentVersion).filter(AgentVersion.agent_id == rec.id, AgentVersion.version == version).first()

            if existing:
                logger.debug(f"Found existing agent version: {existing.id}")
                return existing  # type: ignore[no-any-return]

            # Create new version
            av = AgentVersion(
                id=f"{rec.id}:{version}",
                agent_id=rec.id,
                version=version,
                protocol_version="1.0",  # Default A2A protocol version
                card_json=card_data,
                card_hash=card_hash,
                card_url=card_url,
                jwks_url=None,  # No JWKS URL in new schema
                signature_valid=False,
                public=public,
            )
            self.db.add(av)
            logger.debug(f"Created new agent version: {av.id}")
            return av

        except Exception as exc:
            logger.error(f"Failed to create agent version: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist agent version") from exc

    def publish_agent(self, card_data: Dict[str, Any], card_url: Optional[str], public: bool, tenant_id: str) -> Dict[str, Any]:
        """
        Publish an agent with full database operations.

        Args:
            card_data: Parsed card data
            card_url: Card URL (if applicable)
            public: Whether agent is public
            tenant_id: Tenant identifier

        Returns:
            Dict with agent metadata

        Raises:
            HTTPException: For database errors
        """
        try:
            # Validate card data
            card = AgentCardSpec.model_validate(card_data)
            # Use validated card's dict to ensure ADK-compatible format is stored
            # Use by_alias=True to serialize 'in_' as 'in' for ADK compatibility
            import json
            card_data = json.loads(card.model_dump_json(by_alias=True))

            # Compute hash and version
            canonical = _canonical_json(card_data)
            card_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            version = card.version or datetime.now(timezone.utc).isoformat()

            # Extract metadata
            publisher_id = card.url.host if hasattr(card.url, "host") and card.url.host else "publisher"
            agent_key = card.name.lower().replace(" ", "-")

            logger.debug(f"Publishing agent: {card.name} v{version} for tenant {tenant_id}")

            # Database operations (transactional)
            try:
                # Create or update agent record
                rec = self.create_or_update_agent_record(card_data, card_hash, tenant_id, publisher_id, agent_key, version)

                # Create agent version
                av = self.create_agent_version(rec, card_data, card_hash, card_url, version, public)

                # Commit transaction
                self.db.commit()
                logger.info(f"Successfully published agent: {rec.id} v{version}")

            except Exception as exc:
                self.db.rollback()
                logger.error(f"Database transaction failed: {exc}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist agent") from exc

            # Index in search engine (non-critical)
            self._index_agent_version(av, rec, card_data, tenant_id, publisher_id, version, public)

            # Return success response
            return {
                "agentId": rec.id,
                "version": version,
                "protocolVersion": "1.0",  # Default A2A protocol version
                "public": av.public,
                "signatureValid": av.signature_valid,
            }

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as exc:
            logger.error(f"Unexpected error publishing agent: {exc}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from exc

    def _index_agent_version(
        self,
        av: AgentVersion,
        rec: AgentRecord,
        card_data: Dict[str, Any],
        tenant_id: str,
        publisher_id: str,
        version: str,
        public: bool,
    ) -> None:
        """
        Index agent version in search engine (non-critical operation).

        Args:
            av: Agent version record
            rec: Agent record
            card_data: Parsed card data
            tenant_id: Tenant identifier
            publisher_id: Publisher identifier
            version: Agent version
            public: Whether agent is public
        """
        try:
            card = AgentCardSpec.model_validate(card_data)
            SearchIndex().ensure_index()
            SearchIndex().index_version(
                doc_id=str(av.id),
                body={
                    "tenantId": tenant_id,
                    "agentId": rec.id,
                    "version": version,
                    "protocolVersion": "1.0",  # Default A2A protocol version
                    "name": card.name,
                    "description": card.description,
                    "publisherId": publisher_id,
                    "capabilities": card.capabilities.model_dump(),
                    "skills": [s.model_dump() for s in card.skills],
                    "interface": card.interface.model_dump(),
                    "public": public,
                },
            )
            logger.debug(f"Successfully indexed agent version: {av.id}")
        except Exception as e:
            logger.warning(f"Failed to index agent {rec.id}: {e}")
            # Non-critical operation, don't fail the request

    def get_agent_by_id(self, agent_id: str, tenant_id: str) -> Optional[Tuple[AgentRecord, AgentVersion]]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent identifier
            tenant_id: Tenant identifier

        Returns:
            Tuple of (AgentRecord, AgentVersion) or None if not found
        """
        try:
            from .registry_service import RegistryService

            registry_service = RegistryService(db_session=self.db)
            return registry_service.get_latest(tenant_id, agent_id)
        except Exception as exc:
            logger.error(f"Failed to get agent {agent_id}: {exc}")
            return None

    def get_agent_card_data(self, agent_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent card data.

        Args:
            agent_id: Agent identifier
            tenant_id: Tenant identifier

        Returns:
            Card data dict or None if not found
        """
        try:
            result = self.get_agent_by_id(agent_id, tenant_id)
            if result:
                _, agent_version = result
                return agent_version.card_json  # type: ignore[return-value]
            return None
        except Exception as exc:
            logger.error(f"Failed to get card data for agent {agent_id}: {exc}")
            return None

    def check_agent_access(self, agent_id: str, tenant_id: str, client_id: str) -> bool:
        """
        Check if client has access to agent.

        Args:
            agent_id: Agent identifier
            tenant_id: Tenant identifier
            client_id: Client identifier

        Returns:
            True if access granted, False otherwise
        """
        try:
            from .registry_service import RegistryService

            registry_service = RegistryService(db_session=self.db)
            return registry_service.is_entitled(tenant_id, client_id, agent_id)
        except Exception as exc:
            logger.error(f"Failed to check access for agent {agent_id}: {exc}")
            return False

    def delete_agent(self, agent_id: str, tenant_id: str) -> bool:
        """
        Delete an agent and all its versions.

        Args:
            agent_id: Agent identifier
            tenant_id: Tenant identifier

        Returns:
            True if agent was deleted, False if not found
        """
        try:
            # Find agent record
            rec = (
                self.db.query(AgentRecord)
                .filter(AgentRecord.id == agent_id, AgentRecord.tenant_id == tenant_id)
                .first()
            )

            if not rec:
                logger.info(f"Agent {agent_id} not found for deletion")
                return False

            # Delete all versions
            versions = self.db.query(AgentVersion).filter(AgentVersion.agent_id == agent_id).all()
            for version in versions:
                # Remove from search index (non-critical)
                try:
                    SearchIndex().delete_document(str(version.id))
                except Exception as e:
                    logger.warning(f"Failed to remove agent {agent_id} from search index: {e}")

                self.db.delete(version)

            # Delete agent record
            self.db.delete(rec)

            # Commit transaction
            self.db.commit()
            logger.info(f"Successfully deleted agent: {agent_id}")

            # Invalidate cache (non-critical)
            try:
                from ..core.caching import CacheManager
                cache = CacheManager()
                cache.invalidate_pattern("agents:*")
            except Exception as e:
                logger.warning(f"Failed to invalidate cache after deleting agent {agent_id}: {e}")

            return True

        except Exception as exc:
            self.db.rollback()
            logger.error(f"Failed to delete agent {agent_id}: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete agent") from exc
