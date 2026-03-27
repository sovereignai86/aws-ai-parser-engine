# Use a slim, stable Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Watchdog and Boto3
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project structure
COPY . .

# Set PYTHONPATH so modules are discoverable
ENV PYTHONPATH=/app

# Default port for the Orchestrator
EXPOSE 8080

# The CMD is overridden by docker-compose for each service
CMD ["python", "services/orchestration/src/router.py"]
