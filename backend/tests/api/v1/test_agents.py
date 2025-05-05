"""
Tests for agent management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import get_password_hash
from backend.db.models import User, Agent
from backend.schemas.agent import AgentCreate


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def user_token_headers(client: TestClient, test_user: User) -> dict:
    """Get user token headers for authentication."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_agent(client: TestClient, db: Session, user_token_headers: dict) -> None:
    """Test agent creation endpoint."""
    # Create a new agent
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent",
        "role": "tester",
        "goal": "To test the API",
        "backstory": "This agent was created for testing"
    }
    
    response = client.post(
        "/api/v1/agents",
        json=agent_data,
        headers=user_token_headers
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["role"] == "tester"
    assert data["goal"] == "To test the API"
    
    # Check database
    agent = db.query(Agent).filter(Agent.name == "Test Agent").first()
    assert agent is not None
    assert agent.role == "tester"
    assert agent.goal == "To test the API"


def test_read_agents(client: TestClient, db: Session, test_user: User, user_token_headers: dict) -> None:
    """Test get all agents endpoint."""
    # Create some agents in the database
    for i in range(3):
        agent = Agent(
            name=f"Test Agent {i}",
            description=f"A test agent {i}",
            role=f"tester {i}",
            goal=f"To test the API {i}",
            backstory=f"This agent was created for testing {i}",
            user_id=test_user.id
        )
        db.add(agent)
    db.commit()
    
    # Get all agents
    response = client.get("/api/v1/agents", headers=user_token_headers)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Test Agent 0"
    assert data[1]["name"] == "Test Agent 1"
    assert data[2]["name"] == "Test Agent 2"


def test_read_agent(client: TestClient, db: Session, test_user: User, user_token_headers: dict) -> None:
    """Test get single agent endpoint."""
    # Create an agent in the database
    agent = Agent(
        name="Test Agent",
        description="A test agent",
        role="tester",
        goal="To test the API",
        backstory="This agent was created for testing",
        user_id=test_user.id
    )
    db.add(agent)
    db.commit()
    
    # Get the agent
    response = client.get(f"/api/v1/agents/{agent.id}", headers=user_token_headers)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["role"] == "tester"
    assert data["goal"] == "To test the API"


def test_update_agent(client: TestClient, db: Session, test_user: User, user_token_headers: dict) -> None:
    """Test update agent endpoint."""
    # Create an agent in the database
    agent = Agent(
        name="Test Agent",
        description="A test agent",
        role="tester",
        goal="To test the API",
        backstory="This agent was created for testing",
        user_id=test_user.id
    )
    db.add(agent)
    db.commit()
    
    # Update the agent
    update_data = {
        "name": "Updated Agent",
        "role": "updated tester",
        "goal": "To test the API updates"
    }
    
    response = client.put(
        f"/api/v1/agents/{agent.id}",
        json=update_data,
        headers=user_token_headers
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Agent"
    assert data["role"] == "updated tester"
    assert data["goal"] == "To test the API updates"
    
    # Check database
    updated_agent = db.query(Agent).filter(Agent.id == agent.id).first()
    assert updated_agent.name == "Updated Agent"
    assert updated_agent.role == "updated tester"
    assert updated_agent.goal == "To test the API updates"