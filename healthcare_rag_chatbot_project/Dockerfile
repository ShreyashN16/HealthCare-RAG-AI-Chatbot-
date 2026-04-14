
FROM python:3.10-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install system-level build dependencies required by some Python packages
# (e.g., faiss-cpu may need libgomp for OpenMP support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment — this is the key to multi-stage.
# We'll copy ONLY this folder to the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# COPY requirements first (before app code) so Docker caches this layer.
# If requirements.txt hasn't changed, Docker skips this expensive step.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt



FROM python:3.10-slim AS runtime

# Metadata labels (OCI standard)
LABEL maintainer="Shreyash <shreyash@healthcare-rag.dev>" \
      org.opencontainers.image.title="Healthcare RAG Chatbot" \
      org.opencontainers.image.description="Production RAG chatbot with FAISS vector search" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install ONLY the runtime libraries we need (no compilers, no dev headers)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
        tini && \
    rm -rf /var/lib/apt/lists/* && \
    # Remove package manager caches and unnecessary files
    apt-get purge -y --auto-remove && \
    rm -rf /tmp/* /var/tmp/*

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ---- SECURITY: Non-root user ----
# Why: If an attacker exploits the Flask app, they only get 'appuser' privileges,
# not root access to the container filesystem.
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy application code (order matters for cache — least-changing files first)
COPY --chown=appuser:appgroup chatbot/ ./chatbot/
COPY --chown=appuser:appgroup ui/ ./ui/

# Copy FAISS index and document pickle (these are your "database")
# In Step 4, we'll move these to Docker volumes for persistence
COPY --chown=appuser:appgroup vector_db.index .
COPY --chown=appuser:appgroup docs.pkl .

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 5000

# Health check — Docker will ping this every 30s to verify the app is alive.
# If 3 consecutive checks fail, Docker marks the container as "unhealthy".
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use tini as PID 1 (init process)
# Why: Python doesn't handle SIGTERM properly as PID 1. Without tini,
# `docker stop` will wait 10s then SIGKILL your app (potential data corruption).
# Tini forwards signals correctly, enabling graceful shutdown.
ENTRYPOINT ["tini", "--"]

# Production WSGI server (gunicorn) instead of Flask's dev server
# - workers: 2 (for a small container; scale via replicas, not workers)
# - timeout: 120s (sentence-transformers model loading can be slow on first request)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "chatbot.app:app"]
