# Terminal Veil - Render Deployment
FROM python:3.11-slim

# Install system dependencies for OpenCV and zbar
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "120", "app:app"]
