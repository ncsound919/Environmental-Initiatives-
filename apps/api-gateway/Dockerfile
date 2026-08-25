# ECOS API Gateway (13 project brains + Level 5 routers)
# Build context is the repository root (see docker-compose.yml).
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY apps/api-gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and ecosystem-brains (resolved at runtime via sys.path)
COPY apps/api-gateway/ ./apps/api-gateway/
COPY packages/ecosystem-brains/ ./packages/ecosystem-brains/
COPY config/ ./config/

WORKDIR /app/apps/api-gateway

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]