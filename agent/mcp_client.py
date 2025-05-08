#!/usr/bin/env python
"""
MCP Client Manager - Handles connections to multiple MCP servers
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import BaseTool

# Import Config
from config import Config

# Load environment variables from .env file
load_dotenv()

class MCPClientManager:
    """Manages connections to multiple MCP servers."""
    
    def __init__(self):
        """Initialize the MCP Client Manager."""
        self.mcp_client = None
        self.mcp_config = Config.get_mcp_config()
        self.tools = []
    
    async def setup(self):
        """Set up connections to all MCP servers."""
        try:
            # Define MCP server URLs using service-specific hosts
            bedrock_rag_mcp_url = f"http://{self.mcp_config['bedrock_rag_host']}:{self.mcp_config['bedrock_rag_port']}/sse"
            mongodb_mcp_url = f"http://{self.mcp_config['mongodb_host']}:{self.mcp_config['mongodb_port']}/sse"
            
            # Connect to MCP servers
            self.mcp_client = MultiServerMCPClient(
                {
                    "bedrockragtools": {
                        "url": bedrock_rag_mcp_url,
                        "transport": "sse",
                    },
                    "mongodbtools": {
                        "url": mongodb_mcp_url,
                        "transport": "sse",
                    }
                }
            )
            
            await self.mcp_client.__aenter__()
            
            # Get tools from the MCP servers
            self.tools = self.mcp_client.get_tools()
            
            print(f"Connected to MCP servers:")
            print(f"- Bedrock RAG MCP: {bedrock_rag_mcp_url}")
            print(f"- MongoDB MCP: {mongodb_mcp_url}")
            print(f"Total tools loaded: {len(self.tools)}")
            
        except Exception as e:
            print(f"Error connecting to MCP servers: {str(e)}")
            print("Make sure the MCP servers are running at the specified URLs")
            raise
    
    def get_tools(self) -> List[BaseTool]:
        """Get all tools from the connected MCP servers.
        
        Returns:
            List of available tools
        """
        return self.tools
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_client:
            await self.mcp_client.__aexit__(None, None, None)
