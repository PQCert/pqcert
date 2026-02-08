# PQCert Documentation

> **Post-Quantum Certificates for Everyone**
> Secure your localhost and services with quantum-safe TLS in 10 seconds.

---

## 🚀 Quick Start

```bash
# Install PQCert (macOS/Linux)
curl -sSL https://pqcert.org/install.sh | bash

# Your certificates are ready at ~/.pqcert/certs/localhost/
```

**Full doc index (Let's Encrypt–style):** [DOCS_INDEX.md](./DOCS_INDEX.md)

---

## 📚 Documentation Index

### Getting Started
| Guide | Description |
|-------|-------------|
| [Quick Start](getting-started/quickstart.md) | Get HTTPS localhost in 10 seconds |
| [Installation](getting-started/installation.md) | Detailed install for all platforms |
| [Concepts](getting-started/concepts.md) | Post-quantum cryptography basics |

### Platform Installation
| Platform | Guide |
|----------|-------|
| **macOS** | [INSTALL-MACOS.md](./INSTALL-MACOS.md) |
| **Windows** | [INSTALL-WINDOWS.md](./INSTALL-WINDOWS.md) |
| **Linux** | [INSTALL-LINUX.md](./INSTALL-LINUX.md) |

### 💻 Language Guides (with full code examples)
| Language | Framework | Guide |
|----------|-----------|-------|
| **Node.js** | Express, Fastify, NestJS, Koa | [languages/nodejs.md](languages/nodejs.md) |
| **Python** | Flask, Django, FastAPI, aiohttp | [languages/python.md](languages/python.md) |
| **Go** | net/http, Gin, Echo, Fiber | [languages/go.md](languages/go.md) |
| **Java** | Spring Boot, Quarkus, Micronaut | [languages/java.md](languages/java.md) |
| **C# / .NET** | ASP.NET Core, Kestrel, WCF | [languages/dotnet.md](languages/dotnet.md) |
| **Rust** | Actix-web, Axum, Rocket, Warp | [languages/rust.md](languages/rust.md) |
| **PHP** | Laravel, Symfony, Built-in server | [languages/php.md](languages/php.md) |
| **Ruby** | Rails, Sinatra, Puma | [languages/ruby.md](languages/ruby.md) |

### 🖥️ Server Configuration
| Server | Guide |
|--------|-------|
| **Nginx** | [guides/nginx.md](guides/nginx.md) |
| **Apache** | [guides/apache.md](guides/apache.md) |
| **Caddy** | [guides/caddy.md](guides/caddy.md) |
| **Traefik** | [guides/traefik.md](guides/traefik.md) |
| **HAProxy** | [guides/haproxy.md](guides/haproxy.md) |

### 🐳 DevOps & Infrastructure
| Topic | Guide |
|-------|-------|
| **Docker** | [guides/docker.md](guides/docker.md) |
| **Kubernetes** | [guides/kubernetes.md](guides/kubernetes.md) |
| **Docker Compose** | [guides/docker-compose.md](guides/docker-compose.md) |
| **CI/CD** | [guides/cicd.md](guides/cicd.md) |
| **Microservices mTLS** | [guides/mtls.md](guides/mtls.md) |

### 📖 API Reference
| Reference | Description |
|-----------|-------------|
| [CLI Reference](api/cli.md) | All CLI commands |
| [REST API](api/rest.md) | HTTP API for automation |
| [Certificate Formats](api/formats.md) | PEM, CRT, PFX, DER explained |

### ❓ Help & Support
| Topic | Document |
|-------|----------|
| [FAQ](guides/faq.md) | Frequently asked questions |
| [Troubleshooting](guides/troubleshooting.md) | Common issues |
| [Security](../SECURITY.md) | Security policy |
| [Contributing](../CONTRIBUTING.md) | How to contribute |

---

## 📁 Certificate File Locations

After installation:

```
~/.pqcert/
├── ca/
│   ├── pqcert-ca.pem          # Root CA (add to trust store)
│   ├── pqcert-ca.crt          # Root CA (Windows format)
│   └── pqcert-ca-key.pem      # CA private key (KEEP SECRET!)
└── certs/localhost/
    ├── localhost.pem          # Your certificate
    ├── localhost-key.pem      # Private key
    ├── localhost.crt          # Certificate (.crt format)
    ├── localhost-fullchain.pem # Cert + CA chain
    └── localhost.pfx          # PKCS#12 (password: pqcert)
```

**Windows:** `%USERPROFILE%\.pqcert\certs\localhost\`

---

## 🌐 Supported Domains

Your certificate works for:

| Domain | Example Use |
|--------|-------------|
| `localhost` | https://localhost:3000 |
| `*.localhost` | https://api.localhost:8080 |
| `127.0.0.1` | https://127.0.0.1:443 |
| `::1` | IPv6 localhost |
| `local.dev` | https://local.dev |
| `*.local.dev` | https://myapp.local.dev |

---

## 🧪 Test Your Setup

```bash
# Start test server
make test
# or
python3 test-server.py

# Open in browser
open https://localhost:8443
```

✅ No certificate warnings = Success!

---

## 🗑️ Uninstall / Remove CA

- **macOS:** [INSTALL-MACOS.md#remove-ca](./INSTALL-MACOS.md#remove-ca-from-system)
- **Windows:** [INSTALL-WINDOWS.md#remove-ca](./INSTALL-WINDOWS.md#remove-ca-from-system)
- **Linux:** [INSTALL-LINUX.md#remove-ca](./INSTALL-LINUX.md#remove-ca-from-system)

Or simply run:
```bash
make uninstall-ca
```

---

## 💬 Community & Support

- 🐛 [GitHub Issues](https://github.com/PQCert/pqcert/issues)
- 💬 [Discord](https://discord.gg/pqcert)
- 🐦 [Twitter](https://twitter.com/pqcert)
- 📧 [support@pqcert.org](mailto:support@pqcert.org)
