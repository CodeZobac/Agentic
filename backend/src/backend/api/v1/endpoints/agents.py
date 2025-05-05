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
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Read agents owned by current user.
    """
    agents = agent_crud.get_multi_by_owner(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return agents


@router.post("", response_model=Agent)
def create_agent(
    *,
    db: Session = Depends(get_db),
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new agent owned by current user.
    """
    agent = agent_crud.create_with_owner(
        db, obj_in=agent_in, user_id=current_user.id
    )
    return agent


@router.get("/{agent_id}", response_model=Agent)
def read_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific agent by ID.
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if the user is the owner of the agent
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return agent


@router.put("/{agent_id}", response_model=Agent)
def update_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    agent_in: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific agent.
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if the user is the owner of the agent
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    agent = agent_crud.update(db, db_obj=agent, obj_in=agent_in)
    return agent


@router.delete("/{agent_id}", response_model=Agent)
def delete_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a specific agent.
    """
    agent = agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if the user is the owner of the agent
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    agent = agent_crud.remove(db, id=agent_id)
    return agent