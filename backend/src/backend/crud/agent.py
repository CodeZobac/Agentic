"""
CRUD operations for agent management.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from backend.crud.base import CRUDBase
from backend.db.models import Agent, AgentConfig
from backend.schemas.agent import AgentCreate, AgentUpdate, AgentConfigCreate


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    """
    CRUD operations for Agent model.
    """
    
    def create_with_owner(
        self, db: Session, *, obj_in: AgentCreate, user_id: int
    ) -> Agent:
        """
        Create a new agent with an owner.
        
        Args:
            db: Database session.
            obj_in: Agent data.
            user_id: ID of the owner.
            
        Returns:
            Agent: Created agent.
        """
        obj_in_data = obj_in.dict(exclude={"config"})
        db_obj = Agent(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create agent config if provided
        if obj_in.config:
            config_data = obj_in.config.dict()
            db_config = AgentConfig(**config_data, agent_id=db_obj.id, user_id=user_id)
            db.add(db_config)
            db.commit()
            db.refresh(db_obj)
        
        return db_obj
    
    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """
        Get multiple agents by owner.
        
        Args:
            db: Database session.
            user_id: ID of the owner.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List[Agent]: List of agents owned by the user.
        """
        return (
            db.query(self.model)
            .filter(Agent.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Agent,
        obj_in: Union[AgentUpdate, Dict[str, Any]]
    ) -> Agent:
        """
        Update an agent.
        
        Args:
            db: Database session.
            db_obj: Existing agent.
            obj_in: Updated agent data.
            
        Returns:
            Agent: Updated agent.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
            config_data = update_data.pop("config", None)
        else:
            update_data = obj_in.dict(exclude_unset=True, exclude={"config"})
            config_data = obj_in.config.dict(exclude_unset=True) if obj_in.config else None
        
        # Update agent config if provided
        if config_data and db_obj.config:
            for field, value in config_data.items():
                setattr(db_obj.config, field, value)
            db.add(db_obj.config)
        
        # Continue with normal update for agent
        return super().update(db, db_obj=db_obj, obj_in=update_data)


agent = CRUDAgent(Agent)