# Traefik Guide

> Configure Traefik with PQCert certificates

Traefik is a modern reverse proxy and load balancer. Here's how to use PQCert certificates with Traefik.

---

## Static Configuration

### traefik.yml

```yaml
# API and Dashboard
api:
  dashboard: true
  insecure: true  # Only for development

# Entry Points
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

# Providers
providers:
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true

# TLS Configuration
tls:
  certificates:
    - certFile: /certs/localhost.pem
      keyFile: /certs/localhost-key.pem
```

---

## Dynamic Configuration

### dynamic.yml

```yaml
# HTTP Routers
http:
  routers:
    app:
      rule: "Host(`localhost`)"
      entryPoints:
        - websecure
      service: app
      tls: {}

    api:
      rule: "Host(`api.localhost`)"
      entryPoints:
        - websecure
      service: api
      tls: {}

  # Services
  services:
    app:
      loadBalancer:
        servers:
          - url: "http://localhost:3000"

    api:
      loadBalancer:
        servers:
          - url: "http://localhost:3001"
```

---

## Docker Compose

### docker-compose.yml

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
      - ${HOME}/.pqcert/certs/localhost:/certs:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro

  app:
    image: your-app
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`localhost`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls=true"
      - "traefik.http.services.app.loadbalancer.server.port=3000"
```

### traefik.yml (for Docker)

```yaml
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false
  file:
    filename: /etc/traefik/dynamic.yml

tls:
  certificates:
    - certFile: /certs/localhost.pem
      keyFile: /certs/localhost-key.pem
```

---

## Docker Labels

### Basic Service

```yaml
services:
  myapp:
    image: myapp:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`localhost`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls=true"
      - "traefik.http.services.myapp.loadbalancer.server.port=3000"
```

### Multiple Services

```yaml
services:
  frontend:
    image: frontend:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`localhost`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

  api:
    image: api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.localhost`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.services.api.loadbalancer.server.port=8080"

  admin:
    image: admin:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.admin.rule=Host(`admin.localhost`)"
      - "traefik.http.routers.admin.entrypoints=websecure"
      - "traefik.http.routers.admin.tls=true"
      - "traefik.http.services.admin.loadbalancer.server.port=8000"
```

---

## Path-based Routing

```yaml
services:
  app:
    image: app:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`localhost`) && PathPrefix(`/`)"
      - "traefik.http.routers.app.priority=1"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls=true"

  api:
    image: api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`localhost`) && PathPrefix(`/api`)"
      - "traefik.http.routers.api.priority=2"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.middlewares.api-strip.stripprefix.prefixes=/api"
      - "traefik.http.routers.api.middlewares=api-strip"
```

---

## Load Balancing

### dynamic.yml

```yaml
http:
  routers:
    app:
      rule: "Host(`localhost`)"
      entryPoints:
        - websecure
      service: app
      tls: {}

  services:
    app:
      loadBalancer:
        servers:
          - url: "http://app1:3000"
          - url: "http://app2:3000"
          - url: "http://app3:3000"
        healthCheck:
          path: /health
          interval: 10s
          timeout: 3s
```

---

## WebSocket Support

```yaml
services:
  websocket:
    image: websocket-app:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ws.rule=Host(`localhost`) && PathPrefix(`/ws`)"
      - "traefik.http.routers.ws.entrypoints=websecure"
      - "traefik.http.routers.ws.tls=true"
      - "traefik.http.services.ws.loadbalancer.server.port=8080"
```

---

## Middlewares

### Rate Limiting

```yaml
http:
  middlewares:
    ratelimit:
      rateLimit:
        average: 100
        burst: 50

  routers:
    api:
      rule: "Host(`api.localhost`)"
      middlewares:
        - ratelimit
      service: api
      tls: {}
```

### Basic Auth

```yaml
http:
  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$apr1$..."  # htpasswd generated

  routers:
    admin:
      rule: "Host(`admin.localhost`)"
      middlewares:
        - auth
      service: admin
      tls: {}
```

### CORS

```yaml
http:
  middlewares:
    cors:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
          - OPTIONS
        accessControlAllowHeaders:
          - Content-Type
          - Authorization
        accessControlAllowOriginList:
          - "https://localhost:3000"
        accessControlMaxAge: 100
        addVaryHeader: true
```

### Security Headers

```yaml
http:
  middlewares:
    security:
      headers:
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
```

---

## Kubernetes with Traefik

### IngressRoute

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: app-ingress
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`localhost`)
      kind: Rule
      services:
        - name: app-service
          port: 80
  tls:
    secretName: pqcert-tls
---
apiVersion: v1
kind: Secret
metadata:
  name: pqcert-tls
  namespace: default
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

### Create Secret

```bash
kubectl create secret tls pqcert-tls \
  --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
  --key=$HOME/.pqcert/certs/localhost/localhost-key.pem
```

---

## Health Checks

```yaml
http:
  services:
    app:
      loadBalancer:
        servers:
          - url: "http://app:3000"
        healthCheck:
          path: /health
          interval: 10s
          timeout: 3s
          scheme: http
```

---

## Metrics and Monitoring

### traefik.yml

```yaml
metrics:
  prometheus:
    entryPoint: metrics
    addEntryPointsLabels: true
    addServicesLabels: true

entryPoints:
  metrics:
    address: ":8082"
```

---

## Access Logs

### traefik.yml

```yaml
accessLog:
  filePath: "/var/log/traefik/access.log"
  format: json
  filters:
    statusCodes:
      - "200-299"
      - "400-499"
      - "500-599"
```

---

## Complete Example

### docker-compose.yml

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--api.insecure=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.file.filename=/etc/traefik/dynamic.yml"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
      - ${HOME}/.pqcert/certs/localhost:/certs:ro

  frontend:
    build: ./frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`localhost`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

  api:
    build: ./api
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`localhost`) && PathPrefix(`/api`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.services.api.loadbalancer.server.port=8080"
```

### dynamic.yml

```yaml
tls:
  certificates:
    - certFile: /certs/localhost.pem
      keyFile: /certs/localhost-key.pem
```

---

## Troubleshooting

### Certificate not loading

```bash
# Check certificate files
ls -la ~/.pqcert/certs/localhost/

# Verify certificate
openssl x509 -in ~/.pqcert/certs/localhost/localhost.pem -text -noout
```

### Dashboard not accessible

```bash
# Access dashboard at
open http://localhost:8080/dashboard/
```

### Check Traefik logs

```bash
docker logs traefik
```

---

## Next Steps

- [Docker Guide](./docker.md) - Docker basics
- [Kubernetes Guide](./kubernetes.md) - K8s with Traefik
- [Nginx Guide](./nginx.md) - Alternative: Nginx
