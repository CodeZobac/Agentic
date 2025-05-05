"""
Task-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator

from backend.schemas.base import BaseSchema
from backend.schemas.agent import Agent


class TaskStepBase(BaseSchema):
    """
    Base schema for task step data.
    """
    step_number: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = "pending"


class TaskStepCreate(TaskStepBase):
    """
    Schema for creating a new task step.
    """
    task_id: int
    agent_id: int


class TaskStepUpdate(TaskStepBase):
    """
    Schema for updating a task step.
    """
    status: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None


class TaskStepInDBBase(TaskStepBase):
    """
    Base schema for a task step in the database.
    """
    id: int
    task_id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime


class TaskStep(TaskStepInDBBase):
    """
    Schema for a task step.
    """
    pass


class TaskBase(BaseSchema):
    """
    Base schema for task data.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    expected_output: Optional[str] = None
    status: Optional[str] = "pending"
    result: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    title: str
    description: str
    expected_output: str
    agent_ids: List[int]


class TaskUpdate(TaskBase):
    """
    Schema for updating a task.
    """
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    agent_ids: Optional[List[int]] = None


class TaskInDBBase(TaskBase):
    """
    Base schema for a task in the database.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class Task(TaskInDBBase):
    """
    Schema for a task.
    """
    agents: Optional[List[Agent]] = None
    tasks_steps: Optional[List[TaskStep]] = None