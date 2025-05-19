# Agentic Backend

A robust Python backend solution that integrates advanced AI agent capabilities via Crew AI. The solution enables efficient handling of complex tasks by delegating responsibilities to AI agents, while ensuring seamless integration with traditional backend services provided by FastAPI.

## Features

- AI Agents Integration using Crew AI
- RESTful API with FastAPI
- Authentication and Authorization
- Modular and extensible architecture
- SQLAlchemy for database operations
- Comprehensive testing suite

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
poetry install
```

4. Create a .env file with the following variables:

```
DATABASE_URL=sqlite:///./agentic.db
SECRET_KEY=your-secret-key
```

### Running the Application

```bash
poetry run uvicorn backend.main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

## Project Structure

```
backend/
├── src/
│   └── backend/
│       ├── agents/         # CrewAI agent definitions
│       ├── api/            # API endpoints 
│       ├── core/           # Core configuration
│       ├── db/             # Database models and operations
│       ├── schemas/        # Pydantic schemas
│       └── services/       # Business logic
├── tests/                  # Test suite
└── pyproject.toml          # Project configuration
```

## Testing

```bash
poetry run pytest
```

## API Documentation

The API documentation is automatically generated using Swagger UI and is available at `/docs` endpoint when the application is running.
