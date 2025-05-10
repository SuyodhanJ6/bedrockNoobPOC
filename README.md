# Bedrock RAG System

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![AWS Bedrock](https://img.shields.io/badge/AWS%20Bedrock-232F3E.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-blueviolet)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![MCP Architecture](https://img.shields.io/badge/Architecture-MCP-lightgrey.svg)](#mcp-architecture-overview)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v0.1.0-blue.svg)](#)

A specialized system that leverages AWS Bedrock for Retrieval-Augmented Generation (RAG). The system provides a microservices architecture for retrieving relevant documents from AWS Bedrock knowledge bases and answering user queries with citations and context.

<div align="center">
  <img src="docs/NoobBedrockRag.gif" alt="NoobBedrockRag Animation" width="800">
</div>

## System Architecture

The following diagram illustrates the system setup:

![System Architecture](docs/system-arch.png)

This project follows the Model Context Protocol (MCP) architecture, which separates the agent logic from the tool implementations. The system consists of:

1. **MCP Servers**: Microservices that host tools and provide specific functionality
2. **Agent**: A client that connects to the MCP servers and uses their tools

This diagram shows:
- The **Agent Service** running the main application, including the API endpoint, the core RAG agent logic, and the MCP client manager.
- The **Bedrock RAG MCP Service** hosting the tools for interacting with AWS Bedrock.
- The **MongoDB MCP Service** hosting the tools for managing conversation history.
- The Agent's MCP Client Manager connects to both MCP servers via SSE (Server-Sent Events) connections.
- User requests come in via HTTP to the Agent API, and responses are sent back.

### MCP Architecture Overview

The MCP architecture allows for a modular design where:
- Tools and domain-specific functionality are hosted on dedicated servers
- Agents can connect to these servers via SSE (Server-Sent Events)
- Communication follows the MCP protocol, enabling interoperability

## Components

### MCP Servers

1. **Bedrock RAG MCP Server (`mcp_servers/bedrock_rag/`)**
   - Provides document retrieval services via Amazon Bedrock
   - Implements tools for retrieving and filtering documents
   - Currently implements:
     - `retrieve_documents`: Retrieves documents relevant to a query
     - `filter_by_metadata`: Filters documents by metadata field values
   - Runs on port 3003 by default

2. **MongoDB MCP Server (`mcp_servers/mongodb/`)**
   - Provides conversation history storage and retrieval services
   - Implements tools for accessing conversation history
   - Currently implements:
     - `get_conversation_history`: Retrieves conversation history for a specified ID
   - Runs on port 3004 by default

### Agent

1. **Bedrock RAG Agent (`agent/agent.py`)**
   - Main agent that answers questions using AWS Bedrock RAG capabilities
   - Uses LangChain and LangGraph to create a ReAct agent
   - Connects to the Bedrock RAG and MongoDB MCP servers
   - Handles conversation context and memory

2. **MCP Client Manager (`agent/mcp_client.py`)**
   - Handles connections to MCP servers
   - Collects tools from all servers for the agent to use

3. **Agent API Server (`agent/app.py`)**
   - Provides RESTful API for interacting with the agent
   - Handles HTTP requests and returns responses
   - Includes performance monitoring middleware

### Configuration

1. **Config Module (`agent/config/config.py`)**
   - Centralizes configuration settings loaded from environment variables
   - Provides sections for AWS credentials, Bedrock settings, MCP servers, etc.
   - Supports development and production environments

## How It Works

1. The MCP servers are started first, exposing their tools via SSE endpoints
2. The agent connects to these servers through the MCP Client Manager
3. When given a user query:
   - The agent determines if context from conversation history is needed using MongoDB MCP
   - The agent then uses the Bedrock RAG MCP to retrieve relevant documents
   - The retrieved documents are used to generate an informed answer
   - The conversation is saved to MongoDB for future context

## Getting Started

### Prerequisites

- Python 3.11
- Docker and Docker Compose
- AWS Account with access to Bedrock services
- MongoDB instance

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/bedrock-rag-system.git
   cd bedrock-rag-system
   ```

2. Configure environment variables for each component according to their individual README files.

3. Use the following make commands to build and run the system:

   ```bash
   # Build all containers
   make build
   
   # Start all services in detached mode
   make up
   
   # Start specific services
   make start-agent         # Start only the agent service
   make start-bedrock-rag   # Start only the Bedrock RAG MCP service
   make start-mongodb       # Start only the MongoDB MCP service
   
   # View logs
   make logs                # View all logs
   make logs-agent          # View agent logs
   make logs-bedrock-rag    # View Bedrock RAG MCP logs
   make logs-mongodb        # View MongoDB MCP logs
   
   # Stop services
   make down                # Stop all services
   
   # Clean up
   make clean               # Remove all containers and volumes
   
   # Run tests
   make test                # Run all tests
   ```

4. Start the system with Docker Compose if you don't want to use make:
   ```
   docker-compose up --build
   ```

## Docker Deployment

The repository includes Dockerfiles for all components, allowing for containerized deployment.

To build and run with Docker Compose:

```
docker-compose up --build
```

This will start all services defined in the docker-compose.yml file:
- Agent API server on port 8000
- Bedrock RAG MCP server on port 3003
- MongoDB MCP server on port 3004

### Accessing the API

Once the system is running, you can generate answers by sending a POST request to:
```
http://localhost:8000/v1/query
```

With a JSON body like:
```json
{
  "query": "What is AWS Bedrock?",
  "conversation_id": "optional-conversation-id"
}
```

## License

[MIT](LICENSE)