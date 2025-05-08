#!/usr/bin/env python
"""
MongoDB MCP Server - Provides conversation history retrieval services
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

# Import the Conversation Handler and Config
from tools.conversation_handler import ConversationHandler
from config import Config

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

# Validate MongoDB URI before proceeding
if not Config.validate_mongodb_uri():
    logger.warning("MongoDB URI validation failed, service may not connect properly")

# Create MCP server
mcp = FastMCP("MongoDBConversationTools")

# Initialize the conversation handler with config
logger.info("Initializing ConversationHandler")
conversation_handler = ConversationHandler.create_default()

class ConversationHistoryRequest(BaseModel):
    """Request model for conversation history retrieval"""
    conversation_id: str
    limit: Optional[int] = None
    exclude_current: Optional[bool] = True

class MessageModel(BaseModel):
    """Model for a conversation message"""
    role: str
    content: str
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history retrieval"""
    conversation_id: str
    messages: List[MessageModel] = []
    message_count: int = 0
    error: Optional[str] = None

@mcp.tool()
async def get_conversation_history(request: ConversationHistoryRequest) -> ConversationHistoryResponse:
    """
    Retrieve conversation history for a specified conversation ID.
    
    Args:
        request: An object containing the conversation_id and optional limit.
        
    Returns:
        An object containing the conversation messages with user and assistant roles.
    """
    try:
        # Extract and log the raw conversation_id from the request
        # Handle both direct string and object formats from different clients
        if isinstance(request, dict):
            conv_id = request.get("conversation_id", "unknown")
            exclude_current = request.get("exclude_current", True)
            limit = request.get("limit", None)
        elif isinstance(request, ConversationHistoryRequest):
            conv_id = request.conversation_id
            exclude_current = request.exclude_current
            limit = request.limit
        else:
            # Try to convert to string if it's not a recognized type
            conv_id = str(request)
            exclude_current = True
            limit = None
            
        # Ensure it's a string and log what we received
        conv_id = str(conv_id)
        logger.info(f"Raw conversation_id received: {conv_id}")
        logger.info(f"Exclude current message: {exclude_current}")
        
        # Use the conversation handler to retrieve history
        result = conversation_handler.get_conversation_history(
            conversation_id=conv_id,
            limit=limit,
            exclude_current=exclude_current
        )
        
        logger.info(f"Retrieved conversation history for ID: {conv_id}")
        logger.info(f"Found {result.get('message_count', 0)} messages")
        
        # Check if there was an error
        if "error" in result and result["error"]:
            logger.error(f"Error in conversation retrieval: {result['error']}")
            return ConversationHistoryResponse(
                conversation_id=conv_id,
                messages=[],
                message_count=0,
                error=result["error"]
            )
        
        # Process messages to ensure they're correctly formatted
        formatted_messages = []
        for msg in result.get("messages", []):
            formatted_messages.append(MessageModel(
                role=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp", "")
            ))
        
        return ConversationHistoryResponse(
            conversation_id=conv_id,
            messages=formatted_messages,
            message_count=len(formatted_messages)
        )
        
    except Exception as e:
        error_msg = f"Error retrieving conversation history: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        
        # Get conversation_id even in case of error
        try:
            if isinstance(request, dict):
                conv_id = request.get("conversation_id", "unknown")
            elif isinstance(request, ConversationHistoryRequest):
                conv_id = request.conversation_id
            else:
                conv_id = str(request)
        except:
            conv_id = "unknown"
            
        return ConversationHistoryResponse(
            conversation_id=conv_id,
            messages=[],
            message_count=0,
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
    """Run the MongoDB Conversation MCP Server"""
    import argparse

    # Get MCP server instance from FastMCP
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="MongoDB Conversation History MCP Server")
    parser.add_argument("--port", type=int, default=Config.SERVER_PORT, 
                        help=f"Port for server (default: {Config.SERVER_PORT})")
    parser.add_argument("--host", type=str, default=Config.SERVER_HOST, 
                        help=f"Host for server (default: {Config.SERVER_HOST})")
    parser.add_argument("--debug", action="store_true", default=Config.DEBUG,
                        help=f"Enable debug mode (default: {Config.DEBUG})")
    
    args = parser.parse_args()
    
    # Display server information
    logger.info("Starting MongoDB Conversation MCP Server")
    logger.info(f"Host: {args.host}, Port: {args.port}")
    logger.info(f"Server-Sent Events endpoint: http://{args.host}:{args.port}/sse")
    logger.info(f"MongoDB Database: {Config.MONGODB_DB_NAME}")
    logger.info(f"MongoDB Collection: {Config.MONGODB_COLLECTION}")
    logger.info(f"Max History Length: {Config.MAX_HISTORY_LENGTH}")
    
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