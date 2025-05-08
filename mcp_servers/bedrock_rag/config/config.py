"""
Configuration module for Bedrock RAG service.
Loads all settings from environment variables with sensible defaults.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Bedrock RAG service"""
    
    # Server settings
    SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.environ.get("BEDROCK_RAG_PORT", "3003"))
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    
    # AWS Bedrock settings
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    
    # Knowledge Base settings
    KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "")
    
    # Reranking settings
    USE_RERANKING = os.environ.get("USE_RERANKING", "True").lower() == "true"
    RERANK_MODEL_ID = os.environ.get("RERANK_MODEL_ID", "amazon.rerank-v1:0")
    INITIAL_RESULTS = int(os.environ.get("INITIAL_RESULTS", "5"))
    TOP_N_RESULTS = int(os.environ.get("TOP_N_RESULTS", "3"))
    
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
        credentials = {
            "region_name": cls.AWS_REGION,
            "aws_access_key_id": cls.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": cls.AWS_SECRET_ACCESS_KEY
        }
        
        return credentials
    
    @classmethod
    def get_retriever_config(cls) -> Dict[str, Any]:
        """Return retriever configuration settings"""
        return {
            "knowledge_base_id": cls.KNOWLEDGE_BASE_ID,
            "region_name": cls.AWS_REGION,
            "use_reranking": cls.USE_RERANKING,
            "rerank_model_id": cls.RERANK_MODEL_ID,
            "initial_results": cls.INITIAL_RESULTS,
            "top_n": cls.TOP_N_RESULTS
        }
    
    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        """Return RAG configuration settings (legacy method)"""
        return cls.get_retriever_config()
        
    @staticmethod
    def setup_logging() -> None:
        """Configure logging based on LOG_LEVEL"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ) 