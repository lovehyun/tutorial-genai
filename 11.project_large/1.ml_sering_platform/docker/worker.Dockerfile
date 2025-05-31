# docker/worker.Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyTorch and GPU support
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU version for base image)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install dependencies
COPY requirements.txt worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/models logs

# Set environment variables
ENV PYTHONPATH=/app
ENV CELERY_APP=worker.celery_app

# Default command
CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=1"]
