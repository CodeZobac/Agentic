"""
Task management endpoints.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_db, get_current_active_user
from backend.crud.task import task as task_crud
from backend.db.models import User, Task as TaskModel
from backend.schemas.task import Task, TaskCreate, TaskUpdate, TaskStep
from backend.agents.crew import CrewManager

router = APIRouter()


@router.get("", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Read tasks owned by current user.
    """
    tasks = task_crud.get_multi_by_owner(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return tasks


@router.post("", response_model=Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    # Comment out authentication for development
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new task owned by current user.
    """
    # For development: hardcode user_id=1 instead of requiring authentication
    user_id = 1  # Assuming user with ID 1 exists in the database
    task = task_crud.create_with_owner(
        db, obj_in=task_in, user_id=user_id
    )
    return task


@router.get("/{task_id}", response_model=Task)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    # Comment out authentication for development
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific task by ID.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Comment out user permission check for development
    # if task.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not enough permissions",
    #     )
    
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific task.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Check if the user is the owner of the task
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    task = task_crud.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}", response_model=Task)
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a specific task.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Check if the user is the owner of the task
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    task = task_crud.remove(db, id=task_id)
    return task


@router.post("/{task_id}/execute", response_model=Dict[str, Any])
def execute_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    background_tasks: BackgroundTasks,
    # Comment out authentication for development
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Execute a specific task using AI agents.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Comment out user permission check for development
    # if task.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not enough permissions",
    #     )
    
    # Check if task is already running or completed
    if task.status == "in_progress":
        return {"status": "in_progress", "message": "Task is already running"}
    
    if task.status == "completed":
        return {"status": "completed", "message": "Task is already completed", "result": task.result}
    
    # Create crew manager and execute task
    crew_manager = CrewManager(db)
    background_tasks.add_task(crew_manager.execute_task, task_id)
    
    return {"status": "started", "message": "Task execution started"}


@router.get("/{task_id}/status", response_model=Dict[str, Any])
def get_task_status(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    # Comment out authentication for development
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current status of a task.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Comment out user permission check for development
    # if task.user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not enough permissions",
    #     )
    
    # Get task status from crew manager
    crew_manager = CrewManager(db)
    status_info = crew_manager.get_task_status(task_id)
    
    return status_info


@router.get("/{task_id}/steps", response_model=List[TaskStep])
def get_task_steps(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all steps for a task.
    """
    task = task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Check if the user is the owner of the task
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    steps = task_crud.get_task_steps(db, task_id=task_id)
    return steps