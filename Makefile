.PHONY: start stop build logs clean init all

all: start

# Start all services
start:
	docker compose up -d
	@echo "Services started. Backend available at http://localhost:8000 and Ollama at http://localhost:11434"
	@echo "Use 'make logs' to follow logs"

# Stop all services
stop:
	docker compose down

# Build services
build:
	docker compose build

# View logs
logs:
	docker compose logs -f

# Initialize the database (run after starting services)
init:
	docker compose exec backend python run.py --init-db

# Remove containers, volumes, and database files
clean:
	docker compose down -v
	@echo "Services stopped and volumes removed"

# Restart services
restart: stop start