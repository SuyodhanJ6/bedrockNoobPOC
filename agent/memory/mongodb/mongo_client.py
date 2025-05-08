"""
MongoDB client wrapper for Bedrock RAG Agent's short-term memory
"""

import os
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Set up logging
logger = logging.getLogger(__name__)

class MongoMemoryClient:
    """MongoDB client wrapper with connection management and error handling"""
    
    def __init__(
        self, 
        uri: str,
        db_name: str,
        connection_timeout_ms: int = 5000
    ):
        """
        Initialize MongoDB client with connection parameters
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
            connection_timeout_ms: Connection timeout in milliseconds
        """
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connection_timeout_ms = connection_timeout_ms
        self.is_connected = False
        
        # Try to establish connection on initialization
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish MongoDB connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Configure connection with timeout
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.connection_timeout_ms
            )
            
            # Test connection by executing a command
            self.client.admin.command('ping')
            
            # Get database reference
            self.db = self.client[self.db_name]
            
            self.is_connected = True
            logger.info(f"Connected to MongoDB database: {self.db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.is_connected = False
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Get a MongoDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection or None if not connected
        """
        if not self.is_connected:
            if not self._connect():
                logger.error(f"Not connected to MongoDB. Cannot get collection: {collection_name}")
                return None
        
        return self.db[collection_name]
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {str(e)}")
            finally:
                self.client = None
                self.db = None
                self.is_connected = False
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to MongoDB
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.disconnect()
        return self._connect()
    
    @classmethod
    def from_env(cls) -> "MongoMemoryClient":
        """
        Create MongoMemoryClient from environment variables
        
        Environment variables:
            MONGODB_URI: MongoDB connection URI
            MONGODB_DB_NAME: Database name
            MONGODB_CONNECTION_TIMEOUT_MS: Connection timeout in milliseconds
        
        Returns:
            Configured MongoMemoryClient instance
        """
        uri = os.environ.get("MONGODB_URI", "")
        db_name = os.environ.get("MONGODB_DB_NAME", "bedrock_rag")
        timeout_ms = int(os.environ.get("MONGODB_CONNECTION_TIMEOUT_MS", "5000"))
        
        if not uri:
            logger.error("MONGODB_URI environment variable not set")
            raise ValueError("MONGODB_URI environment variable must be set")
        
        return cls(uri, db_name, timeout_ms) 