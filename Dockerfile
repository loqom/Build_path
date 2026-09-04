# Python 3.11 slim image (lightweight)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed for any packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check (adjust endpoint if different)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "main.py"]