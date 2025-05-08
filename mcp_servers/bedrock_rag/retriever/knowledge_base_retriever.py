"""
Knowledge Base Retriever - Specialized retriever for AWS Bedrock Knowledge Base
"""

import logging
from typing import Dict, Any, List, Optional
from langchain.schema import Document

# Import core client
from core.bedrock_retriever_client import BedrockRetrieverClient

# Set up logging
logger = logging.getLogger(__name__)

class KnowledgeBaseRetriever:
    """
    Specialized retriever for AWS Bedrock Knowledge Base with enhanced functionality
    """
    
    def __init__(self, client: BedrockRetrieverClient):
        """
        Initialize with a BedrockRetrieverClient
        
        Args:
            client: The core Bedrock retriever client
        """
        self.client = client
        logger.info(f"Initialized KnowledgeBaseRetriever with client for KB: {client.knowledge_base_id}")
        
    def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Retrieve documents for a query and format results
        
        Args:
            query: The search query
            
        Returns:
            Dict containing query results and metadata
        """
        try:
            logger.info(f"Starting retrieval for query: '{query[:50]}...'")
            # Get documents from the client
            documents = self.client.retrieve_documents(query)
            logger.info(f"Retrieved {len(documents)} raw documents")
            
            # Format the documents
            sources = self.client.format_documents(documents)
            
            # Return formatted results
            result = {
                "sources": sources,
                "query": query,
                "document_count": len(sources),
                "status": "success"
            }
            logger.info(f"Completed retrieval with {len(sources)} formatted sources")
            return result
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error in retrieval: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return {
                "sources": [],
                "query": query,
                "document_count": 0,
                "status": "error",
                "error": error_msg
            }
    
    def get_metadata_fields(self, sources: List[Dict[str, Any]]) -> List[str]:
        """
        Extract all metadata field names from sources
        
        Args:
            sources: List of source documents
            
        Returns:
            List of unique metadata field names
        """
        fields = set()
        for source in sources:
            if "metadata" in source and isinstance(source["metadata"], dict):
                fields.update(source["metadata"].keys())
        
        result = sorted(list(fields))
        logger.debug(f"Extracted {len(result)} unique metadata fields: {result}")
        return result
    
    def filter_by_metadata(
        self, 
        sources: List[Dict[str, Any]], 
        field: str, 
        value: Any
    ) -> List[Dict[str, Any]]:
        """
        Filter sources by a metadata field value
        
        Args:
            sources: List of source documents
            field: Metadata field name to filter on
            value: Value to filter for
            
        Returns:
            Filtered list of sources
        """
        logger.info(f"Filtering {len(sources)} sources by metadata: {field}={value}")
        
        filtered = [
            source for source in sources
            if "metadata" in source 
            and field in source["metadata"] 
            and source["metadata"][field] == value
        ]
        
        logger.info(f"Filtered from {len(sources)} to {len(filtered)} sources")
        return filtered 