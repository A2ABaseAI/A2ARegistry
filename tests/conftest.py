"""Test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["ELASTICSEARCH_URL"] = "http://localhost:9200"
os.environ["ELASTICSEARCH_INDEX"] = "a2a_agents_test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DEBUG"] = "true"
os.environ["APP_NAME"] = "A2A Agent Registry Test"
os.environ["APP_VERSION"] = "1.0.0"
os.environ["REGISTRY_BASE_URL"] = "http://localhost:8000"
os.environ["MAX_AGENTS_PER_CLIENT"] = "1000"
os.environ["ENABLE_FEDERATION"] = "false"  # Disable federation for tests


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services for all tests."""
    with patch("redis.Redis") as mock_redis, \
         patch("elasticsearch.Elasticsearch") as mock_es, \
         patch("app.services.search_service.Elasticsearch") as mock_es_search, \
         patch("app.services.search_service.SearchService") as mock_search_service:

        # Mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.hset.return_value = True
        mock_redis_instance.hget.return_value = None
        mock_redis_instance.expire.return_value = True
        mock_redis.return_value = mock_redis_instance

        # Mock Elasticsearch
        mock_es_instance = Mock()
        mock_es_instance.ping.return_value = True
        mock_es_instance.index.return_value = {"_id": "test-id"}
        mock_es_instance.delete.return_value = {"deleted": 1}

        # Create a mock search that returns different results based on query
        def mock_search(body=None, **kwargs):
            if body and "query" in body:
                query = body["query"]
                if "search test" in str(query).lower():
                    return {
                        "hits": {
                            "total": {"value": 1},
                            "hits": [{
                                "_id": "search-test-agent",
                                "_source": {
                                    "id": "search-test-agent",
                                    "name": "Search Test Agent",
                                    "description": "An agent for testing search",
                                    "provider": "Search Test Provider",
                                    "tags": ["search", "test"],
                                    "is_public": True,
                                    "is_active": True,
                                    "capabilities": {
                                        "a2a_version": "1.0",
                                        "supported_protocols": ["http"]
                                    },
                                    "auth_schemes": [{
                                        "type": "apiKey",
                                        "location": "header",
                                        "name": "X-API-Key"
                                    }],
                                    "tee_details": None,
                                    "created_at": "2024-01-01T00:00:00Z",
                                    "updated_at": "2024-01-01T00:00:00Z"
                                }
                            }]
                        },
                        "took": 1
                    }
            return {
                "hits": {
                    "total": {"value": 0},
                    "hits": []
                },
                "took": 1
            }

        mock_es_instance.search.side_effect = mock_search
        mock_es_instance.indices.create.return_value = {"acknowledged": True}
        mock_es_instance.indices.exists.return_value = False
        mock_es.return_value = mock_es_instance
        mock_es_search.return_value = mock_es_instance

        # Mock SearchService
        mock_search_instance = Mock()
        
        def mock_search_agents(search_request, client_id=None):
            from app.schemas.agent import AgentSearchResponse
            from datetime import datetime
            
            # Return mock search results
            return AgentSearchResponse(
                registry_version="1.0.0",
                timestamp=datetime.utcnow().isoformat(),
                resources=[{
                    "id": "search-test-agent",
                    "name": "Search Test Agent",
                    "version": "1.0.0",
                    "description": "An agent for testing search",
                    "provider": "Search Test Provider",
                    "tags": ["search", "test"],
                    "is_public": True,
                    "is_active": True,
                    "location": {
                        "url": "http://localhost:8000/agents/search-test-agent/card",
                        "type": "agent_card"
                    },
                    "capabilities": {
                        "a2a_version": "1.0",
                        "supported_protocols": ["http"]
                    },
                    "auth_schemes": [{
                        "type": "apiKey",
                        "location": "header",
                        "name": "X-API-Key"
                    }],
                    "tee_details": None,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }],
                total_count=1,
                search_metadata={
                    "query": search_request.query,
                    "filters_applied": search_request.filters or {},
                    "search_time_ms": 1,
                    "total_hits": 1,
                    "semantic_search": search_request.semantic,
                    "similarity_threshold": None
                },
                pagination={
                    "page": search_request.page,
                    "per_page": search_request.per_page,
                    "total_count": 1,
                    "total_pages": 1
                }
            )
        
        mock_search_instance.search_agents.side_effect = mock_search_agents
        mock_search_service.return_value = mock_search_instance

        yield {
            "redis": mock_redis_instance,
            "elasticsearch": mock_es_instance,
            "search_service": mock_search_instance
        }
