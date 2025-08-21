FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    sqlite3 \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check - less frequent to reduce log spam
HEALTHCHECK --interval=60s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Copy startup script
COPY startup.sh .
RUN chmod +x startup.sh

# Default command
CMD ["./startup.sh"] 