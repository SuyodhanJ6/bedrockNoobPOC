"""
Bedrock RAG Handler - Implements document retrieval using the core client and retriever
"""

import os
import logging
from typing import List, Dict, Any, Optional

# Import the core client and retriever
from core.bedrock_retriever_client import BedrockRetrieverClient
from retriever.knowledge_base_retriever import KnowledgeBaseRetriever
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

class BedrockRagHandler:
    """Handler for Bedrock retrieval operations using specialized retriever"""
    
    def __init__(
        self,
        knowledge_base_id: Optional[str] = None,
        region_name: Optional[str] = None,
        top_n: Optional[int] = None,
        use_reranking: Optional[bool] = None
    ):
        """Initialize the Bedrock RAG handler
        
        Args:
            knowledge_base_id: Knowledge Base ID (defaults to Config.KNOWLEDGE_BASE_ID)
            region_name: AWS region name (defaults to Config.AWS_REGION)
            top_n: Number of documents to return after reranking (default from config)
            use_reranking: Whether to use reranking (default from config)
        """
        # Initialize the core client
        logger.info("Initializing BedrockRetrieverClient from config")
        
        # If any custom parameters provided, update the config and create client directly
        if knowledge_base_id or region_name or top_n is not None or use_reranking is not None:
            # Override config settings with provided parameters
            kb_id = knowledge_base_id or Config.KNOWLEDGE_BASE_ID
            region = region_name or Config.AWS_REGION
            n = top_n if top_n is not None else Config.TOP_N_RESULTS
            rerank = use_reranking if use_reranking is not None else Config.USE_RERANKING
            
            # Create client with custom parameters
            self.retriever_client = BedrockRetrieverClient(
                knowledge_base_id=kb_id,
                region_name=region,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                aws_session_token=Config.AWS_SESSION_TOKEN if Config.AWS_SESSION_TOKEN else None,
                top_n=n,
                initial_results=Config.INITIAL_RESULTS,
                use_reranking=rerank,
                rerank_model_id=Config.RERANK_MODEL_ID
            )
        else:
            # Use default config
            self.retriever_client = BedrockRetrieverClient.from_config()
        
        # Initialize the specialized retriever with the client
        logger.info("Initializing KnowledgeBaseRetriever")
        self.retriever = KnowledgeBaseRetriever(self.retriever_client)
    
    def perform_rag_query(
        self, 
        query: str, 
        context: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform document retrieval for a query using the specialized retriever.
        
        Args:
            query: The user query
            context: Optional context (ignored in this implementation)
            max_tokens: Not used in this implementation
            
        Returns:
            Dict containing retrieved documents and metadata
        """
        try:
            logger.info(f"Performing retrieval for query: {query[:50]}...")
            # Use the specialized retriever to perform the query
            result = self.retriever.retrieve(query)
            
            # Format the response according to MCP server expectations
            response = {
                "response": "",  # No response text, only sources
                "sources": result.get("sources", []),
                "query": query,
                "document_count": result.get("document_count", 0)
            }
            
            logger.info(f"Retrieved {response['document_count']} documents")
            return response
            
        except Exception as e:
            error_msg = f"Error retrieving documents: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return {
                "error": error_msg,
                "response": "",
                "sources": [],
                "query": query,
                "document_count": 0
            }
    
    @classmethod
    def create_default(cls) -> "BedrockRagHandler":
        """
        Create a BedrockRagHandler with default config settings
        
        Returns:
            Configured BedrockRagHandler instance
        """
        return cls() 