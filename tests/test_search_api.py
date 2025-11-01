"""Tests for app/api/search.py - Search API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from registry.main import app
from tests.base_test import BaseTest


class TestSearchAPI(BaseTest):
    """Tests for search API endpoints."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch, mock_services_db):
        """Create a test client with mocked dependencies."""
        from registry.database import get_db

        def get_test_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = get_test_db

        with TestClient(app) as test_client:
            yield test_client

        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]

    def test_search_agents_success(self, client, db_session, mock_auth):
        """Test successful agent search."""
        # Create test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        search_body = {"q": "test", "top": 10, "skip": 0, "filters": {}}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["count"], int)

    def test_search_agents_with_filters(self, client, db_session, mock_auth):
        """Test search with filters."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {
            "q": "test",
            "top": 10,
            "skip": 0,
            "filters": {"protocolVersion": "1.0", "publisherId": "test-publisher"},
        }

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "count" in data

    def test_search_agents_pagination(self, client, db_session, mock_auth):
        """Test search with pagination."""
        # Create multiple agents
        for i in range(5):
            self.setup_complete_agent(db_session, f"agent-{i}")

        search_body = {"q": "test", "top": 2, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) <= 2

    def test_search_agents_invalid_top(self, client, mock_auth):
        """Test search with invalid top parameter."""
        search_body = {"q": "test", "top": 0, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        # Pydantic validation returns 422
        assert response.status_code == 422

    def test_search_agents_invalid_top_too_large(self, client, mock_auth):
        """Test search with top parameter too large."""
        search_body = {"q": "test", "top": 101, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        # Pydantic validation returns 422
        assert response.status_code == 422

    def test_search_agents_invalid_skip(self, client, mock_auth):
        """Test search with invalid skip parameter."""
        search_body = {"q": "test", "top": 10, "skip": -1}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        # Pydantic validation returns 422
        assert response.status_code == 422

    def test_search_agents_empty_query(self, client, db_session, mock_auth):
        """Test search with empty query."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {"q": "", "top": 10, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        # Should still succeed, might return all or filtered results
        assert response.status_code in [200, 400]

    def test_search_agents_no_query(self, client, db_session, mock_auth):
        """Test search without query parameter."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {"top": 10, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200

    def test_search_agents_authentication_required(self, client):
        """Test that search requires authentication."""
        search_body = {"q": "test", "top": 10, "skip": 0}

        response = client.post("/agents/search", json=search_body)
        assert response.status_code == 401

    def test_search_agents_with_cache(self, client, db_session, mock_auth):
        """Test search with caching."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {"q": "test", "top": 10, "skip": 0}

        with patch("registry.api.search.CacheManager") as mock_cache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.get.return_value = {"items": [], "count": 0}
            mock_cache.return_value = mock_cache_instance

            response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
            assert response.status_code == 200

            # Verify cache was checked
            mock_cache_instance.get.assert_called()

    def test_search_agents_fallback_to_database(self, client, db_session, mock_auth):
        """Test that search falls back to database when search index fails."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {"q": "test", "top": 10, "skip": 0}

        with patch("registry.api.search.SearchIndex") as mock_search_index:
            # Make search index fail
            mock_index = MagicMock()
            mock_index.ensure_index.side_effect = Exception("Search backend failed")
            mock_search_index.return_value = mock_index

            # Should fallback to database
            response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
            # Should still succeed via database fallback
            assert response.status_code == 200

    def test_search_agents_response_structure(self, client, db_session, mock_auth):
        """Test that search response has correct structure."""
        self.setup_complete_agent(db_session, "agent-1")

        search_body = {"q": "test", "top": 10, "skip": 0}

        response = client.post("/agents/search", json=search_body, headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["count"], int)
        assert data["count"] >= 0

