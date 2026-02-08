# Python Guide

> Use PQCert certificates with Python applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```python
import os
from pathlib import Path

PQCERT_DIR = Path.home() / '.pqcert'
CERT_DIR = PQCERT_DIR / 'certs' / 'localhost'
CA_DIR = PQCERT_DIR / 'ca'

# Certificate files
CERT_FILE = CERT_DIR / 'localhost.pem'
KEY_FILE = CERT_DIR / 'localhost-key.pem'
CA_FILE = CA_DIR / 'pqcert-ca.pem'
FULLCHAIN_FILE = CERT_DIR / 'localhost-fullchain.pem'
PFX_FILE = CERT_DIR / 'localhost.pfx'
```

---

## Built-in HTTPS Server

```python
import http.server
import ssl
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(
    certfile=CERT_DIR / 'localhost.pem',
    keyfile=CERT_DIR / 'localhost-key.pem'
)

server = http.server.HTTPServer(('localhost', 443), http.server.SimpleHTTPRequestHandler)
server.socket = context.wrap_socket(server.socket, server_side=True)

print('🔐 HTTPS server running at https://localhost:443')
server.serve_forever()
```

---

## Flask

### Basic Setup

```python
from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)
CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from Flask HTTPS!'})

@app.route('/api/data')
def get_data():
    return jsonify({'secure': True, 'data': [1, 2, 3]})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=(
            str(CERT_DIR / 'localhost.pem'),
            str(CERT_DIR / 'localhost-key.pem')
        )
    )
```

### Production with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with HTTPS
gunicorn app:app \
  --bind 0.0.0.0:443 \
  --certfile ~/.pqcert/certs/localhost/localhost.pem \
  --keyfile ~/.pqcert/certs/localhost/localhost-key.pem \
  --workers 4
```

### gunicorn.conf.py

```python
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

bind = '0.0.0.0:443'
workers = 4
certfile = str(CERT_DIR / 'localhost.pem')
keyfile = str(CERT_DIR / 'localhost-key.pem')
```

---

## Django

### settings.py (Development)

```python
# settings.py
import os
from pathlib import Path

# PQCert paths
PQCERT_DIR = Path.home() / '.pqcert'
SSL_CERTIFICATE = PQCERT_DIR / 'certs' / 'localhost' / 'localhost.pem'
SSL_PRIVATE_KEY = PQCERT_DIR / 'certs' / 'localhost' / 'localhost-key.pem'

# Security settings for HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### Run with django-sslserver

```bash
# Install
pip install django-sslserver

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'sslserver',
]

# Run
python manage.py runsslserver \
  --certificate ~/.pqcert/certs/localhost/localhost.pem \
  --key ~/.pqcert/certs/localhost/localhost-key.pem \
  0.0.0.0:443
```

### Production with Gunicorn

```bash
gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:443 \
  --certfile ~/.pqcert/certs/localhost/localhost.pem \
  --keyfile ~/.pqcert/certs/localhost/localhost-key.pem
```

---

## FastAPI

### Basic Setup

```python
from fastapi import FastAPI
from pathlib import Path
import uvicorn

app = FastAPI()
CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

@app.get('/')
async def root():
    return {'message': 'Hello from FastAPI HTTPS!'}

@app.get('/api/items/{item_id}')
async def get_item(item_id: int):
    return {'item_id': item_id, 'secure': True}

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=443,
        ssl_keyfile=str(CERT_DIR / 'localhost-key.pem'),
        ssl_certfile=str(CERT_DIR / 'localhost.pem'),
        reload=True
    )
```

### Run with uvicorn CLI

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-keyfile ~/.pqcert/certs/localhost/localhost-key.pem \
  --ssl-certfile ~/.pqcert/certs/localhost/localhost.pem \
  --reload
```

---

## aiohttp

### Server

```python
from aiohttp import web
from pathlib import Path
import ssl

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

async def handle(request):
    return web.json_response({'message': 'Hello from aiohttp HTTPS!'})

app = web.Application()
app.router.add_get('/', handle)

if __name__ == '__main__':
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(
        str(CERT_DIR / 'localhost.pem'),
        str(CERT_DIR / 'localhost-key.pem')
    )

    web.run_app(app, host='0.0.0.0', port=443, ssl_context=ssl_context)
```

### Client

```python
import aiohttp
import asyncio
import ssl
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

async def fetch():
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(str(CA_FILE))

    async with aiohttp.ClientSession() as session:
        async with session.get('https://localhost:443', ssl=ssl_context) as response:
            data = await response.json()
            print(data)

asyncio.run(fetch())
```

---

## Tornado

```python
import tornado.ioloop
import tornado.web
import tornado.httpserver
import ssl
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'message': 'Hello from Tornado HTTPS!'})

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ])

if __name__ == '__main__':
    app = make_app()

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(
        str(CERT_DIR / 'localhost.pem'),
        str(CERT_DIR / 'localhost-key.pem')
    )

    server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
    server.listen(443)

    print('🔐 Tornado HTTPS running at https://localhost:443')
    tornado.ioloop.IOLoop.current().start()
```

---

## HTTPS Client (requests)

### Basic Request

```python
import requests
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

# Verify with PQCert CA
response = requests.get('https://localhost:443', verify=str(CA_FILE))
print(response.json())
```

### Session with Custom CA

```python
import requests
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

session = requests.Session()
session.verify = str(CA_FILE)

# All requests use the custom CA
response = session.get('https://api.localhost:8443/data')
print(response.json())
```

### mTLS Client (Mutual TLS)

```python
import requests
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'
CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

# Client presents certificate to server
response = requests.get(
    'https://secure-service.localhost/api',
    cert=(
        str(CERT_DIR / 'localhost.pem'),
        str(CERT_DIR / 'localhost-key.pem')
    ),
    verify=str(CA_FILE)
)
print(response.json())
```

---

## HTTPS Client (httpx)

```python
import httpx
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

# Sync client
with httpx.Client(verify=str(CA_FILE)) as client:
    response = client.get('https://localhost:443')
    print(response.json())

# Async client
async def fetch():
    async with httpx.AsyncClient(verify=str(CA_FILE)) as client:
        response = await client.get('https://localhost:443')
        return response.json()
```

---

## WebSocket (websockets)

### Server

```python
import asyncio
import websockets
import ssl
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

async def handler(websocket, path):
    async for message in websocket:
        print(f'Received: {message}')
        await websocket.send(f'Echo: {message}')

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    str(CERT_DIR / 'localhost.pem'),
    str(CERT_DIR / 'localhost-key.pem')
)

async def main():
    async with websockets.serve(handler, 'localhost', 443, ssl=ssl_context):
        print('🔐 WSS server running at wss://localhost:443')
        await asyncio.Future()  # run forever

asyncio.run(main())
```

### Client

```python
import asyncio
import websockets
import ssl
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(str(CA_FILE))

async def connect():
    async with websockets.connect('wss://localhost:443', ssl=ssl_context) as ws:
        await ws.send('Hello, secure WebSocket!')
        response = await ws.recv()
        print(f'Received: {response}')

asyncio.run(connect())
```

---

## gRPC with TLS

### Server

```python
import grpc
from concurrent import futures
from pathlib import Path

CERT_DIR = Path.home() / '.pqcert' / 'certs' / 'localhost'

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add your servicer
    # my_service_pb2_grpc.add_MyServiceServicer_to_server(MyServicer(), server)

    # Load certificates
    with open(CERT_DIR / 'localhost-key.pem', 'rb') as f:
        private_key = f.read()
    with open(CERT_DIR / 'localhost.pem', 'rb') as f:
        certificate_chain = f.read()

    server_credentials = grpc.ssl_server_credentials([(private_key, certificate_chain)])
    server.add_secure_port('[::]:443', server_credentials)

    server.start()
    print('🔐 gRPC server running on port 443')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

### Client

```python
import grpc
from pathlib import Path

CA_FILE = Path.home() / '.pqcert' / 'ca' / 'pqcert-ca.pem'

with open(CA_FILE, 'rb') as f:
    trusted_certs = f.read()

credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
channel = grpc.secure_channel('localhost:443', credentials)

# Use your stub
# stub = my_service_pb2_grpc.MyServiceStub(channel)
# response = stub.MyMethod(request)
```

---

## PQCert Helper Module

### pqcert.py

```python
"""
PQCert helper module for Python applications.
"""

import ssl
from pathlib import Path
from typing import Tuple, Optional

class PQCert:
    def __init__(self, pqcert_dir: Optional[Path] = None):
        self.pqcert_dir = pqcert_dir or Path.home() / '.pqcert'
        self.cert_dir = self.pqcert_dir / 'certs' / 'localhost'
        self.ca_dir = self.pqcert_dir / 'ca'

    @property
    def cert_file(self) -> Path:
        return self.cert_dir / 'localhost.pem'

    @property
    def key_file(self) -> Path:
        return self.cert_dir / 'localhost-key.pem'

    @property
    def ca_file(self) -> Path:
        return self.ca_dir / 'pqcert-ca.pem'

    @property
    def fullchain_file(self) -> Path:
        return self.cert_dir / 'localhost-fullchain.pem'

    @property
    def pfx_file(self) -> Path:
        return self.cert_dir / 'localhost.pfx'

    def exists(self) -> bool:
        """Check if certificates exist."""
        return self.cert_file.exists() and self.key_file.exists()

    def ssl_context(self) -> Tuple[str, str]:
        """Return (cert, key) tuple for Flask/FastAPI ssl_context."""
        return (str(self.cert_file), str(self.key_file))

    def server_ssl_context(self) -> ssl.SSLContext:
        """Return SSL context for server."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(self.cert_file), str(self.key_file))
        return context

    def client_ssl_context(self) -> ssl.SSLContext:
        """Return SSL context for client with CA verification."""
        context = ssl.create_default_context()
        context.load_verify_locations(str(self.ca_file))
        return context

    def mtls_ssl_context(self) -> ssl.SSLContext:
        """Return SSL context for mTLS client."""
        context = ssl.create_default_context()
        context.load_verify_locations(str(self.ca_file))
        context.load_cert_chain(str(self.cert_file), str(self.key_file))
        return context


# Singleton instance
pqcert = PQCert()
```

### Usage

```python
from pqcert import pqcert

# Flask
app.run(ssl_context=pqcert.ssl_context())

# FastAPI
uvicorn.run(app, ssl_keyfile=str(pqcert.key_file), ssl_certfile=str(pqcert.cert_file))

# requests
import requests
response = requests.get('https://localhost', verify=str(pqcert.ca_file))
```

---

## Troubleshooting

### Permission denied for port 443

```bash
# Use port 8443 instead
app.run(port=8443, ssl_context=ssl_context)

# Or allow Python to bind to low ports
sudo setcap 'cap_net_bind_service=+ep' $(which python3)
```

### Certificate verify failed

Make sure the CA is installed:

```bash
make install-ca
```

### Self-signed certificate in chain

Add the CA to your requests:

```python
response = requests.get(url, verify='/path/to/pqcert-ca.pem')
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize your Python app
- [Microservices mTLS](../guides/mtls.md) - Service authentication
- [Nginx Guide](../guides/nginx.md) - Reverse proxy setup
