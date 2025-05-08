"""
Memory module for the Bedrock RAG Agent
"""

from memory.short_term_memory import ShortTermMemory

# Try to import MongoDB components
try:
    from memory.mongodb import MongoMemoryClient, ConversationRepository
    __all__ = ["ShortTermMemory", "MongoMemoryClient", "ConversationRepository"]
except ImportError:
    __all__ = ["ShortTermMemory"] 