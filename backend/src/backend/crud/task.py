"""
CRUD operations for task management.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from backend.crud.base import CRUDBase
from backend.db.models import Task, TaskAgent, TaskStep
from backend.schemas.task import TaskCreate, TaskUpdate, TaskStepCreate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """
    CRUD operations for Task model.
    """
    
    def create_with_owner(
        self, db: Session, *, obj_in: TaskCreate, user_id: int
    ) -> Task:
        """
        Create a new task with an owner.
        
        Args:
            db: Database session.
            obj_in: Task data.
            user_id: ID of the owner.
            
        Returns:
            Task: Created task.
        """
        # Create task without agents
        obj_in_data = obj_in.dict(exclude={"agent_ids"})
        db_obj = Task(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Add agent associations
        for agent_id in obj_in.agent_ids:
            task_agent = TaskAgent(task_id=db_obj.id, agent_id=agent_id)
            db.add(task_agent)
        
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """
        Get multiple tasks by owner.
        
        Args:
            db: Database session.
            user_id: ID of the owner.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List[Task]: List of tasks owned by the user.
        """
        return (
            db.query(self.model)
            .filter(Task.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Task,
        obj_in: Union[TaskUpdate, Dict[str, Any]]
    ) -> Task:
        """
        Update a task.
        
        Args:
            db: Database session.
            db_obj: Existing task.
            obj_in: Updated task data.
            
        Returns:
            Task: Updated task.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
            agent_ids = update_data.pop("agent_ids", None)
        else:
            update_data = obj_in.dict(exclude_unset=True, exclude={"agent_ids"})
            agent_ids = obj_in.agent_ids if obj_in.agent_ids is not None else None
        
        # Update agent associations if provided
        if agent_ids is not None:
            # Remove existing associations
            db.query(TaskAgent).filter(TaskAgent.task_id == db_obj.id).delete()
            
            # Add new associations
            for agent_id in agent_ids:
                task_agent = TaskAgent(task_id=db_obj.id, agent_id=agent_id)
                db.add(task_agent)
        
        # Continue with normal update for task
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def add_task_step(
        self, db: Session, *, obj_in: TaskStepCreate
    ) -> TaskStep:
        """
        Add a step to a task.
        
        Args:
            db: Database session.
            obj_in: Step data.
            
        Returns:
            TaskStep: Created task step.
        """
        step_data = obj_in.dict()
        db_step = TaskStep(**step_data)
        db.add(db_step)
        db.commit()
        db.refresh(db_step)
        return db_step
    
    def get_task_steps(
        self, db: Session, *, task_id: int
    ) -> List[TaskStep]:
        """
        Get all steps for a task.
        
        Args:
            db: Database session.
            task_id: ID of the task.
            
        Returns:
            List[TaskStep]: List of task steps.
        """
        return (
            db.query(TaskStep)
            .filter(TaskStep.task_id == task_id)
            .order_by(TaskStep.step_number)
            .all()
        )


task = CRUDTask(Task)