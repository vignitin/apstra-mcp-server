# Dockerfile for Apstra MCP Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY apstra_mcp.py .
COPY apstra_core.py .
COPY session_manager.py .
COPY apstra_config_sample.json .

# Create non-root user for security
RUN groupadd -r apstra && useradd -r -g apstra apstra
RUN chown -R apstra:apstra /app
USER apstra

# Expose port for MCP server
EXPOSE 8080

# Health check for HTTP transport
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command - can be overridden  
CMD ["python3", "apstra_mcp.py", "-t", "http", "-H", "0.0.0.0", "-p", "8080"]