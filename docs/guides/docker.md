# Docker Guide

> Use PQCert certificates in Docker containers

---

## Option 1: Mount Certificates as Volume

The simplest approach - mount your host certificates into the container.

### docker run

```bash
docker run -d \
  -v ~/.pqcert/certs/localhost:/certs:ro \
  -p 443:443 \
  your-app
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "443:443"
    volumes:
      - ~/.pqcert/certs/localhost:/certs:ro
    environment:
      - SSL_CERT=/certs/localhost.pem
      - SSL_KEY=/certs/localhost-key.pem
```

---

## Option 2: Copy Certificates at Build Time

### Dockerfile (Node.js)

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy certificates
COPY --from=certs . /certs/

# Copy application
COPY package*.json ./
RUN npm ci --production
COPY . .

ENV SSL_CERT=/certs/localhost.pem
ENV SSL_KEY=/certs/localhost-key.pem

EXPOSE 443
CMD ["node", "server.js"]
```

### Build with certificates

```bash
# Build with local certs
docker build \
  --build-context certs=~/.pqcert/certs/localhost \
  -t myapp .
```

---

## Option 3: Multi-Stage Build

### Dockerfile

```dockerfile
# Stage 1: Get certificates
FROM alpine as certs
ARG CERT_DIR=/root/.pqcert/certs/localhost
COPY ${CERT_DIR} /certs/

# Stage 2: Build app
FROM node:20-alpine

WORKDIR /app

# Copy certs from stage 1
COPY --from=certs /certs /certs

COPY package*.json ./
RUN npm ci --production
COPY . .

EXPOSE 443
CMD ["node", "server.js"]
```

---

## Example: Node.js with Express

### server.js

```javascript
const express = require('express');
const https = require('https');
const fs = require('fs');

const app = express();

const certPath = process.env.SSL_CERT || '/certs/localhost.pem';
const keyPath = process.env.SSL_KEY || '/certs/localhost-key.pem';

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Docker HTTPS!' });
});

const options = {
  cert: fs.readFileSync(certPath),
  key: fs.readFileSync(keyPath)
};

https.createServer(options, app).listen(443, () => {
  console.log('🔐 HTTPS server running on port 443');
});
```

### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production
COPY . .

EXPOSE 443
CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "443:443"
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/certs:ro
```

### Run

```bash
docker-compose up -d
open https://localhost:443
```

---

## Example: Python with FastAPI

### main.py

```python
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Docker HTTPS!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        ssl_certfile=os.environ.get("SSL_CERT", "/certs/localhost.pem"),
        ssl_keyfile=os.environ.get("SSL_KEY", "/certs/localhost-key.pem")
    )
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 443
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "443:443"
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/certs:ro
```

---

## Example: Go

### main.go

```go
package main

import (
    "net/http"
    "os"
)

func main() {
    certFile := os.Getenv("SSL_CERT")
    if certFile == "" {
        certFile = "/certs/localhost.pem"
    }

    keyFile := os.Getenv("SSL_KEY")
    if keyFile == "" {
        keyFile = "/certs/localhost-key.pem"
    }

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"message": "Hello from Docker HTTPS!"}`))
    })

    http.ListenAndServeTLS(":443", certFile, keyFile, nil)
}
```

### Dockerfile

```dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY . .
RUN go build -o server .

FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/server .

EXPOSE 443
CMD ["./server"]
```

---

## Docker Compose with Nginx

### docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/etc/nginx/certs:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

  app:
    build: .
    expose:
      - "3000"
```

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:3000;
    }

    server {
        listen 80;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;

        ssl_certificate /etc/nginx/certs/localhost.pem;
        ssl_certificate_key /etc/nginx/certs/localhost-key.pem;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## Trust CA Inside Container

If your container needs to make HTTPS requests to other services using PQCert:

### Dockerfile (Debian/Ubuntu)

```dockerfile
FROM node:20

# Copy CA certificate
COPY pqcert-ca.crt /usr/local/share/ca-certificates/

# Update CA certificates
RUN update-ca-certificates

WORKDIR /app
COPY . .
RUN npm ci

CMD ["node", "server.js"]
```

### Dockerfile (Alpine)

```dockerfile
FROM node:20-alpine

# Copy CA certificate
COPY pqcert-ca.crt /usr/local/share/ca-certificates/

# Update CA certificates
RUN apk add --no-cache ca-certificates && update-ca-certificates

WORKDIR /app
COPY . .
RUN npm ci

CMD ["node", "server.js"]
```

### Build

```bash
# Copy CA cert to build context
cp ~/.pqcert/ca/pqcert-ca.pem ./pqcert-ca.crt

# Build
docker build -t myapp .
```

---

## Environment Variables

Use environment variables for flexibility:

```yaml
services:
  app:
    build: .
    environment:
      - SSL_CERT=/certs/localhost.pem
      - SSL_KEY=/certs/localhost-key.pem
      - SSL_CA=/certs/ca/pqcert-ca.pem
    volumes:
      - ${HOME}/.pqcert:/certs:ro
```

---

## Docker Secrets (Swarm)

```yaml
version: '3.8'

services:
  app:
    image: myapp
    secrets:
      - ssl_cert
      - ssl_key
    environment:
      - SSL_CERT=/run/secrets/ssl_cert
      - SSL_KEY=/run/secrets/ssl_key

secrets:
  ssl_cert:
    file: ~/.pqcert/certs/localhost/localhost.pem
  ssl_key:
    file: ~/.pqcert/certs/localhost/localhost-key.pem
```

---

## Troubleshooting

### Permission denied reading certificates

```yaml
# Add read permissions
volumes:
  - ${HOME}/.pqcert/certs/localhost:/certs:ro
```

### Certificate not found

Make sure the path is correct:

```bash
# Check on host
ls ~/.pqcert/certs/localhost/

# Check in container
docker exec -it container_name ls /certs/
```

### HTTPS not working in browser

The CA needs to be installed on your **host machine**, not in the container:

```bash
# On host machine
make install-ca
```

---

## Next Steps

- [Kubernetes Guide](./kubernetes.md) - Deploy to K8s
- [Nginx Guide](./nginx.md) - Advanced nginx config
- [mTLS Guide](./mtls.md) - Service-to-service auth
