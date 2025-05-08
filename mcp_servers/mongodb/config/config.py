"""
Configuration module for MongoDB MCP service.
Loads all settings from environment variables with sensible defaults from constants.
"""

import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

# Import constants
from config.constants import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_DEBUG,
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
    DEFAULT_COLLECTION_NAME,
    DEFAULT_MAX_HISTORY_LENGTH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_FORMAT
)

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the MongoDB MCP service"""
    
    # Server settings
    SERVER_HOST = os.environ.get("SERVER_HOST", DEFAULT_SERVER_HOST)
    SERVER_PORT = int(os.environ.get("MONGODB_MCP_PORT", DEFAULT_SERVER_PORT))
    DEBUG = os.environ.get("DEBUG", str(DEFAULT_DEBUG)).lower() == "true"
    
    # MongoDB settings
    MONGODB_URI = os.environ.get("MONGODB_URI", DEFAULT_MONGODB_URI)
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", DEFAULT_DB_NAME)
    MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", DEFAULT_COLLECTION_NAME)
    MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", DEFAULT_MAX_HISTORY_LENGTH))
    
    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", DEFAULT_LOG_LEVEL)
    
    @classmethod
    def validate_mongodb_uri(cls) -> bool:
        """
        Validate the MongoDB URI format.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Parse the URI to validate format
            parsed_uri = urlparse(cls.MONGODB_URI)
            
            # Check for minimum valid URI components
            if not parsed_uri.scheme or parsed_uri.scheme not in ["mongodb", "mongodb+srv"]:
                logging.warning(f"Invalid MongoDB URI scheme: {parsed_uri.scheme}")
                return False
                
            # Additional validation could be added here
            return True
            
        except Exception as e:
            logging.error(f"Error validating MongoDB URI: {str(e)}")
            return False
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return all configuration values as a dictionary"""
        return {k: v for k, v in cls.__dict__.items() 
                if not k.startswith('__') and not callable(getattr(cls, k))}
    
    @classmethod
    def get_mongodb_config(cls) -> Dict[str, Any]:
        """Return MongoDB configuration settings"""
        # Validate the URI before returning
        if not cls.validate_mongodb_uri():
            logging.warning(f"Using MongoDB URI: {cls.MONGODB_URI} (validation failed)")
        else:
            logging.info(f"Using MongoDB URI: {cls.MONGODB_URI}")
            
        return {
            "mongodb_uri": cls.MONGODB_URI,
            "mongodb_db_name": cls.MONGODB_DB_NAME,
            "mongodb_collection": cls.MONGODB_COLLECTION,
            "max_history_length": cls.MAX_HISTORY_LENGTH
        }
        
    @staticmethod
    def setup_logging() -> None:
        """Configure logging based on LOG_LEVEL"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=DEFAULT_LOG_FORMAT
        ) 