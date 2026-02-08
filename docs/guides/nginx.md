# Nginx Guide

> Configure Nginx with PQCert certificates

---

## Basic HTTPS Configuration

### /etc/nginx/sites-available/default

```nginx
server {
    listen 80;
    server_name localhost;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    # PQCert certificates
    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000" always;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## Using Environment Variables

### /etc/nginx/conf.d/ssl.conf

```nginx
# Define paths (use envsubst to replace)
ssl_certificate     ${PQCERT_DIR}/certs/localhost/localhost-fullchain.pem;
ssl_certificate_key ${PQCERT_DIR}/certs/localhost/localhost-key.pem;
```

### Start with envsubst

```bash
export PQCERT_DIR=$HOME/.pqcert
envsubst < /etc/nginx/conf.d/ssl.conf.template > /etc/nginx/conf.d/ssl.conf
nginx -g 'daemon off;'
```

---

## Reverse Proxy to Application

### Proxy to Node.js/Python app

```nginx
upstream backend {
    server 127.0.0.1:3000;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Multiple Applications

```nginx
# API on api.localhost
server {
    listen 443 ssl http2;
    server_name api.localhost;

    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# App on app.localhost
server {
    listen 443 ssl http2;
    server_name app.localhost;

    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## WebSocket Support

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

---

## Load Balancing

```nginx
upstream app_servers {
    least_conn;
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
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
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ${HOME}/.pqcert/certs/localhost:/etc/nginx/certs:ro
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
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream app {
        server app:3000;
    }

    server {
        listen 80;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;

        ssl_certificate     /etc/nginx/certs/localhost-fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/localhost-key.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## SSL Best Practices

### Modern Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    # Certificates
    ssl_certificate     /home/user/.pqcert/certs/localhost/localhost-fullchain.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    # Protocols - TLS 1.2 and 1.3 only
    ssl_protocols TLSv1.2 TLSv1.3;

    # Modern ciphers
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # SSL session
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # ... rest of config
}
```

---

## Test Configuration

```bash
# Test nginx config
sudo nginx -t

# Reload nginx
sudo nginx -s reload

# Check SSL certificate
openssl s_client -connect localhost:443 -servername localhost
```

---

## Troubleshooting

### Permission denied

```bash
# Make sure nginx can read the certificates
sudo chmod 644 ~/.pqcert/certs/localhost/*.pem
sudo chmod 600 ~/.pqcert/certs/localhost/*-key.pem
```

### Certificate not trusted

The CA must be installed on the **client** machine:

```bash
# On the machine accessing the site
make install-ca
```

### "ssl_certificate" directive is duplicate

Make sure you only have one SSL config per server block.

---

## Next Steps

- [Docker Guide](./docker.md) - Containerize with nginx
- [Kubernetes Guide](./kubernetes.md) - K8s ingress
- [Apache Guide](./apache.md) - Apache configuration
