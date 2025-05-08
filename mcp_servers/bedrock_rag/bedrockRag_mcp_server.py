#!/usr/bin/env python
"""
Bedrock Retrieval MCP Server - Provides document retrieval services via Amazon Bedrock
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn

# Import the Bedrock RAG Handler and Config
from tools.bedrock_rag_handler import BedrockRagHandler
from config import Config

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("BedrockRetrievalTools")

# Initialize the RAG handler with config
logger.info("Initializing BedrockRagHandler")
rag_handler = BedrockRagHandler.create_default()

class DocumentRetrievalRequest(BaseModel):
    """Request model for document retrieval"""
    query: str
    context: Optional[str] = None
    max_tokens: Optional[int] = None  # Kept for backwards compatibility

class DocumentRetrievalResponse(BaseModel):
    """Response model for document retrieval"""
    sources: List[Dict[str, Any]] = []
    query: str
    document_count: Optional[int] = 0
    error: Optional[str] = None

class MetadataFilterRequest(BaseModel):
    """Request model for metadata filtering"""
    sources: List[Dict[str, Any]]
    field: str
    value: Any

class MetadataFilterResponse(BaseModel):
    """Response model for metadata filtering"""
    filtered_sources: List[Dict[str, Any]] = []
    field: str
    value: Any
    original_count: int
    filtered_count: int
    error: Optional[str] = None

@mcp.tool()
async def retrieve_documents(request: DocumentRetrievalRequest) -> DocumentRetrievalResponse:
    """
    Retrieve and rerank documents relevant to a query using Amazon Bedrock.
    
    Args:
        request: An object containing the query.
        
    Returns:
        An object containing the retrieved documents.
    """
    try:
        # Use the RAG handler to retrieve documents
        result = rag_handler.perform_rag_query(
            query=request.query,
            context=request.context,
            max_tokens=request.max_tokens
        )
        
        logger.info(f"Retrieved documents for query: {request.query[:50]}...")
        logger.info(f"Found {len(result.get('sources', []))} relevant documents")
        
        # Check if there was an error
        if "error" in result and result["error"]:
            logger.error(f"Error in document retrieval: {result['error']}")
            return DocumentRetrievalResponse(
                query=request.query,
                sources=[],
                document_count=0,
                error=result["error"]
            )
        
        return DocumentRetrievalResponse(
            query=request.query,
            sources=result.get("sources", []),
            document_count=result.get("document_count", len(result.get("sources", [])))
        )
        
    except Exception as e:
        error_msg = f"Error retrieving documents: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return DocumentRetrievalResponse(
            query=request.query,
            sources=[],
            document_count=0,
            error=error_msg
        )

@mcp.tool()
async def filter_by_metadata(request: MetadataFilterRequest) -> MetadataFilterResponse:
    """
    Filter documents by metadata field value.
    
    Args:
        request: Object containing sources, field name and value to filter by
        
    Returns:
        Object containing filtered sources
    """
    try:
        # Access the handler's retriever to use filtering functionality
        filtered_sources = rag_handler.retriever.filter_by_metadata(
            request.sources,
            request.field,
            request.value
        )
        
        logger.info(f"Filtered documents by {request.field}={request.value}")
        logger.info(f"Filtered from {len(request.sources)} to {len(filtered_sources)} documents")
        
        return MetadataFilterResponse(
            filtered_sources=filtered_sources,
            field=request.field,
            value=request.value,
            original_count=len(request.sources),
            filtered_count=len(filtered_sources)
        )
        
    except Exception as e:
        error_msg = f"Error filtering documents: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return MetadataFilterResponse(
            filtered_sources=[],
            field=request.field,
            value=request.value,
            original_count=len(request.sources),
            filtered_count=0,
            error=error_msg
        )

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette app with SSE transport for the MCP server."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """Handle SSE connections"""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def main():
    """Run the Bedrock Retrieval MCP Server"""
    import argparse

    # Get MCP server instance from FastMCP
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Bedrock Document Retrieval MCP Server")
    parser.add_argument("--port", type=int, default=Config.SERVER_PORT, 
                        help=f"Port for server (default: {Config.SERVER_PORT})")
    parser.add_argument("--host", type=str, default=Config.SERVER_HOST, 
                        help=f"Host for server (default: {Config.SERVER_HOST})")
    parser.add_argument("--debug", action="store_true", default=Config.DEBUG,
                        help=f"Enable debug mode (default: {Config.DEBUG})")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Bedrock Retrieval MCP Server on {args.host}:{args.port}")
    logger.info(f"Server-Sent Events endpoint: http://{args.host}:{args.port}/sse")
    logger.info(f"Using Knowledge Base ID: {Config.KNOWLEDGE_BASE_ID}")
    
    # Create Starlette app with SSE transport
    starlette_app = create_starlette_app(mcp_server, debug=args.debug)
    
    # Run the server with uvicorn
    uvicorn.run(
        starlette_app,
        host=args.host,
        port=args.port,
    )

if __name__ == "__main__":
    main() 