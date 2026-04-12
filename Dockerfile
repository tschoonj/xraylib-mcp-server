# Multi-stage build for smaller final image
FROM python:3.12-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Copy source code
COPY src/ src/

# Install dependencies and build the package
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Install the package with all its dependencies from pyproject.toml
RUN uv pip install --no-cache-dir .

# Production stage
FROM python:3.12-slim AS production

# Copy the virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port for HTTP transport (default 8000)
EXPOSE 8000

# Default command runs stdio transport (for use with Docker exec or stdin/stdout)
CMD ["xraylib-mcp-server", "--transport", "stdio"]

# Labels for metadata
LABEL org.opencontainers.image.title="xraylib MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for xraylib X-ray interaction data"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.source="https://github.com/tschoonj/xraylib-mcp-server"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL io.modelcontextprotocol.server.name="io.github.tschoonj/xraylib-mcp-server"
