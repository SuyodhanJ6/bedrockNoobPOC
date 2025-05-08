"""
Memory adapter for integrating MongoDB-based conversation history with the agent
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from memory.mongodb.conversation_repository import ConversationRepository
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

class MongoDBMemoryAdapter:
    """Adapter for MongoDB-based conversation history that integrates with the agent"""
    
    def __init__(
        self,
        conversation_id: str,
        repository: Optional[ConversationRepository] = None,
        max_history_length: int = 10
    ):
        """
        Initialize MongoDB memory adapter
        
        Args:
            conversation_id: Unique conversation identifier
            repository: Optional repository instance (created from env if not provided)
            max_history_length: Maximum number of messages to include in context
        """
        self.conversation_id = conversation_id
        self.repository = repository or ConversationRepository.from_env()
        self.max_history_length = max_history_length
        self.fallback_memory = []
        
        logger.info(f"Initialized MongoDB memory adapter for conversation {conversation_id}")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to conversation history
        
        Args:
            role: Message role (user/assistant/system)
            content: Message content
        """
        # Try to add to MongoDB first
        success = self.repository.add_message(
            self.conversation_id, 
            role, 
            content
        )
        
        # If MongoDB fails, add to fallback memory
        if not success:
            logger.warning("Using fallback in-memory storage")
            self.fallback_memory.append({
                "conversation_id": self.conversation_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            })
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get conversation history with limit applied
        
        Returns:
            List of message dictionaries sorted by timestamp
        """
        # Try to get from MongoDB
        messages = self.repository.get_conversation_history(
            self.conversation_id,
            limit=self.max_history_length
        )
        
        # Fall back to in-memory if needed
        if not messages and self.fallback_memory:
            logger.warning("Using fallback in-memory history")
            messages = sorted(
                self.fallback_memory,
                key=lambda msg: msg["timestamp"]
            )
            
            # Apply limit
            if len(messages) > self.max_history_length:
                messages = messages[-self.max_history_length:]
        
        return messages
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        # Clear from MongoDB
        self.repository.clear_conversation(self.conversation_id)
        
        # Also clear fallback memory
        self.fallback_memory = []
        logger.info(f"Cleared conversation history for {self.conversation_id}")
    
    def format_for_llm(self) -> List[Dict[str, str]]:
        """
        Format conversation history for LLM input
        
        Returns:
            List of message dictionaries with role and content
        """
        history = self.get_conversation_history()
        formatted = []
        
        for msg in history:
            # Check if role exists, use default if missing
            role = msg.get("role", "user")  # Default to user if role is missing
            formatted.append({
                "role": role,
                "content": msg.get("content", "")  # Also handle potential missing content
            })
        
        logger.debug(f"Formatted {len(formatted)} messages for LLM input")
        return formatted
    
    def search(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search conversation history for specific text
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        return self.repository.search_conversations(query_text, limit)
    
    def get_all_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get list of all recent conversations
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of conversation summaries
        """
        return self.repository.get_recent_conversations(limit)
    
    def close(self) -> None:
        """Close MongoDB connections"""
        if self.repository and hasattr(self.repository, 'close'):
            try:
                self.repository.close()
                logger.info(f"Closed MongoDB repository for conversation {self.conversation_id}")
            except Exception as e:
                logger.error(f"Error closing MongoDB repository: {str(e)}")
    
    @classmethod
    def from_config(cls, conversation_id: str) -> "MongoDBMemoryAdapter":
        """
        Create memory adapter from application config
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Configured MongoDBMemoryAdapter
        """
        # Get memory config
        memory_config = Config.get_memory_config()
        
        # Create repository using from_env
        repository = ConversationRepository.from_env()
        
        # Get max history length from config
        max_history_length = memory_config.get("max_history_length", 10)
        
        # Create and return adapter
        return cls(
            conversation_id=conversation_id,
            repository=repository,
            max_history_length=max_history_length
        ) 