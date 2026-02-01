# PQCert – Documentation Index

Documentation structure inspired by [Let's Encrypt](https://letsencrypt.org/docs/), adapted for PQCert (local development certificates).

---

## Overview

- **[README (project)](../README.md)** – What PQCert is, quick install, features
- **[Documentation home](./README.md)** – This docs index and install-by-platform links

---

## Getting Started

- **[Install on macOS](./INSTALL-MACOS.md)** – One-command install, Make, or manual steps
- **[Install on Windows](./INSTALL-WINDOWS.md)** – WSL, Git Bash, or PowerShell
- **[Install on Linux](./INSTALL-LINUX.md)** – Debian/Ubuntu and Fedora/RHEL
- **Quick start:** `curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash`

---

## How PQCert Works

- **Local Root CA** – PQCert generates a private Root CA in `~/.pqcert/ca/`
- **Localhost certificate** – A certificate for `localhost`, `*.localhost`, `127.0.0.1`, `::1` is signed by that CA
- **Trust store** – You can install the CA into the system trust store so browsers trust `https://localhost`
- **No ACME server** – For localhost only; no domain validation or public issuance

---

## Why Use HTTPS on Localhost

- **Consistent with production** – Same HTTPS APIs and cookies as production
- **Secure cookies / features** – Some browser features require a secure context
- **No browser warnings** – With PQCert CA installed, `https://localhost` shows as secure

---

## Frequently Asked Questions (FAQ)

- **Where are the certificates?** – `~/.pqcert/certs/localhost/` (Linux/macOS) or `%USERPROFILE%\.pqcert\certs\localhost` (Windows)
- **Can I use this in production?** – No. PQCert is for **local development** only. Use a public CA (e.g. Let's Encrypt) for production.
- **How do I remove the CA?** – See [Remove CA from system](./README.md#remove-ca-from-system) in the docs README
- **What formats are supported?** – PEM, CRT, PFX (password: `pqcert`) for Windows/.NET

---

## Glossary

- **Root CA** – Certificate Authority that signs the localhost certificate; stored in `~/.pqcert/ca/`
- **SAN (Subject Alternative Name)** – Names in the certificate (e.g. localhost, 127.0.0.1)
- **Trust store** – System or browser list of trusted CAs (macOS Keychain, Windows Root store, Linux ca-certificates)

---

## Certificate Policy (Local CA)

- PQCert creates a **local-only** Root CA. It is not intended for public trust.
- Use only on machines you control; do not share the CA or private keys.
- For production, use a public CA (e.g. Let's Encrypt).

---

## Certificates for Localhost

- **[Install guides](./README.md)** – How to generate and install the localhost certificate and CA on each platform
- **SANs included:** `localhost`, `*.localhost`, `local.dev`, `*.local.dev`, `127.0.0.1`, `::1`
- **Formats:** `localhost.pem`, `localhost-key.pem`, `localhost-fullchain.pem`, `localhost.pfx`

---

## Best Practices

- **Keep the CA private** – Do not commit `~/.pqcert/ca/` or private keys to version control
- **Use PFX only when needed** – For Windows/IIS or .NET; password is `pqcert`
- **Remove CA when done** – If you leave a machine or stop development, remove the CA from the system trust store (see [Remove CA](./README.md#remove-ca-from-system))

---

## Revoking / Removing Certificates

- **Remove CA from system** – [macOS](./INSTALL-MACOS.md#remove-ca-from-system), [Windows](./INSTALL-WINDOWS.md#remove-ca-from-system), [Linux](./INSTALL-LINUX.md#remove-ca-from-system)
- **Delete all PQCert data** – `rm -rf ~/.pqcert` (Linux/macOS) or remove `%USERPROFILE%\.pqcert` (Windows)

---

## Client & Developer Information

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** – How to contribute
- **[SECURITY.md](../SECURITY.md)** – How to report vulnerabilities
- **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** – Community guidelines
- **[CHANGELOG.md](../CHANGELOG.md)** – Version history
- **API (backend)** – FastAPI docs at `/docs` when the backend is running
- **CLI** – `pqcert localhost`, `pqcert version`, `pqcert help`

---

## Organization & Repo

- **[ORGANIZATION_SETUP.md](./ORGANIZATION_SETUP.md)** – GitHub org setup, branch ruleset, only founder can merge

---

*This index mirrors common Let's Encrypt doc topics where they apply to PQCert. PQCert is for localhost only and does not replace Let's Encrypt for production.*
