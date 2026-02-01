# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

- Install guides: macOS, Windows, Linux (docs/)
- One-command install: `install.sh`
- CLI: `pqcert localhost`, CA and localhost certificate generation
- Backend API (FastAPI) and frontend
- Docker Compose and Kubernetes examples

---

## [1.0.0] — 2025-01-31

### Added

- Initial release.
- Root CA and localhost certificate generation (OpenSSL).
- macOS, Windows (WSL/Git Bash/PowerShell), Linux support.
- PEM, CRT, PFX formats; SAN (localhost, *.localhost, local.dev, 127.0.0.1, ::1).
- One-command install via `install.sh`.
- `make localhost`, `make test`, `make docker` targets.
- Docs: INSTALL-MACOS, INSTALL-WINDOWS, INSTALL-LINUX, ORGANIZATION_SETUP.

[Unreleased]: https://github.com/PQCert/pqcert/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PQCert/pqcert/releases/tag/v1.0.0
