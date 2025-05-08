"""
Version 1 API routes for the Bedrock RAG Query Service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
from agent import BedrockRAGAgent
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/v1",
    tags=["v1"]
)

# Request and Response Models
class QueryRequest(BaseModel):
    """Request model for RAG query"""
    query: str = Field(..., 
        description="The user's question to answer",
        example="What are the key features of AWS Bedrock?")
    conversation_id: Optional[str] = Field(None, 
        description="Optional conversation ID for continuing a conversation",
        example="user_123_session_456")

class SourceInfo(BaseModel):
    """Model for a document source"""
    index: int = Field(..., description="Source index")
    content: str = Field(..., description="Source content")
    metadata: Dict[str, Any] = Field(..., description="Source metadata")

class MessageInfo(BaseModel):
    """Model for conversation message"""
    role: str = Field(..., description="Role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")

class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceInfo] = Field(..., description="Source documents used")
    conversation_id: str = Field(..., description="Conversation identifier")
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field("success", description="Status of the request")

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    conversation_id: str = Field(..., description="Conversation identifier")
    messages: List[MessageInfo] = Field(..., description="Conversation messages")
    message_count: int = Field(..., description="Number of messages")

# Background task to log requests
def log_request(request_data: Dict[str, Any], request_id: str):
    """Log request details for analytics"""
    logger.info(f"Request {request_id}: {request_data}")

# Dependency to get agent instance
async def get_agent(conversation_id: Optional[str] = None):
    """Get an instance of the Bedrock RAG Agent"""
    agent = BedrockRAGAgent(conversation_id=conversation_id)
    try:
        yield agent
    finally:
        # Clean up agent resources
        await agent.close()

# Dependency to get agent from request
async def get_agent_from_request(request: QueryRequest):
    """Get agent instance from request with conversation_id"""
    async for agent in get_agent(request.conversation_id):
        yield agent

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    agent: BedrockRAGAgent = Depends(get_agent_from_request)
):
    """
    Query the knowledge base using AWS Bedrock RAG.
    
    - **query**: The user's question to answer
    - **conversation_id**: Optional conversation ID for continuing a conversation
    
    Returns the answer along with source information.
    """
    request_id = str(uuid.uuid4())
    
    # Ensure conversation_id is set and valid
    if not request.conversation_id:
        request.conversation_id = str(uuid.uuid4())
        
    # Log request in background with detailed info
    background_tasks.add_task(log_request, request.dict(), request_id)
    logger.info(f"Request {request_id}: Processing query: {request.query[:50]}...")
    logger.info(f"Using conversation_id: {request.conversation_id}")
    logger.info(f"Agent conversation_id: {agent.conversation_id}")
    
    try:
        # Generate answer
        result = await agent.answer_question(request.query)
        
        # Extract answer from result
        ai_messages = [msg.content for msg in result["messages"] 
                    if hasattr(msg, 'type') and msg.type == 'ai']
        
        if not ai_messages:
            raise HTTPException(status_code=500, detail="Failed to generate an answer")
        
        answer = ai_messages[-1]
        
        # Extract source documents (this would come from the actual implementation)
        # In a real scenario, these would be retrieved from the RAG result
        # For now, we'll use a placeholder
        sources = [
            SourceInfo(
                index=1,
                content="Sample source content 1",
                metadata={"source": "knowledge_base", "relevance_score": 0.95}
            )
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            conversation_id=agent.conversation_id,
            request_id=request_id,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Request {request_id}: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    agent: BedrockRAGAgent = Depends(get_agent)
):
    """
    Get the conversation history for a specific conversation ID.
    
    - **conversation_id**: The ID of the conversation to retrieve
    
    Returns the conversation history as a list of messages.
    """
    try:
        logger.info(f"Retrieving conversation history for: {conversation_id}")
        
        # Get the conversation history from the agent
        history = agent.get_conversation_history()
        
        # Convert datetime objects to strings for response
        messages = []
        for msg in history:
            messages.append(MessageInfo(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"].isoformat()
            ))
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            message_count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation history: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    agent: BedrockRAGAgent = Depends(get_agent)
):
    """
    Clear the conversation history for a specific conversation ID.
    
    - **conversation_id**: The ID of the conversation to clear
    
    Returns a success message.
    """
    try:
        logger.info(f"Clearing conversation history for: {conversation_id}")
        
        # Clear the conversation history
        agent.clear_conversation()
        
        return {"status": "success", "message": f"Conversation {conversation_id} cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for the API"""
    return {"status": "healthy", "version": "1.0.0"} 