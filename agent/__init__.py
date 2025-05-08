"""
Bedrock RAG Agent Package
"""

# Import the BedrockRAGAgent class to make it available when importing the package
from agent.agent import BedrockRAGAgent, run_rag_query

# Export the main classes and functions
__all__ = ["BedrockRAGAgent", "run_rag_query"]