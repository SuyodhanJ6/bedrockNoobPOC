FROM python:3.11-slim

WORKDIR /app

# Install dependencies for MongoDB
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    pip install --no-cache-dir ".[dev]"

# Create directories if they don't exist
RUN mkdir -p /app/config /app/core /app/tools

# Copy application files
COPY config/ /app/config/
COPY core/ /app/core/
COPY tools/ /app/tools/
COPY mongodb_mcp_server.py /app/

# Make the script executable
RUN chmod +x /app/mongodb_mcp_server.py

# Expose the port the app runs on
EXPOSE 3004

# Command to run the application
CMD ["python", "mongodb_mcp_server.py"] 