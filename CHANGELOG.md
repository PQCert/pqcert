# Changelog

Tüm önemli değişiklikler bu dosyada listelenir.

Format [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) uyumludur; proje [Semantic Versioning](https://semver.org/spec/v2.0.0.html) kullanır.

---

## [Unreleased]

- Kurulum kılavuzları: macOS, Windows, Linux (docs/)
- Tek komut kurulum: `install.sh`
- CLI: `pqcert localhost`, CA ve localhost sertifikası üretimi
- Backend API (FastAPI) ve frontend
- Docker Compose ve Kubernetes örnekleri

---

## [1.0.0] — 2025-01-31

### Added

- İlk sürüm.
- Root CA ve localhost sertifikası üretimi (OpenSSL).
- macOS, Windows (WSL/Git Bash/PowerShell), Linux desteği.
- PEM, CRT, PFX formatları; SAN (localhost, *.localhost, local.dev, 127.0.0.1, ::1).
- `install.sh` ile tek komut kurulum.
- `make localhost`, `make test`, `make docker` hedefleri.
- Dokümanlar: INSTALL-MACOS, INSTALL-WINDOWS, INSTALL-LINUX, ORGANIZATION_SETUP.

[Unreleased]: https://github.com/PQCert/pqcert/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PQCert/pqcert/releases/tag/v1.0.0
