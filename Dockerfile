# Multi-stage Dockerfile for PySpark with Jupyter
# Stage 1: Build dependencies
FROM python:3.9-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if exists
COPY requirements.txt* ./

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ -f requirements.txt ]; then \
      /opt/venv/bin/pip install --no-cache-dir -r requirements.txt; \
    fi

# Stage 2: Runtime
FROM arjones/pyspark:2.4.5

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    SPARK_HOME=/opt/spark \
    JUPYTER_ENABLE_LAB=yes

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Ensure Jupyter can write notebooks
RUN chmod -R 755 /app

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Default command
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
