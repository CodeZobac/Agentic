"""
Task manager for orchestrating crews of AI agents.
"""
from typing import Dict, List, Optional, Any
import asyncio
import json
import threading
from datetime import datetime

from crewai import Crew, Process, Task as CrewTask
from sqlalchemy.orm import Session

from backend.agents.factory import AgentFactory
from backend.db.models import Task, Agent, TaskStep
from backend.crud.task import task as task_crud
from backend.schemas.task import TaskStepCreate, TaskUpdate


class CrewManager:
    """
    Manager for creating and running Crew AI crews for task execution.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the crew manager.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.running_tasks = {}  # Dict to track running tasks and their threads
    
    def execute_task(self, task_id: int) -> None:
        """
        Execute a task asynchronously using CrewAI.
        
        This method creates a new thread to run the task and tracks it in the manager.
        
        Args:
            task_id: ID of the task to execute.
        """
        # Check if task is already running
        if task_id in self.running_tasks:
            return
        
        # Start a new thread to execute the task
        thread = threading.Thread(
            target=self._execute_task_thread,
            args=(task_id,),
            daemon=True
        )
        self.running_tasks[task_id] = thread
        thread.start()
    
    def _execute_task_thread(self, task_id: int) -> None:
        """
        Thread method to execute a task using CrewAI.
        
        Args:
            task_id: ID of the task to execute.
        """
        try:
            # Update task status to in_progress
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            
            task_update = TaskUpdate(status="in_progress")
            task_crud.update(self.db, db_obj=task, obj_in=task_update)
            
            # Create crew agents from the task's assigned agents
            crew_agents = []
            for agent in task.agents:
                crew_agent = AgentFactory.create_agent(agent)
                crew_agents.append(crew_agent)
            
            if not crew_agents:
                # No agents available
                task_update = TaskUpdate(
                    status="failed",
                    result={"error": "No agents assigned to task"}
                )
                task_crud.update(self.db, db_obj=task, obj_in=task_update)
                return
            
            # Create crew tasks for each agent
            crew_tasks = []
            for i, agent in enumerate(crew_agents):
                # Create task step entry
                step_number = i + 1
                step_create = TaskStepCreate(
                    task_id=task_id,
                    agent_id=task.agents[i].id,
                    step_number=step_number,
                    status="in_progress",
                    input_data={"context": task.description}
                )
                task_step = task_crud.add_task_step(self.db, obj_in=step_create)
                
                # Create crew task
                crew_task = CrewTask(
                    description=task.description,
                    expected_output=task.expected_output,
                    agent=agent
                )
                crew_tasks.append(crew_task)
            
            # Create and run the crew
            crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                process=Process.sequential  # Use sequential processing by default
            )
            
            # Execute the crew
            result = crew.kickoff()
            
            # Update task with result
            task_update = TaskUpdate(
                status="completed",
                result={"output": result}
            )
            task_crud.update(self.db, db_obj=task, obj_in=task_update)
            
            # Update all task steps to completed
            steps = task_crud.get_task_steps(self.db, task_id=task_id)
            for step in steps:
                if step.status != "completed":
                    step.status = "completed"
                    step.output_data = {"part_of_result": True}
                    step.updated_at = datetime.utcnow()
                    self.db.add(step)
            
            self.db.commit()
            
        except Exception as e:
            # Handle any errors
            task_update = TaskUpdate(
                status="failed",
                result={"error": str(e)}
            )
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if task:
                task_crud.update(self.db, db_obj=task, obj_in=task_update)
        
        finally:
            # Remove task from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task.
            
        Returns:
            Dict[str, Any]: Status information for the task.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"status": "not_found"}
        
        steps = task_crud.get_task_steps(self.db, task_id=task_id)
        
        return {
            "id": task.id,
            "status": task.status,
            "title": task.title,
            "is_running": task_id in self.running_tasks,
            "steps": [
                {
                    "id": step.id,
                    "agent_id": step.agent_id,
                    "step_number": step.step_number,
                    "status": step.status
                }
                for step in steps
            ],
            "result": task.result
        }