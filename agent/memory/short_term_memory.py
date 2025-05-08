"""
Short-Term Memory - Conversation history storage for Bedrock RAG Agent with MongoDB support
"""

import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ShortTermMemory:
    """Memory system for conversation history with MongoDB support"""
    
    def __init__(
        self, 
        conversation_id: str,
        config: Optional[Dict[str, Any]] = None,
        max_history_length: int = 10
    ):
        """Initialize the short-term memory with configuration.
        
        Args:
            conversation_id: Unique identifier for the conversation
            config: Configuration dictionary with memory settings
            max_history_length: Maximum number of messages to keep in context
        """
        self.conversation_id = conversation_id
        self.max_history_length = max_history_length
        self.config = config or {}
        self.conversation_history = []
        self.memory_adapter = None
        
        # Try to use MongoDB if available
        try:
            from memory.mongodb.memory_adapter import MongoDBMemoryAdapter
            mongo_uri = self.config.get("mongodb_uri", os.environ.get("MONGODB_URI", ""))
            
            if mongo_uri:
                # Create MongoDB adapter if URI is available
                self.memory_adapter = MongoDBMemoryAdapter(
                    conversation_id=conversation_id,
                    max_history_length=max_history_length
                )
                logger.info(f"Using MongoDB for conversation history: {conversation_id}")
            else:
                logger.warning("No MongoDB URI provided. Using in-memory storage.")
        except ImportError:
            logger.warning("MongoDB adapter not available. Using in-memory storage.")
        
        logger.info(f"Initialized short-term memory for conversation ID: {conversation_id}")
        
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: Message role (user/assistant/system)
            content: The message content
        """
        if self.memory_adapter:
            # Use MongoDB adapter if available
            self.memory_adapter.add_message(role, content)
        else:
            # Fall back to in-memory storage
            message = {
                "conversation_id": self.conversation_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            self.conversation_history.append(message)
            logger.debug(f"Added {role} message to in-memory history")
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retrieve the conversation history.
        
        Returns:
            List of message dictionaries sorted by timestamp
        """
        if self.memory_adapter:
            # Use MongoDB adapter if available
            return self.memory_adapter.get_conversation_history()
        else:
            # Return in-memory history with limit
            history = self.conversation_history[-self.max_history_length:] if self.conversation_history else []
            logger.debug(f"Retrieved {len(history)} messages from in-memory history")
            return history
    
    def clear_conversation(self) -> None:
        """Clear the conversation history for this conversation ID."""
        if self.memory_adapter:
            # Use MongoDB adapter if available
            self.memory_adapter.clear_conversation()
        else:
            # Clear in-memory history
            self.conversation_history = []
            logger.info("Cleared in-memory conversation history")
    
    def format_for_llm(self) -> List[Dict[str, str]]:
        """Format conversation history for use with LLMs.
        
        Returns:
            List of message dictionaries with role and content keys
        """
        if self.memory_adapter:
            # Use MongoDB adapter's formatting
            return self.memory_adapter.format_for_llm()
        else:
            # Format in-memory history
            formatted = []
            
            # Use just the last few messages based on max_history_length
            history = self.get_conversation_history()
            
            for msg in history:
                formatted.append({
                    "role": msg.get("role", "user"),  # Default to user if missing
                    "content": msg.get("content", "")  # Default to empty if missing
                })
                
            return formatted
    
    def search_messages(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for messages containing specific text.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        if self.memory_adapter and hasattr(self.memory_adapter, 'search'):
            return self.memory_adapter.search(query_text, limit)
        else:
            # Simple text search for in-memory (not efficient but works for small datasets)
            matching = [
                msg for msg in self.conversation_history 
                if query_text.lower() in msg["content"].lower()
            ][:limit]
            return matching
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get a list of recent conversations.
        
        Args:
            limit: Maximum number of conversations
            
        Returns:
            List of conversation summaries
        """
        if self.memory_adapter and hasattr(self.memory_adapter, 'get_all_conversations'):
            return self.memory_adapter.get_all_conversations(limit)
        else:
            # In-memory version can only access the current conversation
            return [{
                "conversation_id": self.conversation_id,
                "message_count": len(self.conversation_history)
            }]
    
    def close(self) -> None:
        """Close any open connections."""
        if self.memory_adapter and hasattr(self.memory_adapter, 'close'):
            try:
                self.memory_adapter.close()
                logger.info(f"Closed memory adapter for conversation {self.conversation_id}")
            except Exception as e:
                logger.error(f"Error closing memory adapter: {str(e)}")
    
    @classmethod
    def from_config(cls, conversation_id: str, config) -> "ShortTermMemory":
        """Create a ShortTermMemory instance from a config object.
        
        Args:
            conversation_id: Unique identifier for the conversation
            config: Configuration object with memory settings
            
        Returns:
            Configured ShortTermMemory instance
        """
        # Extract relevant config values
        memory_config = {
            "mongodb_uri": getattr(config, "MONGODB_URI", os.environ.get("MONGODB_URI", "")),
            "max_history_length": getattr(config, "MAX_HISTORY_LENGTH", 10)
        }
        
        # Create instance with the extracted config
        return cls(
            conversation_id=conversation_id,
            config=memory_config,
            max_history_length=memory_config["max_history_length"]
        ) 