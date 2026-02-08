# Caddy Guide

> Configure Caddy with PQCert certificates

Caddy is a modern web server with automatic HTTPS. For local development with PQCert certificates, you can use custom certificate configuration.

---

## Basic HTTPS Configuration

### Caddyfile

```caddyfile
{
    # Disable automatic HTTPS for local development
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    respond "Hello from Caddy HTTPS!"
}
```

---

## Using Environment Variables

### Caddyfile

```caddyfile
{
    auto_https off
}

localhost {
    tls {$PQCERT_DIR}/certs/localhost/localhost.pem {$PQCERT_DIR}/certs/localhost/localhost-key.pem

    root * /var/www/html
    file_server
}
```

### Run Caddy

```bash
export PQCERT_DIR=$HOME/.pqcert
caddy run --config Caddyfile
```

---

## Reverse Proxy

### Single Backend

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3000
}
```

### With Health Checks

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3000 {
        health_uri /health
        health_interval 10s
    }
}
```

---

## Multiple Applications

```caddyfile
{
    auto_https off
}

# Main app
localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3000
}

# API
api.localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3001
}

# Admin
admin.localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3002
}
```

---

## Path-based Routing

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    # API routes
    handle /api/* {
        reverse_proxy localhost:3001
    }

    # WebSocket
    handle /ws/* {
        reverse_proxy localhost:3002
    }

    # Static files
    handle {
        root * /var/www/html
        file_server
    }
}
```

---

## Load Balancing

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    reverse_proxy localhost:3001 localhost:3002 localhost:3003 {
        lb_policy round_robin
        health_uri /health
        health_interval 10s
    }
}
```

---

## WebSocket Support

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    # WebSocket connections
    @websocket {
        header Connection *Upgrade*
        header Upgrade websocket
    }

    reverse_proxy @websocket localhost:3000

    # Regular HTTP
    reverse_proxy localhost:3000
}
```

---

## PHP with Caddy

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    root * /var/www/html

    php_fastcgi unix//var/run/php/php8.2-fpm.sock

    file_server
}
```

---

## Security Headers

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }

    reverse_proxy localhost:3000
}
```

---

## CORS Configuration

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    @cors_preflight method OPTIONS
    handle @cors_preflight {
        header Access-Control-Allow-Origin "*"
        header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
        header Access-Control-Allow-Headers "Content-Type, Authorization"
        respond "" 204
    }

    header Access-Control-Allow-Origin "*"

    reverse_proxy localhost:3000
}
```

---

## JSON Configuration

### caddy.json

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":443"],
          "routes": [
            {
              "match": [{"host": ["localhost"]}],
              "handle": [
                {
                  "handler": "reverse_proxy",
                  "upstreams": [{"dial": "localhost:3000"}]
                }
              ],
              "terminal": true
            }
          ],
          "tls_connection_policies": [
            {
              "certificate_selection": {
                "any_tag": ["pqcert"]
              }
            }
          ]
        }
      }
    },
    "tls": {
      "certificates": {
        "load_files": [
          {
            "certificate": "/home/user/.pqcert/certs/localhost/localhost.pem",
            "key": "/home/user/.pqcert/certs/localhost/localhost-key.pem",
            "tags": ["pqcert"]
          }
        ]
      }
    }
  }
}
```

### Run with JSON

```bash
caddy run --config caddy.json
```

---

## Docker with Caddy

### Dockerfile

```dockerfile
FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ${HOME}/.pqcert/certs/localhost:/certs:ro
    depends_on:
      - app

  app:
    build: .
    expose:
      - "3000"
```

### Caddyfile (for Docker)

```caddyfile
{
    auto_https off
}

localhost {
    tls /certs/localhost.pem /certs/localhost-key.pem

    reverse_proxy app:3000
}
```

---

## Caddy with React/Vue/Angular

### Development Proxy

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    # API proxy
    handle /api/* {
        reverse_proxy localhost:5000
    }

    # Frontend dev server
    handle {
        reverse_proxy localhost:3000
    }
}
```

### Production Static Files

```caddyfile
{
    auto_https off
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    root * /var/www/dist

    # API proxy
    handle /api/* {
        reverse_proxy localhost:5000
    }

    # SPA fallback
    handle {
        try_files {path} /index.html
        file_server
    }
}
```

---

## Logging

```caddyfile
{
    auto_https off
    log {
        output file /var/log/caddy/access.log
        format json
    }
}

localhost {
    tls /home/user/.pqcert/certs/localhost/localhost.pem /home/user/.pqcert/certs/localhost/localhost-key.pem

    log {
        output file /var/log/caddy/localhost.log
    }

    reverse_proxy localhost:3000
}
```

---

## Troubleshooting

### Certificate not found

```bash
# Check certificate paths
ls -la ~/.pqcert/certs/localhost/

# Make sure Caddy can read them
chmod 644 ~/.pqcert/certs/localhost/*.pem
chmod 600 ~/.pqcert/certs/localhost/*-key.pem
```

### Certificate not trusted

The CA must be installed on the **client** machine:

```bash
make install-ca
```

### Validate Caddyfile

```bash
caddy validate --config Caddyfile
```

### Format Caddyfile

```bash
caddy fmt --overwrite Caddyfile
```

---

## Next Steps

- [Docker Guide](./docker.md) - Containerize with Caddy
- [Nginx Guide](./nginx.md) - Alternative: Nginx configuration
- [Traefik Guide](./traefik.md) - Alternative: Traefik configuration
