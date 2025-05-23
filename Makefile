.PHONY: start stop build logs clean init all

all: start

# Start all services
start:
	docker compose up -d
	@echo "Services started. Backend available at http://localhost:8000 and Ollama at http://localhost:11434"
	@echo "Pulling models from Ollama..."
	docker exec agentic-ollama-1 ollama pull mistral:7b
	@echo "Models pulled. Starting backend..."
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

agent1:
	docker exec agentic-backend-1 python run.py create-agent \
  --name "Research Specialist" \
  --role "Senior Research Analyst" \
  --goal "Conduct thorough research on any given topic and provide comprehensive, well-structured analysis" \
  --backstory "You are an experienced research analyst with 10+ years in academia and industry. You excel at finding reliable sources, synthesizing complex information, and presenting findings in a clear, actionable format." \
  --tools "search,web_scraper" \
  --model "ollama/mistral:7b" \
  --temperature 0.3 \
  --verbose \
  --allow-delegation false

agent2:
	docker exec agentic-backend-1 python run.py create-agent \
  --name "Content Writer" \
  --role "Senior Content Specialist" \
  --goal "Create engaging, well-structured content based on research and analysis provided by other team members" \
  --backstory "You are a skilled content writer with expertise in technical writing, marketing copy, and educational materials. You excel at transforming complex research into clear, compelling narratives that resonate with target audiences." \
  --tools "file_writer,text_editor" \
  --model "ollama/mistral:7b" \
  --temperature 0.7 \
  --verbose \
  --allow-delegation false

task:
	docker exec agentic-backend-1 python run.py create-task \
  --title "AI Technology Research and Article" \
  --description "Research the latest developments in AI technology for 2025 and create a comprehensive article based on the findings" \
  --expected-output "A well-researched, engaging article about AI technology trends in 2025, approximately 1000-1500 words" \
  --agent-ids "1,2"

run-task:
	docker exec agentic-backend-1 python run.py run-task --task-id 1

# List all created agents
list-agents:
	docker exec agentic-backend-1 python run.py list-agents

# Add a status command to check task progress
status:
	@echo "Checking containers status..."
	docker compose ps
	@echo "\nChecking available models in Ollama..."
	docker exec agentic-ollama-1 ollama list
	@echo "\nChecking backend logs..."
	docker logs agentic-backend-1 --tail 10
