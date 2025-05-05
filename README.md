# Agentic

A powerful platform for AI agent orchestration using Crew AI. This project implements a robust backend system that enables efficient handling of complex tasks by delegating responsibilities to AI agents, powered by Ollama and our specialized agentic-specialist model.

## Features

- **Custom Ollama Model**: Uses a specialized 7B model fine-tuned for agent orchestration
- **AI Agent Management**: Create, configure, and manage AI agents with different roles, goals, and capabilities
- **Task Orchestration**: Assign tasks to multiple agents and monitor their execution
- **RESTful API**: Complete API for agent and task management
- **Authentication & Authorization**: Secure JWT-based authentication system
- **Multi-user Support**: All agents and tasks are scoped to their owners

## Architecture

The application is built with a modular and extensible architecture:

- **Backend**: Python with FastAPI and Crew AI
- **LLM Integration**: Ollama with a specialized agentic-specialist model
- **Database**: SQLAlchemy ORM with SQLite (easy to switch to PostgreSQL, MySQL, etc.)
- **Authentication**: JWT token-based authentication
- **Testing**: Comprehensive test suite with pytest

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Ollama installed and running locally

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic.git
cd agentic
```

2. Install backend dependencies:
```bash
cd backend
poetry install
```

3. Create and start the specialized Ollama model:
```bash
# Navigate to the backend directory which contains the Modelfile
cd backend
ollama create agentic-specialist -f Modelfile
```

4. Create a `.env` file in the `backend` directory with your configuration:
```
DATABASE_URL=sqlite:///./agentic.db
SECRET_KEY=your-secret-key-here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=agentic-specialist
```

### Running the Backend

```bash
cd backend
./run.py --init-db
./run.py --run
```

The API will be available at http://localhost:8000 with API documentation at http://localhost:8000/docs

## Usage Examples

### Creating an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Researcher",
    "description": "An AI agent that researches topics",
    "role": "researcher",
    "goal": "Find accurate information",
    "backstory": "This agent is specialized in researching topics and finding accurate information."
  }'
```

### Creating a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research quantum computing",
    "description": "Research the latest developments in quantum computing",
    "expected_output": "A summary of recent breakthroughs in quantum computing",
    "agent_ids": [1, 2]
  }'
```

### Executing a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/1/execute" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Crew AI](https://github.com/joaomdmoura/crewAI)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- LLM integration via [Ollama](https://ollama.ai/)