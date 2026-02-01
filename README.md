# PQCert

<p align="center">
  <strong>Post-Quantum Certificates</strong> — Local HTTPS in seconds.
</p>

<p align="center">
  <a href="https://github.com/PQCert/pqcert/actions"><img src="https://github.com/PQCert/pqcert/workflows/CI/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/PQCert/pqcert"><img src="https://img.shields.io/badge/repo-PQCert%2Fpqcert-6366f1" alt="PQCert/pqcert"></a>
</p>

---

Create **HTTPS (localhost)** certificates for local development with a single command. Root CA and localhost certificate are generated automatically; macOS, Windows, and Linux are supported. **Everyone** is welcome to use, contribute to, and improve PQCert.

## Quick install

**macOS / Linux:**

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Windows:** [docs/INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) — WSL, Git Bash, or PowerShell steps.

After install, `https://localhost` will appear secure in the browser (CA is installed to the system).

---

## Features

- **Single command:** Root CA + localhost certificate + (optional) system trust store install
- **Multi-platform:** macOS, Windows (WSL/Git Bash/PowerShell), Linux (Debian/Ubuntu, Fedora/RHEL)
- **Standard formats:** PEM, CRT, PFX (for Windows/.NET; password: `pqcert`)
- **SAN support:** localhost, *.localhost, local.dev, 127.0.0.1, ::1

---

## Documentation

| Platform   | Install guide |
|-----------|----------------|
| **macOS** | [docs/INSTALL-MACOS.md](docs/INSTALL-MACOS.md) |
| **Windows** | [docs/INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) |
| **Linux** | [docs/INSTALL-LINUX.md](docs/INSTALL-LINUX.md) |

| Topic | Document |
|-------|----------|
| All docs | [docs/README.md](docs/README.md) |
| Full index (Let's Encrypt–style) | [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) |
| Organization setup (GitHub) | [docs/ORGANIZATION_SETUP.md](docs/ORGANIZATION_SETUP.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Code of Conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |

---

## Project structure

```
pqcert/
├── cli/                 # CLI (pqcert localhost)
├── backend/             # API (FastAPI)
├── frontend/            # Web UI
├── docs/                # Install guides (macOS, Windows, Linux)
├── install.sh           # One-command install script
├── Makefile             # localhost, test, docker, k8s targets
└── docker-compose.yml   # API + frontend + Redis
```

---

## Development

```bash
# Generate certificates (without installing CA to system)
make localhost

# Install CA to system (sudo required)
make install-ca

# HTTPS test server (https://localhost:8443)
make test

# Run with Docker
make docker
```

More targets: `make help`

---

## License

[MIT](LICENSE) — Under the [PQCert](https://github.com/PQCert) organization.
