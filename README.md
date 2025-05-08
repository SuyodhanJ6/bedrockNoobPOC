# Bedrock RAG System

A specialized system that leverages AWS Bedrock for Retrieval-Augmented Generation (RAG). The system provides a microservices architecture for retrieving relevant documents from AWS Bedrock knowledge bases and answering user queries with citations and context.

## System Architecture

This project follows the Model Context Protocol (MCP) architecture, which separates the agent logic from the tool implementations. The system consists of:

1. **MCP Servers**: Microservices that host tools and provide specific functionality
2. **Agent**: A client that connects to the MCP servers and uses their tools
3. **Metrics & Monitoring**: Components for tracking system performance and health

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

- Python 3.10+
- Docker and Docker Compose
- AWS Account with access to Bedrock services
- MongoDB instance

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/bedrock-rag-system.git
   cd bedrock-rag-system
   ```

2. Create a `.env` file with:
   ```
   # OpenAI API
   OPENAI_API_KEY=your-openai-key-here

   # AWS Credentials
   AWS_REGION=ca-central-1
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key

   # Bedrock Settings
   BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   KNOWLEDGE_BASE_ID=your-knowledge-base-id

   # MCP Server settings
   MCP_HOST=127.0.0.1
   BEDROCK_RAG_MCP_PORT=3003
   MONGODB_MCP_PORT=3004

   # Agent API settings
   AGENT_PORT=8000
   API_HOST=0.0.0.0

   # MongoDB settings
   MONGODB_URI=mongodb://username:password@host:port/database
   MONGODB_DB_NAME=bedrock_rag
   MONGODB_COLLECTION=conversations
   MAX_HISTORY_LENGTH=10

   # Log settings
   LOG_LEVEL=INFO
   ```

3. Start the system with Docker Compose:
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