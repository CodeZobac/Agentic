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

## Project Structure

```
agentic/
├── backend/                    # Backend application
│   ├── src/backend/
│   │   ├── api/               # REST API endpoints
│   │   ├── agents/            # Agent management and CrewAI integration
│   │   ├── core/              # Configuration and security
│   │   ├── crud/              # Database operations
│   │   ├── db/                # Database models and connection
│   │   └── schemas/           # Pydantic models for API
│   ├── cli.py                 # Command-line interface
│   ├── run.py                 # Application entry point
│   └── Dockerfile             # Backend container configuration
├── docker-compose.yml         # Service orchestration
├── Makefile                   # Convenient commands for testing
└── README.md                  # This file
```

The backend is designed as a microservice that can:
- Manage AI agents with different roles and capabilities
- Create and execute complex tasks using multiple agents
- Provide both REST API and CLI interfaces
- Scale horizontally with Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile commands)

### Quick Start with Docker Compose

The easiest way to get started is using the provided Makefile commands that handle all the Docker setup automatically.

#### 1. Start All Services

```bash
make start
```

This command will:
- Start all Docker containers (backend and Ollama)
- Pull the required Mistral 7B model from Ollama
- Set up the backend service
- Make the backend available at http://localhost:8000
- Make Ollama available at http://localhost:11434

#### 2. Initialize the Database

```bash
make init
```

This creates all necessary database tables.

#### 3. Check System Status

```bash
make status
```

This shows:
- Container status
- Available Ollama models
- Recent backend logs

### Testing the Backend with Agents

The system includes convenient Make commands to create and test AI agents:

#### Create Test Agents

Create two different agents with distinct roles:

```bash
# Create a Research Specialist agent
make agent1

# Create a Content Writer agent  
make agent2
```

#### Create and Execute a Task

```bash
# Create a task that uses both agents
make task

# Execute the task
make run-task
```

#### Monitor Execution

```bash
# Check logs to see task execution progress
make logs

# Check overall system status
make status
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make start` | Start all services (backend + Ollama) |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make init` | Initialize database |
| `make status` | Check system status |
| `make logs` | Follow real-time logs |
| `make agent1` | Create Research Specialist agent |
| `make agent2` | Create Content Writer agent |
| `make list-agents` | List all created agents |
| `make task` | Create a sample task |
| `make run-task` | Execute the created task |
| `make clean` | Stop services and remove volumes |
| `make build` | Build Docker images |

### Manual Installation (Alternative)

If you prefer to run without Docker:

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

3. Install and start Ollama, then pull the model:
```bash
ollama pull mistral:7b
```

4. Create a `.env` file in the `backend` directory:
```
DATABASE_URL=sqlite:///./agentic.db
SECRET_KEY=your-secret-key-here
OLLAMA_BASE_URL=http://localhost:11434
```

5. Run the backend:
```bash
cd backend
python run.py init-db
python run.py run
```

### API Access

The backend API will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Usage Examples

### Using the CLI (Recommended for Testing)

The backend includes a comprehensive CLI that works seamlessly with the Docker setup:

#### Creating Agents via CLI

```bash
# Create a research agent
docker exec agentic-backend-1 python run.py create-agent \
  --name "Data Analyst" \
  --role "Senior Data Scientist" \
  --goal "Analyze complex datasets and extract meaningful insights" \
  --backstory "Expert in statistical analysis with 8+ years experience" \
  --model "ollama/mistral:7b" \
  --temperature 0.2 \
  --verbose

# Create a writing agent
docker exec agentic-backend-1 python run.py create-agent \
  --name "Technical Writer" \
  --role "Documentation Specialist" \
  --goal "Create clear, comprehensive technical documentation" \
  --backstory "Professional technical writer specializing in complex topics" \
  --model "ollama/mistral:7b" \
  --temperature 0.6 \
  --verbose
```

#### Creating and Running Tasks via CLI

```bash
# Create a task that uses multiple agents
docker exec agentic-backend-1 python run.py create-task \
  --title "Market Analysis Report" \
  --description "Analyze current market trends and create a comprehensive report" \
  --expected-output "A detailed market analysis report with insights and recommendations" \
  --agent-ids "1,2"

# Execute the task
docker exec agentic-backend-1 python run.py run-task --task-id 1
```

#### CLI Command Reference

```bash
# Initialize database
docker exec agentic-backend-1 python run.py init-db

# Create an agent
docker exec agentic-backend-1 python run.py create-agent [options]

# Create a task
docker exec agentic-backend-1 python run.py create-task [options]

# Run a task
docker exec agentic-backend-1 python run.py run-task --task-id <id>

# Start the web server
docker exec agentic-backend-1 python run.py run
```

### Using the REST API

For programmatic access, you can use the REST API:

#### Creating an Agent via API

```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Researcher",
    "description": "An AI agent that researches topics",
    "role": "researcher",
    "goal": "Find accurate information",
    "backstory": "This agent is specialized in researching topics and finding accurate information."
  }'
```

#### Creating a Task via API

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research quantum computing",
    "description": "Research the latest developments in quantum computing",
    "expected_output": "A summary of recent breakthroughs in quantum computing",
    "agent_ids": [1, 2]
  }'
```

#### Executing a Task via API

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/1/execute"
```

### Complete Testing Workflow

Here's a complete workflow to test the system from scratch:

```bash
# 1. Start all services
make start

# 2. Initialize database
make init

# 3. Create test agents
make agent1
make agent2

# 4. Create a test task
make task

# 5. Execute the task
make run-task

# 6. Monitor execution
make logs

# 7. Check status
make status
```

## Troubleshooting

### Common Issues and Solutions

#### Services Won't Start
```bash
# Check if ports are in use
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :11434

# Force restart
make clean
make start
```

#### Model Download Issues
```bash
# Check Ollama container logs
docker logs agentic-ollama-1

# Manually pull the model
docker exec agentic-ollama-1 ollama pull mistral:7b

# Verify model is available
docker exec agentic-ollama-1 ollama list
```

#### Database Issues
```bash
# Reinitialize database
make clean
make start
make init
```

#### Task Execution Problems
```bash
# Check backend logs
docker logs agentic-backend-1 --tail 50

# Verify agents exist
docker exec agentic-backend-1 python run.py list-agents

# Check system status
make status
```

### Logs and Debugging

```bash
# View all logs
make logs

# View specific container logs
docker logs agentic-backend-1
docker logs agentic-ollama-1

# Follow logs in real-time
docker logs -f agentic-backend-1
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Crew AI](https://github.com/joaomdmoura/crewAI)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- LLM integration via [Ollama](https://ollama.ai/)