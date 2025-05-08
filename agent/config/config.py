"""
Configuration module for Bedrock RAG Agent.
Loads all settings from environment variables with sensible defaults.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Bedrock RAG Agent"""
    
    # API settings
    API_HOST = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT = int(os.environ.get("API_PORT", "8000"))
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    
    # AWS Bedrock settings
    AWS_REGION = os.environ.get("AWS_REGION", "ca-central-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    
    # Bedrock Model settings
    BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
    TEMPERATURE = float(os.environ.get("TEMPERATURE", "0"))
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "3000"))
    TOP_P = float(os.environ.get("TOP_P", "0.9"))
    
    # MCP Server settings
    BEDROCK_RAG_MCP_HOST = os.environ.get("BEDROCK_RAG_MCP_HOST", "bedrock-rag-mcp")
    BEDROCK_RAG_MCP_PORT = os.environ.get("BEDROCK_RAG_MCP_PORT", "3003")
    MONGODB_MCP_HOST = os.environ.get("MONGODB_MCP_HOST", "mongodb-mcp")
    MONGODB_MCP_PORT = os.environ.get("MONGODB_MCP_PORT", "3004")
    
    # Memory settings
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "bedrock_rag")
    MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "conversations")
    MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", "10"))
    
    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return all configuration values as a dictionary"""
        return {k: v for k, v in cls.__dict__.items() 
                if not k.startswith('__') and not callable(getattr(cls, k))}
    
    @classmethod
    def get_aws_credentials(cls) -> Dict[str, str]:
        """Return AWS credentials as a dictionary"""
        return {
            "region_name": cls.AWS_REGION,
            "aws_access_key_id": cls.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": cls.AWS_SECRET_ACCESS_KEY
        }
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Return Bedrock model configuration settings"""
        return {
            "model_id": cls.BEDROCK_MODEL_ID,
            "model_kwargs": {
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS,
                "top_p": cls.TOP_P
            }
        }
    
    @classmethod
    def get_mcp_config(cls) -> Dict[str, str]:
        """Return MCP server configuration settings"""
        return {
            "bedrock_rag_host": cls.BEDROCK_RAG_MCP_HOST,
            "bedrock_rag_port": cls.BEDROCK_RAG_MCP_PORT,
            "mongodb_host": cls.MONGODB_MCP_HOST,
            "mongodb_port": cls.MONGODB_MCP_PORT
        }
    
    @classmethod
    def get_memory_config(cls) -> Dict[str, Any]:
        """Return memory configuration settings"""
        return {
            "mongodb_uri": cls.MONGODB_URI,
            "db_name": cls.MONGODB_DB_NAME,
            "collection_name": cls.MONGODB_COLLECTION,
            "max_history_length": cls.MAX_HISTORY_LENGTH
        }
    
    @staticmethod
    def setup_logging() -> None:
        """Configure logging based on LOG_LEVEL"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ) 