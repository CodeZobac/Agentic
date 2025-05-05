"""
Database models for the Agentic backend.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from backend.db.database import Base


class JSONEncodedDict(TypeDecorator):
    """
    Represents a JSON-encoded dictionary.
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(Base):
    """
    User model for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    agent_configs = relationship("AgentConfig", back_populates="user", cascade="all, delete-orphan")


class Agent(Base):
    """
    AI Agent model.
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    role = Column(String)
    goal = Column(String)
    backstory = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    tasks = relationship("Task", secondary="task_agents", back_populates="agents")
    config = relationship("AgentConfig", back_populates="agent", uselist=False, cascade="all, delete-orphan")


class AgentConfig(Base):
    """
    Configuration for AI Agents.
    """
    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model = Column(String, default="gpt-4o")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    verbose = Column(Boolean, default=False)
    allow_delegation = Column(Boolean, default=True)
    tools = Column(JSONEncodedDict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="config")
    user = relationship("User", back_populates="agent_configs")


class Task(Base):
    """
    Task model for agent tasks.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    expected_output = Column(String)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    result = Column(JSONEncodedDict, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    agents = relationship("Agent", secondary="task_agents", back_populates="tasks")
    tasks_steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")


class TaskAgent(Base):
    """
    Association table for tasks and agents.
    """
    __tablename__ = "task_agents"

    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)


class TaskStep(Base):
    """
    Step in a task execution.
    """
    __tablename__ = "task_steps"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    step_number = Column(Integer)
    input_data = Column(JSONEncodedDict, nullable=True)
    output_data = Column(JSONEncodedDict, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="tasks_steps")
    agent = relationship("Agent")