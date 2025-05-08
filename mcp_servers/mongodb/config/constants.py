"""
Constants module for MongoDB MCP service.
Defines all hardcoded values and defaults in one place.
"""

# Server defaults
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 3004
DEFAULT_DEBUG = False

# MongoDB defaults
DEFAULT_MONGODB_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "bedrock_rag"
DEFAULT_COLLECTION_NAME = "conversations"
DEFAULT_MAX_HISTORY_LENGTH = 10
DEFAULT_CONNECTION_TIMEOUT_MS = 5000

# Logging defaults
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 