"""
CLI utility for the Agentic backend.
"""
import argparse
import logging
import sys
import os
from pathlib import Path
from contextlib import contextmanager

from backend.core.config import settings
from backend.db.database import Base, engine, SessionLocal
from backend.main import start as start_app
from backend.crud.agent import agent as agent_crud
from backend.crud.task import task as task_crud
from backend.schemas.agent import AgentCreate, AgentConfigBase
from backend.schemas.task import TaskCreate
from backend.agents.crew import CrewManager

# Default User ID for entities created via CLI
DEFAULT_USER_ID = 1

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_command(args):
    """Initialize database."""
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")

def run_app_command(args):
    """Run application."""
    start_app()

def handle_create_agent(args):
    """Handles the 'create-agent' CLI command."""
    with get_db_session() as db:
        agent_config_data = {}
        if args.model:
            agent_config_data["model"] = args.model
        if args.temperature is not None:
            agent_config_data["temperature"] = args.temperature
        if args.verbose is not None: # Check if flag was used
            agent_config_data["verbose"] = args.verbose
        if args.allow_delegation is not None:
             agent_config_data["allow_delegation"] = args.allow_delegation

        parsed_tools = []
        if args.tools:
            tool_names = [tool.strip() for tool in args.tools.split(',')]
            if tool_names:
                 agent_config_data["tools"] = {"tools": [{"name": name} for name in tool_names]}


        agent_config = AgentConfigBase(**agent_config_data) if agent_config_data else None

        agent_in = AgentCreate(
            name=args.name,
            role=args.role,
            goal=args.goal,
            backstory=args.backstory,
            config=agent_config
        )
        agent = agent_crud.create_with_owner(db=db, obj_in=agent_in, user_id=DEFAULT_USER_ID)
        logging.info(f"Agent '{agent.name}' created with ID: {agent.id}")

def handle_create_task(args):
    """Handles the 'create-task' CLI command."""
    with get_db_session() as db:
        try:
            agent_ids = [int(id_str.strip()) for id_str in args.agent_ids.split(',')]
        except ValueError:
            logging.error("Invalid agent IDs. Please provide a comma-separated list of integers.")
            return

        task_in = TaskCreate(
            title=args.title,
            description=args.description,
            expected_output=args.expected_output,
            agent_ids=agent_ids
        )
        task = task_crud.create_with_owner(db=db, obj_in=task_in, user_id=DEFAULT_USER_ID)
        logging.info(f"Task '{task.title}' created with ID: {task.id}")

def handle_run_task(args):
    """Handles the 'run-task' CLI command."""
    with get_db_session() as db:
        # First, check if the task exists
        task = task_crud.get(db, id=args.task_id)
        if not task:
            logging.error(f"Task with ID {args.task_id} not found.")
            return
        if task.user_id != DEFAULT_USER_ID: # Basic check if CLI should manage this task
            logging.warning(f"Task {args.task_id} was not created by the CLI user (user_id {DEFAULT_USER_ID}). Proceeding with caution.")

        crew_manager = CrewManager(db=db)
        logging.info(f"Attempting to run task ID: {args.task_id}")
        crew_manager.execute_task(task_id=args.task_id)
        # FYI execute_task runs in a separate thread.
        # The CLI will print this message and exit, while the task runs in the background.
        logging.info(f"Task {args.task_id} execution started in the background.")


def main():
    """Execute CLI command."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Agentic Backend CLI")
    subparsers = parser.add_subparsers(title="Commands", dest="command", help="Available commands")
    subparsers.required = True # Make sure a subcommand is provided

    # Init DB command
    parser_init_db = subparsers.add_parser("init-db", help="Initialize database")
    parser_init_db.set_defaults(func=init_db_command)

    # Run app command
    parser_run_app = subparsers.add_parser("run", help="Run application")
    parser_run_app.set_defaults(func=run_app_command)

    # Create Agent command
    parser_create_agent = subparsers.add_parser("create-agent", help="Create a new agent")
    parser_create_agent.add_argument("--name", type=str, required=True, help="Name of the agent")
    parser_create_agent.add_argument("--role", type=str, required=True, help="Role of the agent")
    parser_create_agent.add_argument("--goal", type=str, required=True, help="Goal of the agent")
    parser_create_agent.add_argument("--backstory", type=str, help="Backstory of the agent")
    parser_create_agent.add_argument("--tools", type=str, help="Comma-separated list of tool names (e.g., 'search,calculator')")
    parser_create_agent.add_argument("--model", type=str, help="Model name to use (e.g., 'ollama/mistral:7b')")
    parser_create_agent.add_argument("--temperature", type=float, help="Model temperature")
    parser_create_agent.add_argument("--verbose", action=argparse.BooleanOptionalAction, help="Enable verbose logging for the agent")
    parser_create_agent.add_argument("--allow-delegation", type=lambda x: (str(x).lower() == 'true'), choices=[True, False], help="Allow agent delegation (true/false)")
    parser_create_agent.set_defaults(func=handle_create_agent)

    # Create Task command
    parser_create_task = subparsers.add_parser("create-task", help="Create a new task")
    parser_create_task.add_argument("--title", type=str, required=True, help="Title of the task")
    parser_create_task.add_argument("--description", type=str, required=True, help="Description of the task")
    parser_create_task.add_argument("--expected-output", type=str, required=True, help="Expected output of the task")
    parser_create_task.add_argument("--agent-ids", type=str, required=True, help="Comma-separated list of agent IDs")
    parser_create_task.set_defaults(func=handle_create_task)

    # Run Task command
    parser_run_task = subparsers.add_parser("run-task", help="Run a specific task by ID")
    parser_run_task.add_argument("--task-id", type=int, required=True, help="ID of the task to run")
    parser_run_task.set_defaults(func=handle_run_task)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        # If a user just types 'python cli.py' without any command.
        # If this happens, argparse itself will show help if no command is given.
        # This is more of a fallback.
        if not any(vars(args).values()): # If no arguments were passed at all
             parser.print_help()


if __name__ == "__main__":
    main()
