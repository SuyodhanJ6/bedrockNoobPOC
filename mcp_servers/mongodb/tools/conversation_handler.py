"""
Conversation Handler - Implements MCP tool for retrieving conversation history
"""

import logging
from typing import List, Dict, Any, Optional

from core.mongodb_client import MongoDBClient
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

class ConversationHandler:
    """Handler for conversation history operations using MongoDB"""
    
    def __init__(self):
        """Initialize the conversation handler with MongoDB client"""
        logger.info("Initializing ConversationHandler")
        self.mongodb_client = MongoDBClient.from_config()
    
    def get_conversation_history(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None,
        exclude_current: bool = True
    ) -> Dict[str, Any]:
        """
        Get conversation history for a specific conversation ID.
        
        Args:
            conversation_id: The conversation ID to retrieve
            limit: Optional limit of messages to retrieve
            exclude_current: Whether to exclude the most recent user message
            
        Returns:
            Dictionary containing conversation history and metadata
        """
        try:
            # Ensure conversation_id is a string and log the actual value
            conv_id = str(conversation_id)
            logger.info(f"Retrieving conversation history for ID: {conv_id}")
            logger.info(f"Exclude current message: {exclude_current}")
            
            # Get raw messages from MongoDB
            messages = self.mongodb_client.get_conversation_history(
                conversation_id=conv_id,
                limit=limit or Config.MAX_HISTORY_LENGTH,
                exclude_current=exclude_current
            )
            
            # Format messages for response
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", "").isoformat() 
                    if hasattr(msg.get("timestamp", ""), "isoformat") else msg.get("timestamp", "")
                })
            
            logger.info(f"Found {len(formatted_messages)} messages for conversation {conv_id}")
            
            # Return formatted response
            return {
                "conversation_id": conv_id,
                "messages": formatted_messages,
                "message_count": len(formatted_messages)
            }
        
        except Exception as e:
            error_msg = f"Error retrieving conversation history: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return {
                "conversation_id": conversation_id,
                "messages": [],
                "message_count": 0,
                "error": error_msg
            }
    
    def close(self):
        """Close connections"""
        if self.mongodb_client:
            self.mongodb_client.close()
    
    @classmethod
    def create_default(cls) -> "ConversationHandler":
        """
        Create a ConversationHandler with default config settings
        
        Returns:
            Configured ConversationHandler instance
        """
        return cls() 