# Bedrock RAG MCP Service

This service provides an interface for Retrieval Augmented Generation (RAG) capabilities using AWS Bedrock.

## Overview

The Bedrock RAG MCP (Multi-Container Platform) service is a specialized component designed to handle RAG-related tasks. It likely interacts with an AWS Knowledge Base and uses reranking models to provide relevant and context-aware responses.

## Features

-   Integrates with AWS Bedrock.
-   Supports Knowledge Base interactions (configurable via `KNOWLEDGE_BASE_ID`).
-   Implements reranking for search results (`USE_RERANKING`, `RERANK_MODEL_ID`).
-   Configurable logging and operational environment.

## Getting Started

### Prerequisites

-   Docker and Docker Compose installed.
-   AWS credentials configured if connecting to AWS services (though currently commented out in `docker-compose.yml`).
-   An `.env` file within the `./mcp_servers/bedrock_rag` directory with necessary environment variables.

### Running the Service

The Bedrock RAG MCP service is defined in the main `docker-compose.yml` file at the root of the project.

1.  **Navigate to the project root directory.**
2.  **Start the service:**
    ```bash
    docker-compose up bedrock-rag-mcp
    ```
    Or, to run all services defined in the `docker-compose.yml`:
    ```bash
    docker-compose up -d
    ```

The service will be accessible on the port defined by `BEDROCK_RAG_PORT` (defaulting to `3003`).

## Configuration

Environment variables for this service can be configured in `mcp_servers/bedrock_rag/.env`. Key configurations include:

-   `SERVER_HOST`: Host address for the server (default: `0.0.0.0`).
-   `BEDROCK_RAG_PORT`: Port for the service (default: `3003`).
-   `DEBUG`: Enable/disable debug mode (default: `False`).

-   **AWS Credentials (if enabled):**
    -   `AWS_REGION`
    -   `AWS_ACCESS_KEY_ID`
    -   `AWS_SECRET_ACCESS_KEY`
    -   `AWS_SESSION_TOKEN`

-   **Knowledge Base Settings (if used):**
    -   `KNOWLEDGE_BASE_ID`

-   **Reranking Settings:**
    -   `USE_RERANKING`: Enable/disable reranking (default: `True`).
    -   `RERANK_MODEL_ID`: Model ID for reranking (default: `amazon.rerank-v1:0`).
    -   `INITIAL_RESULTS`: Number of initial results to fetch (default: `5`).
    -   `TOP_N_RESULTS`: Number of top results to return after reranking (default: `3`).

-   **Logging Settings:**
    -   `LOG_LEVEL`: Logging level (default: `INFO`).

-   **Environment:**
    -   `ENVIRONMENT`: Deployment environment (default: `development`).

## Development

The service's main application logic can be found in `mcp_servers/bedrock_rag/bedrockRag_mcp_server.py`.

-   The Docker build context is `./mcp_servers/bedrock_rag`.
-   The service runs the command `python bedrockRag_mcp_server.py --host 0.0.0.0`.
