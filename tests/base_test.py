import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.agent_core import AgentRecord, AgentVersion, Entitlement


class BaseTest:
    """Base test class with common setup and helper methods."""

    @pytest.fixture
    def setup_test_db(self):
        """Set up in-memory SQLite database for testing."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        def get_test_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()

        return get_test_db

    @pytest.fixture
    def db_session(self, setup_test_db):
        """Create a database session for testing."""
        db_gen = setup_test_db()
        db = next(db_gen)
        try:
            yield db
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection."""
        with patch('redis.from_url') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = None
            mock_redis_instance.set.return_value = True
            mock_redis_instance.incr.return_value = 1
            mock_redis_instance.expire.return_value = True
            mock_redis.return_value = mock_redis_instance
            yield mock_redis_instance

    @pytest.fixture
    def mock_opensearch(self):
        """Mock OpenSearch connection."""
        with patch('app.services.search_index.OpenSearch') as mock_opensearch, \
             patch('opensearchpy.OpenSearch') as mock_health_opensearch:
            mock_es_instance = MagicMock()
            mock_es_instance.ping.return_value = True
            mock_es_instance.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}
            mock_es_instance.indices.exists.return_value = False
            mock_es_instance.indices.create.return_value = {"acknowledged": True}
            mock_opensearch.return_value = mock_es_instance
            mock_health_opensearch.return_value = mock_es_instance
            yield mock_es_instance

    @pytest.fixture
    def mock_health_checker_db(self, setup_test_db):
        """Mock database session factory for HealthChecker."""
        from unittest.mock import patch
        
        # Get the test database session factory
        test_db_factory = setup_test_db
        
        def mock_session_local():
            return next(test_db_factory())
        
        with patch('app.database.SessionLocal', side_effect=mock_session_local):
            yield

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication dependency."""
        from app.auth_jwks import require_oauth
        from app.main import app

        def mock_require_oauth():
            return {
                "sub": "test-client",
                "client_id": "test-client",
                "tenant": "default",
                "roles": ["Administrator"]
            }

        # Apply the mock to the app
        app.dependency_overrides[require_oauth] = mock_require_oauth
        yield mock_require_oauth
        # Clean up
        if require_oauth in app.dependency_overrides:
            del app.dependency_overrides[require_oauth]

    @pytest.fixture
    def mock_services_db(self, setup_test_db):
        """Mock services to use test database."""
        from unittest.mock import patch
        
        # Get the test database session factory
        test_db_factory = setup_test_db
        
        def mock_registry_service():
            from app.services.registry_service import RegistryService
            service = RegistryService()
            # Replace the db session with test database
            service.db = next(test_db_factory())
            return service
        
        def mock_agent_service():
            from app.services.agent_service import AgentService
            service = AgentService()
            # Replace the db session with test database
            service.db = next(test_db_factory())
            return service
        
        def mock_card_service():
            from app.services.card_service import CardService
            service = CardService()
            # Replace the db session with test database
            service.db = next(test_db_factory())
            return service
        
        # Mock the static method separately
        def mock_parse_and_validate_card(body):
            from app.services.card_service import CardService
            # Call the real method but with test database
            return CardService.parse_and_validate_card(body)
        
        with patch('app.api.agents.RegistryService', side_effect=mock_registry_service), \
             patch('app.api.agents.AgentService', side_effect=mock_agent_service), \
             patch('app.api.agents.CardService', side_effect=mock_card_service), \
             patch('app.api.agents.CardService.parse_and_validate_card', side_effect=mock_parse_and_validate_card), \
             patch('app.api.well_known.RegistryService', side_effect=mock_registry_service), \
             patch('app.api.search.RegistryService', side_effect=mock_registry_service):
            yield

    def create_test_agent_record(
        self, db_session, agent_id="test-agent-123", **kwargs
    ):
        """Create a test agent record."""
        defaults = {
            "id": agent_id,
            "publisher_id": "test-publisher",
            "tenant_id": "default",
            "agent_key": f"test-key-{agent_id}",
            "latest_version": "1.0.0"
        }
        defaults.update(kwargs)

        agent_record = AgentRecord(**defaults)
        db_session.add(agent_record)
        db_session.commit()
        return agent_record

    def create_test_agent_version(
        self, db_session, agent_id="test-agent-123", public=True, **kwargs
    ):
        """Create a test agent version."""
        defaults = {
            "id": f"version-{agent_id}",
            "agent_id": agent_id,
            "version": "1.0.0",
            "protocol_version": "0.3.0",
            "card_json": {
                "protocolVersion": "0.3.0",
                "name": "Test Agent",
                "description": "A test agent for unit testing",
                "capabilities": {
                    "a2a_version": "0.3.0",
                    "supported_protocols": ["text"],
                    "text": True,
                    "streaming": True
                },
                "skills": []
            },
            "card_hash": "test-hash",
            "public": public
        }
        defaults.update(kwargs)

        agent_version = AgentVersion(**defaults)
        db_session.add(agent_version)
        db_session.commit()
        return agent_version

    def create_test_entitlement(
        self, db_session, agent_id="test-agent-123", client_id="test-client", **kwargs
    ):
        """Create a test entitlement."""
        defaults = {
            "id": f"entitlement-{agent_id}",
            "tenant_id": "default",
            "client_id": client_id,
            "agent_id": agent_id,
            "scope": "view"
        }
        defaults.update(kwargs)

        entitlement = Entitlement(**defaults)
        db_session.add(entitlement)
        db_session.commit()
        return entitlement

    def setup_complete_agent(
        self, db_session, agent_id="test-agent-123", public=True, **kwargs
    ):
        """Set up a complete agent with record and version."""
        agent_record = self.create_test_agent_record(db_session, agent_id, **kwargs)
        agent_version = self.create_test_agent_version(db_session, agent_id, public=public)
        return agent_record, agent_version

    def get_valid_agent_card_data(self):
        """Get valid agent card data for testing."""
        return {
            "protocolVersion": "0.3.0",
            "name": "Test Agent",
            "description": "A test agent for unit testing",
            "url": "https://example.com/.well-known/agent-card.json",
            "capabilities": {
                "a2a_version": "0.3.0",
                "supported_protocols": ["text"],
                "text": True,
                "streaming": True
            },
            "skills": []
        }

    def get_valid_publish_data(self):
        """Get valid publish data for testing."""
        return {
            "public": True,
            "card": self.get_valid_agent_card_data()
        }

    def assert_agent_response_structure(self, data):
        """Assert that the response has the expected agent structure."""
        assert "agentId" in data
        assert "version" in data
        assert "protocolVersion" in data
        assert "public" in data
        assert "signatureValid" in data

    def assert_paginated_response_structure(self, data):
        """Assert that the response has the expected paginated structure."""
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["count"], int)
