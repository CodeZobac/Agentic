"""
Tests for authentication endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import get_password_hash
from backend.db.models import User


def test_register_user(client: TestClient, db: Session) -> None:
    """Test user registration endpoint."""
    # Create a new user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    
    # Check database
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_superuser is False


def test_login_user(client: TestClient, db: Session) -> None:
    """Test user login endpoint."""
    # Create user in DB
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Try to login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, db: Session) -> None:
    """Test login with incorrect password."""
    # Create user in DB
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"