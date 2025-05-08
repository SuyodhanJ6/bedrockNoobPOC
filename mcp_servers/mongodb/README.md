# MongoDB MCP Service

This service provides a MongoDB interface, likely used for data storage such as conversation history for the RAG application.

## Overview

The MongoDB MCP (Multi-Container Platform) service acts as a dedicated data layer. It exposes a MongoDB instance or an API to interact with a MongoDB database, configured for storing application-specific data.

## Features

-   Provides a MongoDB interface for other services.
-   Configurable database name (`MONGODB_DB_NAME`) and collection (`MONGODB_COLLECTION`).
-   Manages history length for stored data (e.g., conversations) via `MAX_HISTORY_LENGTH`.
-   Configurable logging.

## Getting Started

### Prerequisites

-   Docker and Docker Compose installed.
-   An `.env` file within the `./mcp_servers/mongodb` directory with necessary environment variables.

### Running the Service

The MongoDB MCP service is defined in the main `docker-compose.yml` file at the root of the project.

1.  **Navigate to the project root directory.**
2.  **Start the service:**
    ```bash
    docker-compose up mongodb-mcp
    ```
    Or, to run all services defined in the `docker-compose.yml`:
    ```bash
    docker-compose up -d
    ```

The service will be accessible on the port defined by `MONGODB_MCP_PORT` (defaulting to `3004`).

## Configuration

Environment variables for this service can be configured in `mcp_servers/mongodb/.env`. Key configurations include:

-   `SERVER_HOST`: Host address for the server (default: `0.0.0.0`).
-   `MONGODB_MCP_PORT`: Port for the service (default: `3004`).
-   `DEBUG`: Enable/disable debug mode (default: `False`).

-   **MongoDB Settings:**
    -   `MONGODB_DB_NAME`: Name of the MongoDB database (default: `bedrock_rag`).
    -   `MONGODB_COLLECTION`: Name of the MongoDB collection (default: `conversations`).
    -   `MAX_HISTORY_LENGTH`: Maximum length of history to maintain (default: `10`).

-   **Logging Settings:**
    -   `LOG_LEVEL`: Logging level (default: `INFO`).

## Development

The service's main application logic can be found in `mcp_servers/mongodb/mongodb_mcp_server.py`.

-   The Docker build context is `./mcp_servers/mongodb`.
-   The service runs the command `python mongodb_mcp_server.py --host 0.0.0.0`.
