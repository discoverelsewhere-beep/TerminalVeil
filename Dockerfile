# Terminal Veil - Render Deployment
FROM python:3.11-slim

# Install system dependencies for OpenCV and zbar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use sync version for stability
ENV FLASK_APP=app_sync.py

# Run with gunicorn (Render provides PORT env var)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --keep-alive 60 app_sync:app
