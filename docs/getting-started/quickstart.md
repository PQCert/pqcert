# Quick Start Guide

> Get HTTPS localhost working in 10 seconds

---

## Step 1: Install PQCert

### macOS / Linux

```bash
curl -sSL https://pqcert.org/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://pqcert.org/install.ps1 | iex
```

### What this does:

1. ✅ Downloads PQCert CLI
2. ✅ Generates a local Root CA
3. ✅ Installs CA to your system trust store
4. ✅ Creates localhost certificates (PEM, CRT, PFX)
5. ✅ Done! https://localhost works

---

## Step 2: Verify Installation

```bash
# Check certificate files
ls ~/.pqcert/certs/localhost/

# Expected output:
# localhost.pem
# localhost-key.pem
# localhost.crt
# localhost-fullchain.pem
# localhost.pfx
```

---

## Step 3: Test It

### Quick Test Server

```bash
# Start test server
cd /path/to/pqcert
make test

# Or with Python
python3 test-server.py
```

### Open in Browser

```
https://localhost:8443
```

✅ **No certificate warnings!**

---

## Step 4: Use in Your App

### Node.js

```javascript
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const certDir = path.join(os.homedir(), '.pqcert', 'certs', 'localhost');

https.createServer({
  key: fs.readFileSync(path.join(certDir, 'localhost-key.pem')),
  cert: fs.readFileSync(path.join(certDir, 'localhost.pem'))
}, (req, res) => {
  res.end('Hello HTTPS!');
}).listen(443);
```

### Python

```python
from flask import Flask
from pathlib import Path

app = Flask(__name__)
cert_dir = Path.home() / '.pqcert' / 'certs' / 'localhost'

@app.route('/')
def hello():
    return 'Hello HTTPS!'

app.run(ssl_context=(
    str(cert_dir / 'localhost.pem'),
    str(cert_dir / 'localhost-key.pem')
), port=443)
```

### Go

```go
package main

import (
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Hello HTTPS!"))
    })

    http.ListenAndServeTLS(":443",
        filepath.Join(certDir, "localhost.pem"),
        filepath.Join(certDir, "localhost-key.pem"),
        nil)
}
```

---

## Certificate Files Explained

| File | Use |
|------|-----|
| `localhost.pem` | Certificate (most frameworks) |
| `localhost-key.pem` | Private key |
| `localhost.crt` | Certificate (Windows format) |
| `localhost-fullchain.pem` | Cert + CA chain (nginx) |
| `localhost.pfx` | PKCS#12 bundle (Java, .NET) |

---

## Supported Domains

Your certificate works for:

- `https://localhost`
- `https://localhost:3000`
- `https://127.0.0.1`
- `https://api.localhost:8080`
- `https://local.dev`
- `https://myapp.local.dev`

---

## Common Commands

```bash
# Generate new certificates
pqcert localhost

# Show certificate info
make info

# Start test server
make test

# Remove CA from system
make uninstall-ca

# Full cleanup
make clean-all
```

---

## What's Next?

- 📖 [Language Guides](../README.md#-language-guides-with-full-code-examples) - Full examples for your stack
- 🐳 [Docker Guide](../guides/docker.md) - Containerize your app
- 🖥️ [Nginx Guide](../guides/nginx.md) - Reverse proxy setup

---

## Troubleshooting

### Certificate still not trusted?

```bash
# Reinstall CA
make install-ca
# Restart your browser
```

### Permission denied for port 443?

Use a higher port (3000, 8443) or:

```bash
# macOS/Linux: Allow binding to port 443
sudo setcap 'cap_net_bind_service=+ep' $(which node)
```

### Need help?

- 💬 [Discord](https://discord.gg/pqcert)
- 🐛 [GitHub Issues](https://github.com/PQCert/pqcert/issues)
