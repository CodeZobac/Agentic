FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip packages directly instead of using Poetry
COPY pyproject.toml poetry.lock ./

# Extract dependencies from pyproject.toml and install them
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.22.0 \
    crewai>=0.18.0 \
    pydantic>=2.0.0 \
    python-dotenv>=1.0.0 \
    sqlalchemy>=2.0.0 \
    alembic>=1.11.0 \
    langchain>=0.0.331 \
    langchain-community>=0.0.10 \
    python-jose[cryptography]>=3.3.0 \
    passlib[bcrypt]>=1.7.4 \
    python-multipart>=0.0.5 \
    "email-validator>=2.2.0,<3.0.0"

# Copy application code
COPY . .

# Install the backend package in development mode
# This makes the 'backend' module importable
RUN pip install -e .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py", "--run"]