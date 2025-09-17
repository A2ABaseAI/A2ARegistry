"""Tests for agent API endpoints."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.models.client import Client
from app.auth import get_password_hash

# Test database - use environment variable if available, otherwise sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL in CI
    engine = create_engine(DATABASE_URL)
else:
    # For SQLite in local testing
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database once for all tests."""
    # Ensure all tables are created
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after all tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client():
    """Create a test client for testing."""
    db = TestingSessionLocal()
    
    # Create test client
    test_client = Client(
        id="test-client-id",
        name="Test Client",
        client_id="test_client_id",
        client_secret=get_password_hash("test_secret"),
        scopes=["agent:read", "agent:write", "admin"]
    )
    
    db.add(test_client)
    db.commit()
    db.refresh(test_client)
    
    yield test_client
    
    # Cleanup
    db.delete(test_client)
    db.commit()
    db.close()


@pytest.fixture
def auth_headers(test_client):
    """Get authentication headers for test client."""
    response = client.post(
        "/oauth/token",
        data={
            "username": test_client.client_id,
            "password": "test_secret"
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_agent(auth_headers):
    """Test creating an agent."""
    agent_data = {
        "agent_card": {
            "id": "test-agent",
            "name": "Test Agent",
            "version": "1.0.0",
            "description": "A test agent",
            "capabilities": {
                "a2a_version": "1.0",
                "supported_protocols": ["http"]
            },
            "skills": {
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"}
            },
            "auth_schemes": [
                {
                    "type": "apiKey",
                    "location": "header",
                    "name": "X-API-Key"
                }
            ],
            "provider": "Test Provider",
            "tags": ["test"],
            "location": {
                "url": "https://test.example.com/agent.json",
                "type": "agent_card"
            }
        },
        "is_public": True
    }
    
    response = client.post("/agents", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["is_public"] == True


def test_get_agent(auth_headers):
    """Test getting an agent."""
    # First create an agent
    agent_data = {
        "agent_card": {
            "id": "test-agent-2",
            "name": "Test Agent 2",
            "version": "1.0.0",
            "description": "Another test agent",
            "capabilities": {
                "a2a_version": "1.0",
                "supported_protocols": ["http"]
            },
            "skills": {
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"}
            },
            "auth_schemes": [
                {
                    "type": "apiKey",
                    "location": "header",
                    "name": "X-API-Key"
                }
            ],
            "provider": "Test Provider",
            "tags": ["test"],
            "location": {
                "url": "https://test2.example.com/agent.json",
                "type": "agent_card"
            }
        },
        "is_public": True
    }
    
    create_response = client.post("/agents", json=agent_data, headers=auth_headers)
    agent_id = create_response.json()["id"]
    
    # Get the agent
    response = client.get(f"/agents/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test Agent 2"


def test_search_agents(auth_headers):
    """Test searching agents."""
    # Create a test agent
    agent_data = {
        "agent_card": {
            "id": "search-test-agent",
            "name": "Search Test Agent",
            "version": "1.0.0",
            "description": "An agent for testing search",
            "capabilities": {
                "a2a_version": "1.0",
                "supported_protocols": ["http"]
            },
            "skills": {
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"}
            },
            "auth_schemes": [
                {
                    "type": "apiKey",
                    "location": "header",
                    "name": "X-API-Key"
                }
            ],
            "provider": "Search Test Provider",
            "tags": ["search", "test"],
            "location": {
                "url": "https://search-test.example.com/agent.json",
                "type": "agent_card"
            }
        },
        "is_public": True
    }
    
    client.post("/agents", json=agent_data, headers=auth_headers)
    
    # Search for the agent
    search_data = {
        "query": "search test",
        "top": 10
    }
    
    response = client.post("/agents/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] >= 1
    assert len(data["resources"]) >= 1


def test_get_public_agents():
    """Test getting public agents without authentication."""
    response = client.get("/agents/public")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_well_known_endpoints():
    """Test well-known endpoints."""
    # Test agents index
    response = client.get("/.well-known/agents/index.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "agents" in data
    assert "total_count" in data
    
    # Test registry agent card
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == "a2a-registry"
    assert data["name"] == "A2A Agent Registry"
