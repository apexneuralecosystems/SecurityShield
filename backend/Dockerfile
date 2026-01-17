FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Increment this to force cache bust
    APP_VERSION=1.0.0

WORKDIR /app

# Install system dependencies
# git is required for cloning repositories
# curl is used for healthchecks
# postgresql-client and libpq-dev for database connectivity
RUN apt-get update && apt-get install -y \
    git \
    curl \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy entrypoint script and make sure it has correct permissions
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p logs workspace/code_projects media staticfiles

# Create a non-root user
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app /usr/local/bin/docker-entrypoint.sh

USER app

# Expose port (metadata)
EXPOSE 8000

# Healthcheck using dynamic port
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Entrypoint to run migrations
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Command to run the application with dynamic port binding
CMD ["sh", "-c", "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"]