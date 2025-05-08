"""
MongoDB Client - Handles connections and queries to MongoDB for conversation history
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import Config
from config.constants import DEFAULT_CONNECTION_TIMEOUT_MS

# Set up logging
logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for conversation history retrieval and management"""
    
    def __init__(
        self,
        mongodb_uri: str = None,
        db_name: str = None,
        collection_name: str = None,
        max_history_length: int = None,
        connection_timeout_ms: int = DEFAULT_CONNECTION_TIMEOUT_MS
    ):
        """Initialize MongoDB client with connection parameters
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Database name
            collection_name: Collection name for conversations
            max_history_length: Maximum number of messages to retrieve
            connection_timeout_ms: Connection timeout in milliseconds
        """
        # Use parameters or config defaults
        self.mongodb_uri = mongodb_uri or Config.MONGODB_URI
        self.db_name = db_name or Config.MONGODB_DB_NAME
        self.collection_name = collection_name or Config.MONGODB_COLLECTION
        self.max_history_length = max_history_length or Config.MAX_HISTORY_LENGTH
        self.connection_timeout_ms = connection_timeout_ms
        
        # Initialize connection objects
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        
        # Connect on initialization
        self._connect()
        
    def _connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create MongoDB client with timeout
            self.client = MongoClient(
                self.mongodb_uri, 
                serverSelectionTimeoutMS=self.connection_timeout_ms
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Create indexes if they don't exist
            self.collection.create_index("conversation_id")
            self.collection.create_index("timestamp")
            
            self.is_connected = True
            logger.info(f"Connected to MongoDB at {self.mongodb_uri}, database '{self.db_name}'")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.is_connected = False
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_conversation_history(
        self, 
        conversation_id: str, 
        limit: int = None,
        exclude_current: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific conversation ID.
        
        Args:
            conversation_id: The conversation ID to retrieve
            limit: Max number of messages to return (defaults to self.max_history_length)
            exclude_current: Whether to exclude the most recent user message
            
        Returns:
            List of conversation messages with role and content
        """
        # Use parameter or instance default
        limit = limit or self.max_history_length
        
        try:
            # Check connection
            if not self.is_connected:
                if not self._connect():
                    logger.error("Failed to connect to MongoDB")
                    return []
            
            # Ensure conversation_id is properly formatted as a string
            conv_id = str(conversation_id)
            
            # Log the actual query parameters
            logger.info(f"Querying MongoDB for conversation_id: '{conv_id}', limit: {limit}, exclude_current: {exclude_current}")
            
            # Query for messages in this conversation
            messages = list(self.collection.find(
                {"conversation_id": conv_id},
                sort=[("timestamp", DESCENDING)],
                limit=limit + (2 if exclude_current else 0)  # Get extra messages if excluding current Q&A pair
            ))
            
            # If we need to exclude the current question (typically the last user message and its response)
            if exclude_current and len(messages) >= 2:
                # Check if the last message is from the user
                has_user_last = False
                for i, msg in enumerate(messages):
                    if msg.get("role") == "user":
                        has_user_last = True
                        # Remove the last user message and the assistant's response if it exists
                        messages = messages[2:]  # Skip the most recent pair
                        logger.info(f"Excluded the current question/answer pair from results")
                        break
                    if i >= 1:  # Only check the first two messages
                        break
            
            # Reverse to get chronological order (oldest first)
            messages.reverse()
            
            logger.info(f"Retrieved {len(messages)} messages for conversation {conv_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def from_config(cls) -> "MongoDBClient":
        """
        Create MongoDB client from application config.
        
        Returns:
            Configured MongoDBClient instance
        """
        # Get MongoDB config from Config class
        config = Config.get_mongodb_config()
        return cls(
            mongodb_uri=config["mongodb_uri"],
            db_name=config["mongodb_db_name"],
            collection_name=config["mongodb_collection"],
            max_history_length=config["max_history_length"]
        ) 