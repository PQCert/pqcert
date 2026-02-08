# Node.js Guide

> Use PQCert certificates with Node.js applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```javascript
const path = require('path');
const os = require('os');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const certs = {
  key: path.join(CERT_DIR, 'localhost-key.pem'),
  cert: path.join(CERT_DIR, 'localhost.pem'),
  ca: path.join(os.homedir(), '.pqcert', 'ca', 'pqcert-ca.pem')
};
```

---

## Native HTTPS Server

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const options = {
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
};

const server = https.createServer(options, (req, res) => {
  res.writeHead(200);
  res.end('Hello from HTTPS!\n');
});

server.listen(443, () => {
  console.log('🔐 HTTPS server running at https://localhost:443');
});
```

---

## Express.js

### Basic Setup

```javascript
const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const httpsOptions = {
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
};

app.get('/', (req, res) => {
  res.json({ message: 'Hello from secure Express!' });
});

https.createServer(httpsOptions, app).listen(443, () => {
  console.log('🔐 Express HTTPS running at https://localhost:443');
});
```

### With HTTP to HTTPS Redirect

```javascript
const express = require('express');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

// HTTPS options
const httpsOptions = {
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
};

// Your routes
app.get('/', (req, res) => {
  res.json({ secure: true, protocol: req.protocol });
});

// HTTP redirect server
const httpApp = express();
httpApp.all('*', (req, res) => {
  res.redirect(301, `https://${req.hostname}${req.url}`);
});

// Start both servers
http.createServer(httpApp).listen(80, () => {
  console.log('HTTP redirect server on port 80');
});

https.createServer(httpsOptions, app).listen(443, () => {
  console.log('🔐 HTTPS server running at https://localhost:443');
});
```

---

## Fastify

```javascript
const fastify = require('fastify');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const app = fastify({
  https: {
    key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
    cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
  }
});

app.get('/', async (request, reply) => {
  return { hello: 'world', secure: true };
});

app.listen({ port: 443, host: '0.0.0.0' }, (err, address) => {
  if (err) throw err;
  console.log(`🔐 Fastify HTTPS running at ${address}`);
});
```

---

## NestJS

### main.ts

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

async function bootstrap() {
  const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

  const httpsOptions = {
    key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
    cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem')),
  };

  const app = await NestFactory.create(AppModule, { httpsOptions });

  await app.listen(443);
  console.log('🔐 NestJS HTTPS running at https://localhost:443');
}
bootstrap();
```

---

## Koa

```javascript
const Koa = require('koa');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = new Koa();
const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const httpsOptions = {
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
};

app.use(async ctx => {
  ctx.body = { message: 'Hello from Koa HTTPS!' };
});

https.createServer(httpsOptions, app.callback()).listen(443, () => {
  console.log('🔐 Koa HTTPS running at https://localhost:443');
});
```

---

## Hapi

```javascript
const Hapi = require('@hapi/hapi');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const init = async () => {
  const server = Hapi.server({
    port: 443,
    host: 'localhost',
    tls: {
      key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
      cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
    }
  });

  server.route({
    method: 'GET',
    path: '/',
    handler: (request, h) => {
      return { message: 'Hello from Hapi HTTPS!' };
    }
  });

  await server.start();
  console.log('🔐 Hapi HTTPS running at', server.info.uri);
};

init();
```

---

## HTTPS Client (axios, fetch)

### Making HTTPS Requests to Another Service

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const axios = require('axios');

const CA_PATH = path.join(os.homedir(), '.pqcert', 'ca', 'pqcert-ca.pem');

// Create HTTPS agent with custom CA
const httpsAgent = new https.Agent({
  ca: fs.readFileSync(CA_PATH)
});

// Use with axios
async function fetchData() {
  const response = await axios.get('https://api.localhost:8443/data', {
    httpsAgent
  });
  return response.data;
}

// Use with native fetch (Node 18+)
async function fetchWithNative() {
  const response = await fetch('https://api.localhost:8443/data', {
    agent: httpsAgent
  });
  return response.json();
}
```

### mTLS (Mutual TLS) Client

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const axios = require('axios');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');
const CA_PATH = path.join(os.homedir(), '.pqcert', 'ca', 'pqcert-ca.pem');

// mTLS agent - client presents certificate to server
const mtlsAgent = new https.Agent({
  ca: fs.readFileSync(CA_PATH),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem')),
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem'))
});

async function callSecureService() {
  const response = await axios.get('https://secure-service.localhost/api', {
    httpsAgent: mtlsAgent
  });
  return response.data;
}
```

---

## WebSocket (wss://)

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const WebSocket = require('ws');

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const server = https.createServer({
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
});

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    console.log('Received:', message.toString());
    ws.send('Echo: ' + message);
  });
});

server.listen(443, () => {
  console.log('🔐 WSS server running at wss://localhost:443');
});
```

### WebSocket Client

```javascript
const WebSocket = require('ws');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CA_PATH = path.join(os.homedir(), '.pqcert', 'ca', 'pqcert-ca.pem');

const ws = new WebSocket('wss://localhost:443', {
  ca: fs.readFileSync(CA_PATH)
});

ws.on('open', () => {
  console.log('Connected to WSS server');
  ws.send('Hello, secure WebSocket!');
});

ws.on('message', (data) => {
  console.log('Received:', data.toString());
});
```

---

## Next.js

### Custom Server (server.js)

```javascript
const { createServer } = require('https');
const { parse } = require('url');
const next = require('next');
const fs = require('fs');
const path = require('path');
const os = require('os');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

const httpsOptions = {
  key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
};

app.prepare().then(() => {
  createServer(httpsOptions, (req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  }).listen(443, () => {
    console.log('🔐 Next.js HTTPS running at https://localhost:443');
  });
});
```

### package.json script

```json
{
  "scripts": {
    "dev:https": "node server.js"
  }
}
```

---

## Vite (React, Vue, Svelte)

### vite.config.js

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';
import os from 'os';

const CERT_DIR = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

export default defineConfig({
  plugins: [react()],
  server: {
    https: {
      key: fs.readFileSync(path.join(CERT_DIR, 'localhost-key.pem')),
      cert: fs.readFileSync(path.join(CERT_DIR, 'localhost.pem'))
    },
    port: 443
  }
});
```

---

## Environment Variables Helper

Create a helper module to load certificate paths:

### pqcert.js

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

const PQCERT_DIR = process.env.PQCERT_DIR || path.join(os.homedir(), '.pqcert');
const CERT_DIR = path.join(PQCERT_DIR, 'certs', 'localhost');
const CA_DIR = path.join(PQCERT_DIR, 'ca');

module.exports = {
  // Certificate paths
  paths: {
    key: path.join(CERT_DIR, 'localhost-key.pem'),
    cert: path.join(CERT_DIR, 'localhost.pem'),
    fullchain: path.join(CERT_DIR, 'localhost-fullchain.pem'),
    ca: path.join(CA_DIR, 'pqcert-ca.pem'),
    pfx: path.join(CERT_DIR, 'localhost.pfx')
  },

  // Load certificates
  load() {
    return {
      key: fs.readFileSync(this.paths.key),
      cert: fs.readFileSync(this.paths.cert),
      ca: fs.readFileSync(this.paths.ca)
    };
  },

  // HTTPS options for createServer
  httpsOptions() {
    return {
      key: fs.readFileSync(this.paths.key),
      cert: fs.readFileSync(this.paths.cert)
    };
  },

  // HTTPS agent for clients
  httpsAgent() {
    const https = require('https');
    return new https.Agent({
      ca: fs.readFileSync(this.paths.ca)
    });
  },

  // Check if certificates exist
  exists() {
    return fs.existsSync(this.paths.key) && fs.existsSync(this.paths.cert);
  }
};
```

### Usage

```javascript
const pqcert = require('./pqcert');

// Server
const https = require('https');
const server = https.createServer(pqcert.httpsOptions(), app);

// Client
const axios = require('axios');
axios.get('https://api.localhost', { httpsAgent: pqcert.httpsAgent() });
```

---

## Troubleshooting

### EACCES: permission denied, open port 443

Run with sudo or use a port above 1024:

```bash
# Option 1: Use port 3000
server.listen(3000);

# Option 2: Use sudo (not recommended for development)
sudo node server.js

# Option 3: Allow Node.js to bind to privileged ports
sudo setcap 'cap_net_bind_service=+ep' $(which node)
```

### UNABLE_TO_VERIFY_LEAF_SIGNATURE

The CA is not installed in your system. Run:

```bash
make install-ca
```

### Certificate not trusted in browser

1. Make sure CA is installed: `make install-ca`
2. Restart your browser
3. For Chrome, go to `chrome://restart`

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize your Node.js app
- [Microservices mTLS](../guides/mtls.md) - Service-to-service authentication
- [CI/CD Guide](../guides/cicd.md) - Automate certificate management
