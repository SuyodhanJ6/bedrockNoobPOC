"""
Repository for managing conversation data in MongoDB
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from memory.mongodb.mongo_client import MongoMemoryClient

# Set up logging
logger = logging.getLogger(__name__)

class ConversationRepository:
    """Repository for CRUD operations on conversation data"""
    
    def __init__(
        self, 
        mongo_client: MongoMemoryClient,
        collection_name: str = "conversations"
    ):
        """
        Initialize conversation repository
        
        Args:
            mongo_client: MongoDB client
            collection_name: Collection name for conversation data
        """
        self.mongo_client = mongo_client
        self.collection_name = collection_name
        self.collection = self.mongo_client.get_collection(collection_name)
    
    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        """
        Add a message to the conversation history
        
        Args:
            conversation_id: Unique conversation identifier
            role: Message role (user/assistant/system)
            content: Message content
            
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB collection not available")
            return False
        
        try:
            # Ensure all required fields are present
            message = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            result = self.collection.insert_one(message)
            logger.debug(f"Added message to conversation {conversation_id}: {result.inserted_id}")
            return True
            
        except PyMongoError as e:
            logger.error(f"Error adding message to MongoDB: {str(e)}")
            return False
    
    def get_conversation_history(
        self, 
        conversation_id: str,
        limit: Optional[int] = None,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific conversation ID
        
        Args:
            conversation_id: Unique conversation identifier
            limit: Maximum number of messages to return
            skip: Number of messages to skip
            
        Returns:
            List of message dictionaries sorted by timestamp
        """
        if self.collection is None:
            logger.error("MongoDB collection not available")
            return []
            
        try:
            # Build query
            query = {"conversation_id": conversation_id}
            
            # Create cursor with sorting
            cursor = self.collection.find(
                query,
                {"_id": 0}
            ).sort("timestamp", 1)
            
            # Apply skip and limit if provided
            if skip > 0:
                cursor = cursor.skip(skip)
            
            if limit is not None:
                cursor = cursor.limit(limit)
            
            # Convert cursor to list
            messages = list(cursor)
            
            # Validate that all messages have required fields
            validated_messages = []
            for msg in messages:
                # Handle legacy messages with 'type' instead of 'role'
                if "type" in msg and "role" not in msg:
                    # Map 'type' to 'role' (human->user, ai->assistant)
                    msg_type = msg["type"]
                    if msg_type == "human":
                        msg["role"] = "user"
                    elif msg_type == "ai":
                        msg["role"] = "assistant"
                    elif msg_type == "system":
                        msg["role"] = "system"
                    else:
                        msg["role"] = msg_type  # Keep as is for unknown types
                    
                    logger.info(f"Mapped message type '{msg_type}' to role '{msg['role']}'")
                
                # Add defaults for missing fields
                if "role" not in msg:
                    msg["role"] = "user"  # Default role
                    logger.warning(f"Message missing role field: {msg}")
                if "content" not in msg:
                    msg["content"] = ""  # Default empty content
                    logger.warning(f"Message missing content field: {msg}")
                
                validated_messages.append(msg)
            
            logger.debug(f"Retrieved {len(validated_messages)} messages for conversation {conversation_id}")
            return validated_messages
            
        except PyMongoError as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Delete all messages for a specific conversation
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB collection not available")
            return False
            
        try:
            # Delete all messages with the given conversation ID
            result = self.collection.delete_many({"conversation_id": conversation_id})
            logger.info(f"Deleted {result.deleted_count} messages for conversation {conversation_id}")
            return True
            
        except PyMongoError as e:
            logger.error(f"Error clearing conversation history: {str(e)}")
            return False
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent conversations with their latest message
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries with latest message
        """
        if self.collection is None:
            logger.error("MongoDB collection not available")
            return []
            
        try:
            # Aggregate pipeline to get the latest message for each conversation
            pipeline = [
                # Group by conversation_id, keeping the document with the latest timestamp
                {"$sort": {"timestamp": -1}},
                {"$group": {
                    "_id": "$conversation_id",
                    "latest_message": {"$first": "$$ROOT"},
                    "message_count": {"$sum": 1}
                }},
                # Sort by latest message timestamp
                {"$sort": {"latest_message.timestamp": -1}},
                # Limit results
                {"$limit": limit},
                # Project the fields we want
                {"$project": {
                    "_id": 0,
                    "conversation_id": "$_id",
                    "latest_message": "$latest_message",
                    "message_count": "$message_count"
                }}
            ]
            
            conversations = list(self.collection.aggregate(pipeline))
            logger.debug(f"Retrieved {len(conversations)} recent conversations")
            return conversations
            
        except PyMongoError as e:
            logger.error(f"Error retrieving recent conversations: {str(e)}")
            return []
            
    def search_conversations(self, search_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search conversations for specific text
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        if self.collection is None:
            logger.error("MongoDB collection not available")
            return []
            
        try:
            # Create text search query
            # Note: This requires a text index on the content field
            result = self.collection.find(
                {"$text": {"$search": search_text}},
                {"score": {"$meta": "textScore"}, "_id": 0}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            messages = list(result)
            logger.debug(f"Found {len(messages)} messages matching '{search_text}'")
            return messages
            
        except PyMongoError as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []
    
    def close(self) -> None:
        """Close the MongoDB connection"""
        if self.mongo_client:
            try:
                self.mongo_client.disconnect()
                logger.info("Closed MongoDB connection")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {str(e)}")
    
    @classmethod
    def from_env(cls) -> "ConversationRepository":
        """
        Create repository instance from environment variables
        
        Returns:
            Configured repository instance
        """
        # Create MongoDB client from environment
        mongo_client = MongoMemoryClient.from_env()
        
        # Get collection name from environment or use default
        collection_name = os.environ.get("MONGODB_COLLECTION", "conversations")
        
        return cls(mongo_client, collection_name) 