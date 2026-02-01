# PQCert – Documentation

Create HTTPS (localhost) certificates for local development with PQCert. This page is the index for all documentation.

**Full doc index (Let's Encrypt–style):** [DOCS_INDEX.md](./DOCS_INDEX.md) — Overview, Getting Started, How it works, FAQ, Glossary, Best practices, Revoking, Client/developer info.

---

## Install by platform

| Platform | Guide | Summary |
|----------|--------|---------|
| **macOS** | [INSTALL-MACOS.md](./INSTALL-MACOS.md) | Terminal, `install.sh` or `make` |
| **Windows** | [INSTALL-WINDOWS.md](./INSTALL-WINDOWS.md) | WSL, Git Bash, or PowerShell step-by-step |
| **Linux** | [INSTALL-LINUX.md](./INSTALL-LINUX.md) | Debian/Ubuntu and Fedora/RHEL steps |

---

## Other docs

| Topic | Document |
|-------|----------|
| Organization setup (GitHub) | [ORGANIZATION_SETUP.md](./ORGANIZATION_SETUP.md) |
| Contributing | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Security | [SECURITY.md](../SECURITY.md) |
| Code of Conduct | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) |
| Changelog | [CHANGELOG.md](../CHANGELOG.md) |

---

## After install

- **Certificate files:** `~/.pqcert/certs/localhost/` (Linux/macOS) or `%USERPROFILE%\.pqcert\certs\localhost` (Windows)
- **HTTPS test:** `make test` or `python test-server.py` → open https://localhost:8443 in the browser
- **Remove CA:** See “Remove CA from system” in the platform guides below

---

## Remove CA from system

- **macOS:** [INSTALL-MACOS.md#remove-ca-from-system](./INSTALL-MACOS.md#remove-ca-from-system)
- **Windows:** [INSTALL-WINDOWS.md#remove-ca-from-system](./INSTALL-WINDOWS.md#remove-ca-from-system)
- **Linux:** [INSTALL-LINUX.md#remove-ca-from-system](./INSTALL-LINUX.md#remove-ca-from-system)
