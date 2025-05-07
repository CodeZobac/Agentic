"""
Agent management endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_db, get_current_active_user
from backend.crud.agent import agent as agent_crud
from backend.db.models import User, Agent as AgentModel
from backend.schemas.agent import Agent, AgentCreate, AgentUpdate

router = APIRouter()


@router.get("", response_model=List[Agent])
def read_agents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # Commenting out the authentication requirement
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Read all agents. (Authentication requirement removed for development)
    """
    # Return all agents instead of just those owned by the current user
    agents = agent_crud.get_multi(db, skip=skip, limit=limit)
    return agents


@router.post("", response_model=Agent)
def create_agent(
    *,
    db: Session = Depends(get_db),
    agent_in: AgentCreate,
    # Commenting out the authentication requirement
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new agent. (Authentication requirement removed for development)
    """
    # Since we're not requiring authentication, we'll use a default user
    # Get the first user from the database or create one if none exists
    user = db.query(User).first()
    if not user:
        # If no user exists, create a default user
        from backend.core.security import get_password_hash
        user = User(
            email="default@example.com",
            username="default",
            hashed_password=get_password_hash("default"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    agent = agent_crud.create_with_owner(
        db, obj_in=agent_in, user_id=user.id
    )
    return agent


@router.get("/{agent_id}", response_model=Agent)
def read_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    # Commenting out the authentication requirement
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific agent by ID. (Authentication requirement removed for development)
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Removed permission check for development
    return agent


@router.put("/{agent_id}", response_model=Agent)
def update_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    agent_in: AgentUpdate,
    # Commenting out the authentication requirement
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific agent. (Authentication requirement removed for development)
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Removed permission check for development
    agent = agent_crud.update(db, db_obj=agent, obj_in=agent_in)
    return agent


@router.delete("/{agent_id}", response_model=Agent)
def delete_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    # Commenting out the authentication requirement
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a specific agent. (Authentication requirement removed for development)
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Removed permission check for development
    agent = agent_crud.remove(db, id=agent_id)
    return agent