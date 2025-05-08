# Makefile for managing Docker Compose lifecycle

.PHONY: build up down build-up logs logs-agent logs-bedrock logs-mongo clean prune-system prune-all help

# Default command - build and then up
default: build-up

# Build the Docker images
build:
	@echo "Building Docker images..."
	docker compose build

# Start the services in detached mode
up:
	@echo "Starting Docker services in detached mode..."
	docker compose up -d

# Build images and then start services in detached mode
build-up: build up
	@echo "Build complete and services started."

# Stop and remove the services
down:
	@echo "Stopping and removing Docker services..."
	docker compose down

# View logs for all services (follow mode)
logs:
	@echo "Tailing logs for all services... (Ctrl+C to stop)"
	docker compose logs -f

# View logs for the agent service
logs-agent:
	@echo "Tailing logs for agent service... (Ctrl+C to stop)"
	docker compose logs -f agent

# View logs for the Bedrock RAG MCP service
logs-bedrock:
	@echo "Tailing logs for bedrock-rag-mcp service... (Ctrl+C to stop)"
	docker compose logs -f bedrock-rag-mcp

# View logs for the MongoDB MCP service
logs-mongo:
	@echo "Tailing logs for mongodb-mcp service... (Ctrl+C to stop)"
	docker compose logs -f mongodb-mcp

# Legacy logs-service (can be removed if new ones are preferred)
logs-service:
	@echo "Tailing logs for service: ${service}... (Ctrl+C to stop)"
	docker compose logs -f ${service}

# Clean up: Stop services, remove containers, networks, and volumes defined in compose
clean: down
	@echo "Removing Docker volumes defined in docker-compose.yml..."
	docker compose down -v

# Prune system: Remove all unused containers, networks, images (dangling and unreferenced).
prune-system:
	@echo "Pruning unused Docker resources (containers, networks, images)..."
	docker system prune -f

# Prune all: Clean compose environment then prune all unused Docker resources including volumes and images.
prune-all: clean
	@echo "Pruning all unused Docker resources including volumes and images..."
	docker system prune --volumes --all -f

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build          Build Docker images for all services."
	@echo "  up             Start all services in detached mode."
	@echo "  build-up       Build Docker images and then start services in detached mode (default)."
	@echo "  down           Stop and remove containers for all services."
	@echo "  logs           Follow logs for all services."
	@echo "  logs-agent     Follow logs for the agent service."
	@echo "  logs-bedrock   Follow logs for the bedrock-rag-mcp service."
	@echo "  logs-mongo     Follow logs for the mongodb-mcp service."
	@echo "  logs-service service=<name>  (Legacy) Follow logs for a specific service."
	@echo "  clean          Stop services, remove containers, networks, and volumes defined in compose."
	@echo "  prune-system   Remove all unused Docker containers, networks, and images (system-wide)."
	@echo "  prune-all      Remove all unused Docker containers, networks, images, and volumes (system-wide, implies clean)."
	@echo "  help           Show this help message."
	@echo "  default        Alias for 'build-up'." 