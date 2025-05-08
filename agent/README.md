# Agent Service

This service is the main application component, responsible for orchestrating tasks and interacting with other backend services like Bedrock RAG and MongoDB.

## Overview

The Agent service acts as the central hub of the application. It receives requests, processes them by potentially leveraging AI capabilities from the Bedrock RAG service, and stores or retrieves data using the MongoDB service.

## Features

-   Handles primary application logic.
-   Integrates with AWS Bedrock for Retrieval Augmented Generation (RAG) via the `bedrock-rag-mcp` service.
-   Utilizes MongoDB for data persistence (e.g., conversation history) via the `mongodb-mcp` service.

## Getting Started

### Prerequisites

-   Docker and Docker Compose installed.
-   Ensure the dependent services (`bedrock-rag-mcp` and `mongodb-mcp`) are configured and running.
-   An `.env` file within the `./agent` directory with necessary environment variables (see `docker-compose.yml` for `env_file` reference).

### Running the Service

The Agent service is defined in the main `docker-compose.yml` file at the root of the project.

1.  **Navigate to the project root directory.**
2.  **Start the services:**
    ```bash
    docker-compose up agent
    ```
    Or, to run all services defined in the `docker-compose.yml`:
    ```bash
    docker-compose up -d
    ```

The service will be accessible on the port defined by `AGENT_PORT` (defaulting to `8000`).

## Configuration

Environment variables for this service can be configured in `agent/.env`. Key configurations might include:

-   `AGENT_PORT`: The port on which the agent service will listen.

(Add any other relevant environment variables or configuration details here.)

## Development

The service's main application logic can be found in `agent/app.py` and `agent/agent.py`.

-   The Docker build context is `./agent`.
-   The service runs the command `python -m agent.app`.
