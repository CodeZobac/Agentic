"""
Agent-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator

from backend.schemas.base import BaseSchema


class AgentConfigBase(BaseSchema):
    """
    Base schema for agent configuration.
    """
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    verbose: Optional[bool] = False
    allow_delegation: Optional[bool] = True
    tools: Optional[Dict[str, Any]] = None


class AgentConfigCreate(AgentConfigBase):
    """
    Schema for creating an agent configuration.
    """
    agent_id: int


class AgentConfigUpdate(AgentConfigBase):
    """
    Schema for updating an agent configuration.
    """
    pass


class AgentConfigInDBBase(AgentConfigBase):
    """
    Base schema for an agent configuration in the database.
    """
    id: int
    agent_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class AgentConfig(AgentConfigInDBBase):
    """
    Schema for an agent configuration.
    """
    pass


class AgentBase(BaseSchema):
    """
    Base schema for agent data.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None


class AgentCreate(AgentBase):
    """
    Schema for creating a new agent.
    """
    name: str
    role: str
    goal: str
    config: Optional[AgentConfigBase] = None


class AgentUpdate(AgentBase):
    """
    Schema for updating an agent.
    """
    config: Optional[AgentConfigBase] = None


class AgentInDBBase(AgentBase):
    """
    Base schema for an agent in the database.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class Agent(AgentInDBBase):
    """
    Schema for an agent.
    """
    config: Optional[AgentConfig] = None