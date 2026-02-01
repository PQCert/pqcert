FROM python:3.12-slim

WORKDIR /app

# Install OpenSSL with OQS (Open Quantum Safe) support
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    cmake \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /var/lib/pqcert/certs /var/lib/pqcert/challenges

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
