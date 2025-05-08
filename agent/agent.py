#!/usr/bin/env python
"""
Bedrock RAG Agent - Agent for answering questions using AWS Bedrock RAG via MCP servers
"""

import os
import asyncio
# import boto3
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from pydantic import SecretStr
import uuid

# Load environment variables from .env file
load_dotenv()

# LangChain imports
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent

# Import the MCP client manager
from mcp_client import MCPClientManager

# Import prompt templates and config
from prompts.bedrock_rag_agent_prompt import BedrockRAGAgentPrompts
from config import Config

# Import the short-term memory
from memory.short_term_memory import ShortTermMemory

# Set up logging
Config.setup_logging()

class BedrockRAGAgent:
    """Agent that answers questions using AWS Bedrock RAG capabilities."""
    
    def __init__(self, model_id: str = None, conversation_id: str = None):
        """Initialize the Bedrock RAG Agent.
        
        Args:
            model_id: The ID of the AWS Bedrock model to use, defaults to Config.BEDROCK_MODEL_ID
            conversation_id: Unique ID for this conversation, generates one if not provided
        """
        self.model_id = model_id or Config.BEDROCK_MODEL_ID
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.llm = None
        self.agent = None
        self.mcp_client_manager = None
        self.system_prompt = BedrockRAGAgentPrompts.get_system_prompt()
        self.memory = ShortTermMemory.from_config(self.conversation_id, Config)
    
    async def setup(self):
        """Set up the agent with the appropriate model and MCP tools."""
        # Get AWS credentials from config
        aws_creds = Config.get_aws_credentials()
        model_config = Config.get_model_config()
        
        # Initialize the AWS Bedrock LLM
        self.llm = ChatBedrock(
            model_id=self.model_id,
            model_kwargs=model_config["model_kwargs"],
            region_name=aws_creds["region_name"],
            aws_access_key_id=SecretStr(aws_creds["aws_access_key_id"]),
            aws_secret_access_key=SecretStr(aws_creds["aws_secret_access_key"])
        )
        
        # Initialize the MCP client manager
        self.mcp_client_manager = MCPClientManager()
        await self.mcp_client_manager.setup()
        
        # Get tools from the MCP client manager
        mcp_tools = self.mcp_client_manager.get_tools()
        print(f"Loaded {len(mcp_tools)} tools from MCP servers")
        
        # Create the ReAct agent with MCP tools
        self.agent = create_react_agent(
            self.llm,
            mcp_tools,
            prompt=self.system_prompt
        )
    
    async def answer_question(self, user_query: str) -> Dict[str, Any]:
        """Generate an answer to a user's question using Bedrock RAG.
        
        Args:
            user_query: The user's question to answer
            
        Returns:
            Generated answer and supporting information
        """
        if not self.agent:
            await self.setup()
            
        try:
            print(f"Answering question: {user_query[:50]}...")
            
            # Add the user's query to memory (save to MongoDB but don't use for context)
            self.memory.add_message("user", user_query)
            
            # Create a generic prompt that allows the agent to choose the appropriate tool
            generic_prompt = f"""
Please answer this question: {user_query}

First determine what type of question this is:
1. If this is about conversation history, previous messages, or past interactions, use the 'get_conversation_history' tool with these EXACT parameters:
   {{
     "conversation_id": "{self.conversation_id}",
     "exclude_current": true
   }}
   
2. If this needs information from the knowledge base, use the 'retrieve_documents' tool.

Your current conversation ID is: {self.conversation_id}
Make sure to set exclude_current to true to avoid getting the current question when retrieving history.
"""
            
            # Make a single call to the agent
            messages = [HumanMessage(content=generic_prompt)]
            
            result = await self.agent.ainvoke({
                "messages": messages
            })
            
            # Find the AI's response
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            
            if not ai_messages:
                error_response = f"Error: Could not generate an answer for this query."
                self.memory.add_message("assistant", error_response)
                return {
                    "messages": [
                        HumanMessage(content=f"Answer this question: {user_query}"),
                        AIMessage(content=error_response)
                    ],
                    "error": True
                }
            
            # Store the assistant's response in memory
            self.memory.add_message("assistant", ai_messages[-1].content)
            
            return result
            
        except Exception as e:
            error_message = f"An error occurred while generating the answer: {str(e)}"
            print(error_message)
            import traceback
            print(traceback.format_exc())
            
            # Still record the error in memory
            self.memory.add_message("assistant", error_message)
            
            return {
                "messages": [
                    HumanMessage(content=f"Answer this question: {user_query}"),
                    AIMessage(content=error_message)
                ],
                "error": True
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history.
        
        Returns:
            List of message dictionaries with role, content, and timestamp
        """
        return self.memory.get_conversation_history()
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.memory.clear_conversation()
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_client_manager:
            await self.mcp_client_manager.close()
        
        # Close memory connection
        self.memory.close()

async def run_rag_query(user_query: str, conversation_id: str = None):
    """
    Run the Bedrock RAG with the given user query.
    
    Args:
        user_query: The user's question to answer
        conversation_id: Optional conversation ID for context
    
    Returns:
        The generated answer
    """
    # Check for AWS credentials
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        print("\nERROR: AWS credentials not found in .env file.")
        return None
    
    # Initialize the agent with Bedrock Claude
    agent = BedrockRAGAgent(conversation_id=conversation_id)
    
    try:
        # Generate answer
        print(f"Generating answer for question: {user_query[:50]}...")
        result = await agent.answer_question(user_query)
        
        # Display result
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages:
            print("\n==== ANSWER ====\n")
            print(ai_messages[-1].content)
            
        return result
        
    finally:
        # Clean up
        await agent.close()

async def main():
    """Example of using the run_rag_query function."""
    # Example user query
    user_query = """
    What is the tmap?
    """
    
    # Create a conversation ID
    conversation_id = "demo_session_" + str(uuid.uuid4())[:8]
    
    # Generate answer
    result = await run_rag_query(user_query, conversation_id)
    if result:
        print("\nQuery answered successfully!")

if __name__ == "__main__":
    asyncio.run(main())
