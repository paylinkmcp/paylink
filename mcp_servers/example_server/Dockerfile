FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first to leverage Docker cache
COPY mcp_servers/example_server/pyproject.toml .

# Install dependencies from pyproject.toml
# Note: uvicorn and starlette are likely transitive deps of mcp, but included explicitly for clarity
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "click>=8.2.1" \
        "httpx>=0.28.1" \
        "mcp[cli]>=1.13.0" \
        "python-dotenv>=1.1.1" \
        "motor>=3.6.0" \
        "paylink-tracer>=0.2.1" \
        "uvicorn[standard]>=0.27.0" \
        "starlette>=0.37.0"

# Copy the server code
COPY mcp_servers/example_server/server.py .
COPY mcp_servers/example_server/src/ ./src/

# Expose the port the server runs on
EXPOSE 5002

# Command to run the MCP server
CMD ["python", "server.py"]