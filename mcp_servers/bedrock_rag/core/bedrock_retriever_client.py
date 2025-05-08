"""
Bedrock Retriever Client - Core module for AWS Bedrock document retrieval
"""

import boto3
import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import SecretStr

# Import LangChain components
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from langchain_aws.document_compressors.rerank import BedrockRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import Document

# Import Config
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

class BedrockRetrieverClient:
    """Client for AWS Bedrock retrieval operations"""
    
    def __init__(
        self,
        knowledge_base_id: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        top_n: int = 3,
        initial_results: int = 5,
        use_reranking: bool = True,
        rerank_model_id: Optional[str] = None
    ):
        """
        Initialize the Bedrock Retriever client
        
        Args:
            knowledge_base_id: Knowledge Base ID to query
            region_name: AWS region name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            top_n: Number of documents to return after reranking
            initial_results: Number of initial results to retrieve before reranking
            use_reranking: Whether to use reranking (if False, just return initial results)
            rerank_model_id: The model ID to use for reranking
        """
        self.knowledge_base_id = knowledge_base_id
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.top_n = top_n
        self.initial_results = initial_results
        self.use_reranking = use_reranking
        self.rerank_model_id = rerank_model_id or Config.RERANK_MODEL_ID
        
        # Initialize AWS session
        session_kwargs = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": region_name
        }
            
        self.session = boto3.Session(**session_kwargs)
        
        # Create the base retriever for Knowledge Base
        logger.info(f"Initializing Knowledge Base retriever for KB ID: {knowledge_base_id}")
        retriever_kwargs = {
            "knowledge_base_id": knowledge_base_id,
            "region_name": region_name,
            "aws_access_key_id": SecretStr(aws_access_key_id),
            "aws_secret_access_key": SecretStr(aws_secret_access_key),
            "retrieval_config": {
                "vectorSearchConfiguration": {
                    "numberOfResults": initial_results
                }
            }
        }
            
        self.base_retriever = AmazonKnowledgeBasesRetriever(**retriever_kwargs)
        
        # Create the retriever (with or without reranking)
        if use_reranking:
            logger.info(f"Using reranking with model ID: {self.rerank_model_id}")
            # Create Bedrock Reranker
            reranker_kwargs = {
                "model_arn": f"arn:aws:bedrock:{region_name}::foundation-model/{self.rerank_model_id}",
                "region_name": region_name,
                "aws_access_key_id": SecretStr(aws_access_key_id),
                "aws_secret_access_key": SecretStr(aws_secret_access_key),
                "top_n": top_n
            }
                
            self.reranker = BedrockRerank(**reranker_kwargs)
            
            # Create the reranking retriever
            self.retriever = ContextualCompressionRetriever(
                base_compressor=self.reranker,
                base_retriever=self.base_retriever
            )
            logger.info(f"Initialized reranking retriever with top_n={top_n}")
        else:
            # Use base retriever without reranking
            self.retriever = self.base_retriever
            logger.info("Using base retriever without reranking")
    
    def retrieve_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents from the knowledge base for a given query
        
        Args:
            query: The search query
            
        Returns:
            List of Document objects with content and metadata
        """
        logger.info(f"Retrieving documents for query: {query[:50]}...")
        try:
            documents = self.retriever.get_relevant_documents(query)
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def format_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Format retrieved documents into a standardized format
        
        Args:
            documents: List of Document objects from LangChain
            
        Returns:
            List of dictionaries with formatted document information
        """
        sources = []
        for i, doc in enumerate(documents):
            source_info = {
                "index": i + 1,
                "content": doc.page_content,
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
            }
            sources.append(source_info)
        
        logger.debug(f"Formatted {len(sources)} document sources")
        return sources
    
    @classmethod
    def from_config(cls) -> "BedrockRetrieverClient":
        """
        Create a BedrockRetrieverClient instance from Config settings
        
        Returns:
            Configured BedrockRetrieverClient instance
        """
        aws_creds = Config.get_aws_credentials()
        retriever_config = Config.get_retriever_config()
        
        return cls(
            knowledge_base_id=retriever_config["knowledge_base_id"],
            region_name=aws_creds["region_name"],
            aws_access_key_id=aws_creds["aws_access_key_id"],
            aws_secret_access_key=aws_creds["aws_secret_access_key"],
            top_n=retriever_config["top_n"],
            initial_results=retriever_config["initial_results"],
            use_reranking=retriever_config["use_reranking"],
            rerank_model_id=retriever_config["rerank_model_id"]
        ) 