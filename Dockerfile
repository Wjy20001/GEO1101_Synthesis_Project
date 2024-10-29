# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-root

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

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

# Install uvicorn explicitly
RUN pip install uvicorn

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8080

# Run the application with host and port
CMD python -m uvicorn API.main:app --host 0.0.0.0 --port $PORT