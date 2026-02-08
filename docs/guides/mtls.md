# mTLS Guide

> Mutual TLS (mTLS) for service-to-service authentication

Mutual TLS provides two-way authentication where both client and server verify each other's certificates. This is essential for secure service-to-service communication.

---

## How mTLS Works

```
┌──────────┐                    ┌──────────┐
│  Client  │◄──── Verify ──────►│  Server  │
│          │                    │          │
│ Has:     │                    │ Has:     │
│ - Cert   │──── Present ──────►│ - Cert   │
│ - Key    │◄─── Present ───────│ - Key    │
│ - CA     │                    │ - CA     │
└──────────┘                    └──────────┘
```

1. Client connects to server
2. Server presents its certificate
3. Client verifies server certificate against CA
4. Client presents its certificate
5. Server verifies client certificate against CA
6. Encrypted connection established

---

## Generate Service Certificates

### Using PQCert CLI

```bash
# Generate certificates for each service
pqcert service-a.local
pqcert service-b.local
pqcert api-gateway.local
```

### Certificate Structure

```
~/.pqcert/
├── ca/
│   ├── pqcert-ca.pem      # Root CA (shared)
│   └── pqcert-ca-key.pem  # CA private key
└── certs/
    ├── service-a.local/
    │   ├── service-a.local.pem
    │   └── service-a.local-key.pem
    ├── service-b.local/
    │   ├── service-b.local.pem
    │   └── service-b.local-key.pem
    └── api-gateway.local/
        ├── api-gateway.local.pem
        └── api-gateway.local-key.pem
```

---

## Node.js mTLS Server

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const pqcertDir = path.join(os.homedir(), '.pqcert');
const serviceName = 'service-a.local';

const options = {
  // Server certificate
  cert: fs.readFileSync(path.join(pqcertDir, 'certs', serviceName, `${serviceName}.pem`)),
  key: fs.readFileSync(path.join(pqcertDir, 'certs', serviceName, `${serviceName}-key.pem`)),

  // CA for verifying client certificates
  ca: fs.readFileSync(path.join(pqcertDir, 'ca', 'pqcert-ca.pem')),

  // Require client certificate
  requestCert: true,
  rejectUnauthorized: true
};

const server = https.createServer(options, (req, res) => {
  // Get client certificate info
  const clientCert = req.socket.getPeerCertificate();

  if (req.client.authorized) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      message: 'Hello from mTLS server!',
      client: clientCert.subject.CN,
      authorized: true
    }));
  } else {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Client certificate not authorized' }));
  }
});

server.listen(443, () => {
  console.log('🔐 mTLS server running on https://localhost:443');
});
```

---

## Node.js mTLS Client

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const pqcertDir = path.join(os.homedir(), '.pqcert');
const clientService = 'service-b.local';

const options = {
  hostname: 'service-a.local',
  port: 443,
  path: '/api/data',
  method: 'GET',

  // Client certificate
  cert: fs.readFileSync(path.join(pqcertDir, 'certs', clientService, `${clientService}.pem`)),
  key: fs.readFileSync(path.join(pqcertDir, 'certs', clientService, `${clientService}-key.pem`)),

  // CA for verifying server certificate
  ca: fs.readFileSync(path.join(pqcertDir, 'ca', 'pqcert-ca.pem')),

  rejectUnauthorized: true
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(JSON.parse(data)));
});

req.on('error', console.error);
req.end();
```

---

## Python mTLS Server (FastAPI)

```python
import os
import ssl
import uvicorn
from fastapi import FastAPI, Request
from pathlib import Path

app = FastAPI()

@app.get("/")
async def root(request: Request):
    # Get client certificate info
    client_cert = request.scope.get("transport").get_extra_info("peercert")
    return {
        "message": "Hello from mTLS server!",
        "client": client_cert.get("subject") if client_cert else None,
        "authorized": client_cert is not None
    }

if __name__ == "__main__":
    home = Path.home()
    pqcert_dir = home / ".pqcert"
    service_name = "service-a.local"

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Server certificate
    ssl_context.load_cert_chain(
        certfile=pqcert_dir / "certs" / service_name / f"{service_name}.pem",
        keyfile=pqcert_dir / "certs" / service_name / f"{service_name}-key.pem"
    )

    # CA for client verification
    ssl_context.load_verify_locations(pqcert_dir / "ca" / "pqcert-ca.pem")

    # Require client certificate
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    uvicorn.run(app, host="0.0.0.0", port=443, ssl=ssl_context)
```

---

## Python mTLS Client

```python
import httpx
from pathlib import Path

home = Path.home()
pqcert_dir = home / ".pqcert"
client_service = "service-b.local"

# Create mTLS client
client = httpx.Client(
    cert=(
        str(pqcert_dir / "certs" / client_service / f"{client_service}.pem"),
        str(pqcert_dir / "certs" / client_service / f"{client_service}-key.pem")
    ),
    verify=str(pqcert_dir / "ca" / "pqcert-ca.pem")
)

response = client.get("https://service-a.local:443/api/data")
print(response.json())
```

---

## Go mTLS Server

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "encoding/json"
    "io/ioutil"
    "log"
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    pqcertDir := filepath.Join(home, ".pqcert")
    serviceName := "service-a.local"

    // Load CA certificate
    caCert, _ := ioutil.ReadFile(filepath.Join(pqcertDir, "ca", "pqcert-ca.pem"))
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // Load server certificate
    cert, _ := tls.LoadX509KeyPair(
        filepath.Join(pqcertDir, "certs", serviceName, serviceName+".pem"),
        filepath.Join(pqcertDir, "certs", serviceName, serviceName+"-key.pem"),
    )

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        ClientCAs:    caCertPool,
        ClientAuth:   tls.RequireAndVerifyClientCert,
        MinVersion:   tls.VersionTLS12,
    }

    server := &http.Server{
        Addr:      ":443",
        TLSConfig: tlsConfig,
    }

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        clientCert := r.TLS.PeerCertificates[0]
        json.NewEncoder(w).Encode(map[string]interface{}{
            "message":    "Hello from mTLS server!",
            "client":     clientCert.Subject.CommonName,
            "authorized": true,
        })
    })

    log.Println("🔐 mTLS server running on https://localhost:443")
    log.Fatal(server.ListenAndServeTLS("", ""))
}
```

---

## Go mTLS Client

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    pqcertDir := filepath.Join(home, ".pqcert")
    clientService := "service-b.local"

    // Load CA certificate
    caCert, _ := ioutil.ReadFile(filepath.Join(pqcertDir, "ca", "pqcert-ca.pem"))
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // Load client certificate
    cert, _ := tls.LoadX509KeyPair(
        filepath.Join(pqcertDir, "certs", clientService, clientService+".pem"),
        filepath.Join(pqcertDir, "certs", clientService, clientService+"-key.pem"),
    )

    client := &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{
                RootCAs:      caCertPool,
                Certificates: []tls.Certificate{cert},
            },
        },
    }

    resp, _ := client.Get("https://service-a.local:443/api/data")
    defer resp.Body.Close()

    body, _ := ioutil.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

---

## Nginx mTLS Configuration

```nginx
server {
    listen 443 ssl;
    server_name service-a.local;

    # Server certificate
    ssl_certificate /home/user/.pqcert/certs/service-a.local/service-a.local.pem;
    ssl_certificate_key /home/user/.pqcert/certs/service-a.local/service-a.local-key.pem;

    # Client certificate verification
    ssl_client_certificate /home/user/.pqcert/ca/pqcert-ca.pem;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location / {
        # Pass client certificate info to backend
        proxy_set_header X-Client-Cert-CN $ssl_client_s_dn_cn;
        proxy_set_header X-Client-Cert-Verified $ssl_client_verify;

        proxy_pass http://backend:3000;
    }
}
```

---

## Docker Compose mTLS

### docker-compose.yml

```yaml
version: '3.8'

services:
  service-a:
    build: ./service-a
    volumes:
      - ${HOME}/.pqcert:/certs:ro
    environment:
      - SERVICE_NAME=service-a.local
      - PQCERT_DIR=/certs
    networks:
      - mtls-network

  service-b:
    build: ./service-b
    volumes:
      - ${HOME}/.pqcert:/certs:ro
    environment:
      - SERVICE_NAME=service-b.local
      - PQCERT_DIR=/certs
    networks:
      - mtls-network

networks:
  mtls-network:
    driver: bridge
```

---

## Kubernetes mTLS

### Secret for Each Service

```bash
# Service A
kubectl create secret tls service-a-tls \
  --cert=$HOME/.pqcert/certs/service-a.local/service-a.local.pem \
  --key=$HOME/.pqcert/certs/service-a.local/service-a.local-key.pem

# Service B
kubectl create secret tls service-b-tls \
  --cert=$HOME/.pqcert/certs/service-b.local/service-b.local.pem \
  --key=$HOME/.pqcert/certs/service-b.local/service-b.local-key.pem

# CA ConfigMap
kubectl create configmap pqcert-ca --from-file=ca.pem=$HOME/.pqcert/ca/pqcert-ca.pem
```

### Deployment with mTLS

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-a
spec:
  replicas: 1
  selector:
    matchLabels:
      app: service-a
  template:
    metadata:
      labels:
        app: service-a
    spec:
      containers:
        - name: service-a
          image: service-a:latest
          ports:
            - containerPort: 443
          volumeMounts:
            - name: tls
              mountPath: /certs/tls
              readOnly: true
            - name: ca
              mountPath: /certs/ca
              readOnly: true
          env:
            - name: TLS_CERT
              value: /certs/tls/tls.crt
            - name: TLS_KEY
              value: /certs/tls/tls.key
            - name: CA_CERT
              value: /certs/ca/ca.pem
      volumes:
        - name: tls
          secret:
            secretName: service-a-tls
        - name: ca
          configMap:
            name: pqcert-ca
```

---

## Istio mTLS

### Enable Strict mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

### DestinationRule

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: mtls-rule
  namespace: default
spec:
  host: "*.default.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
```

---

## gRPC mTLS

### Node.js gRPC Server

```javascript
const grpc = require('@grpc/grpc-js');
const fs = require('fs');
const path = require('path');
const os = require('os');

const pqcertDir = path.join(os.homedir(), '.pqcert');
const serviceName = 'service-a.local';

const credentials = grpc.ServerCredentials.createSsl(
  fs.readFileSync(path.join(pqcertDir, 'ca', 'pqcert-ca.pem')),
  [{
    cert_chain: fs.readFileSync(path.join(pqcertDir, 'certs', serviceName, `${serviceName}.pem`)),
    private_key: fs.readFileSync(path.join(pqcertDir, 'certs', serviceName, `${serviceName}-key.pem`))
  }],
  true // requireClientCert
);

const server = new grpc.Server();
server.bindAsync('0.0.0.0:50051', credentials, () => {
  console.log('🔐 gRPC mTLS server running on port 50051');
  server.start();
});
```

### Node.js gRPC Client

```javascript
const grpc = require('@grpc/grpc-js');
const fs = require('fs');
const path = require('path');
const os = require('os');

const pqcertDir = path.join(os.homedir(), '.pqcert');
const clientService = 'service-b.local';

const credentials = grpc.credentials.createSsl(
  fs.readFileSync(path.join(pqcertDir, 'ca', 'pqcert-ca.pem')),
  fs.readFileSync(path.join(pqcertDir, 'certs', clientService, `${clientService}-key.pem`)),
  fs.readFileSync(path.join(pqcertDir, 'certs', clientService, `${clientService}.pem`))
);

const client = new YourServiceClient('service-a.local:50051', credentials);
```

---

## Troubleshooting

### Verify Certificate Chain

```bash
# Verify server cert against CA
openssl verify -CAfile ~/.pqcert/ca/pqcert-ca.pem \
  ~/.pqcert/certs/service-a.local/service-a.local.pem

# Test mTLS connection
openssl s_client -connect localhost:443 \
  -cert ~/.pqcert/certs/service-b.local/service-b.local.pem \
  -key ~/.pqcert/certs/service-b.local/service-b.local-key.pem \
  -CAfile ~/.pqcert/ca/pqcert-ca.pem
```

### Common Errors

**"certificate verify failed"**
- Check CA is correct
- Verify certificate chain

**"no client certificate"**
- Client must send certificate
- Check `requestCert: true` on server

**"certificate not valid"**
- Check expiration date
- Verify hostname matches CN/SAN

---

## Next Steps

- [Kubernetes Guide](./kubernetes.md) - K8s mTLS
- [Docker Guide](./docker.md) - Containerize services
- [CI/CD Guide](./cicd.md) - Automate certificate deployment
