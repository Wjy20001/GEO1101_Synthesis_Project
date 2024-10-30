# Stage 1: Build stage
FROM --platform=linux/amd64 python:3.11-slim as builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY API ./API

# Copy only necessary data files
COPY API/data/floorplan.geojson ./API/data/
COPY API/data/nodes.geojson ./API/data/
COPY API/data/slam_coordinates.csv ./API/data/

# Create cache directory
RUN mkdir -p API/data/user_data_cache

# Set environment variables
ENV PYTHONPATH=/app \
  PORT=8080 \
  ENVIRONMENT=production

EXPOSE 8080

CMD python -m uvicorn API.main:app --host 0.0.0.0 --port $PORT