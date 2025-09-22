"""Tests for app/api/health.py - Health check endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from .base_test import BaseTest


class TestHealthAPI(BaseTest):
    """Tests for health check API endpoints."""

    @pytest.fixture
    def client(self, db_session, mock_redis, mock_opensearch, mock_health_checker_db):
        """Create a test client with mocked dependencies."""
        from app.database import get_db

        def get_test_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = get_test_db

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()

    def test_health_ready_endpoint(self, client):
        """Test health ready endpoint."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_health_live_endpoint(self, client):
        """Test health live endpoint."""
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_health_detailed_endpoint(self, client):
        """Test detailed health check endpoint."""
        # Mock the HealthChecker
        with patch('app.api.health.HealthChecker') as mock_health_checker:
            mock_checker_instance = MagicMock()
            # Create an async mock that returns the health data
            async def mock_check_all():
                return {
                    "status": "healthy",
                    "checks": {
                        "database": {"status": "healthy"},
                        "redis": {"status": "healthy"},
                        "opensearch": {"status": "healthy"}
                    }
                }
            mock_checker_instance.check_all = mock_check_all
            mock_health_checker.return_value = mock_checker_instance

            response = client.get("/health/detailed")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_health_endpoints_structure(self, client):
        """Test that health endpoints return correct structure."""
        # Test ready endpoint
        ready_response = client.get("/health/ready")
        assert ready_response.status_code == 200
        ready_data = ready_response.json()
        assert "status" in ready_data
        assert ready_data["status"] == "ready"

        # Test live endpoint
        live_response = client.get("/health/live")
        assert live_response.status_code == 200
        live_data = live_response.json()
        assert "status" in live_data
        assert live_data["status"] == "alive"

    def test_health_with_database_issues(self, client):
        """Test health check when database has issues."""
        # This would require mocking database failures
        # For now, test that the endpoint exists and responds
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # Could be unhealthy

    def test_health_with_redis_issues(self, client):
        """Test health check when Redis has issues."""
        # This would require mocking Redis failures
        # For now, test that the endpoint exists and responds
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # Could be unhealthy

    def test_health_with_opensearch_issues(self, client):
        """Test health check when OpenSearch has issues."""
        # This would require mocking OpenSearch failures
        # For now, test that the endpoint exists and responds
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # Could be unhealthy

    def test_health_detailed_structure(self, client):
        """Test that detailed health check has correct structure."""
        with patch('app.api.health.HealthChecker') as mock_health_checker:
            mock_checker_instance = MagicMock()
            # Create an async mock that returns the health data
            async def mock_check_all():
                return {
                    "status": "healthy",
                    "checks": {
                        "database": {"status": "healthy", "details": "Connected"},
                        "redis": {"status": "healthy", "details": "Connected"},
                        "opensearch": {"status": "healthy", "details": "Connected"}
                    },
                    "timestamp": "2023-01-01T00:00:00Z",
                    "version": "1.0.0"
                }
            mock_checker_instance.check_all = mock_check_all
            mock_health_checker.return_value = mock_checker_instance

            response = client.get("/health/detailed")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert "checks" in data
            assert "timestamp" in data
            assert "version" in data

    def test_health_endpoints_no_auth_required(self, client):
        """Test that health endpoints don't require authentication."""
        # Health endpoints should be publicly accessible
        ready_response = client.get("/health/ready")
        assert ready_response.status_code == 200

        live_response = client.get("/health/live")
        assert live_response.status_code == 200

    def test_health_response_times(self, client):
        """Test that health endpoints respond quickly."""
        import time

        # Test ready endpoint response time
        start_time = time.time()
        response = client.get("/health/ready")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_health_with_agent_data(self, client, db_session):
        """Test health check with actual agent data."""
        # Create some test agents
        self.setup_complete_agent(db_session, "agent-1")
        self.setup_complete_agent(db_session, "agent-2")

        # Health check should still work
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_health_detailed_checks(self, client):
        """Test individual health checks in detailed endpoint."""
        with patch('app.api.health.HealthChecker') as mock_health_checker:
            mock_checker_instance = MagicMock()
            # Create an async mock that returns the health data
            async def mock_check_all():
                return {
                    "status": "healthy",
                    "checks": {
                        "database": {"status": "healthy", "response_time_ms": 10},
                        "redis": {"status": "healthy", "response_time_ms": 5},
                        "opensearch": {"status": "healthy", "response_time_ms": 15}
                    }
                }
            mock_checker_instance.check_all = mock_check_all
            mock_health_checker.return_value = mock_checker_instance

            response = client.get("/health/detailed")
            assert response.status_code == 200

            data = response.json()
            checks = data["checks"]

            # Verify individual check structure
            assert "database" in checks
            assert "redis" in checks
            assert "opensearch" in checks

            for check_name, check_data in checks.items():
                assert "status" in check_data
                assert check_data["status"] == "healthy"
