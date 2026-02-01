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

PQCert ile yerel geliştirme için **HTTPS (localhost)** sertifikalarını tek komutla oluşturun. Root CA ve localhost sertifikası otomatik üretilir; macOS, Windows ve Linux desteklenir.

## Hızlı kurulum

**macOS / Linux:**

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Windows:** [docs/INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) — WSL, Git Bash veya PowerShell adımları.

Kurulumdan sonra `https://localhost` tarayıcıda güvenli görünür (CA sisteme yüklenir).

---

## Özellikler

- **Tek komut:** Root CA + localhost sertifikası + (isteğe bağlı) sistem güvenilir CA yüklemesi
- **Çoklu platform:** macOS, Windows (WSL/Git Bash/PowerShell), Linux (Debian/Ubuntu, Fedora/RHEL)
- **Standart formatlar:** PEM, CRT, PFX (Windows/.NET için; şifre: `pqcert`)
- **SAN desteği:** localhost, *.localhost, local.dev, 127.0.0.1, ::1

---

## Dokümanlar

| Platform   | Kurulum kılavuzu |
|-----------|-------------------|
| **macOS** | [docs/INSTALL-MACOS.md](docs/INSTALL-MACOS.md) |
| **Windows** | [docs/INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) |
| **Linux** | [docs/INSTALL-LINUX.md](docs/INSTALL-LINUX.md) |

| Konu | Doküman |
|------|---------|
| Tüm dokümanlar | [docs/README.md](docs/README.md) |
| Organizasyon kurulumu (GitHub) | [docs/ORGANIZATION_SETUP.md](docs/ORGANIZATION_SETUP.md) |
| Katkıda bulunma | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Güvenlik | [SECURITY.md](SECURITY.md) |
| Davranış kuralları | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |

---

## Proje yapısı

```
pqcert/
├── cli/                 # CLI (pqcert localhost)
├── backend/             # API (FastAPI)
├── frontend/            # Web arayüzü
├── docs/                # Kurulum kılavuzları (macOS, Windows, Linux)
├── install.sh           # Tek komut kurulum script'i
├── Makefile             # localhost, test, docker, k8s hedefleri
└── docker-compose.yml   # API + frontend + Redis
```

---

## Geliştirme

```bash
# Sertifikaları oluştur (CA'yı sisteme eklemeden)
make localhost

# CA'yı sisteme ekle (sudo gerekir)
make install-ca

# HTTPS test sunucusu (https://localhost:8443)
make test

# Docker ile çalıştır
make docker
```

Daha fazla hedef: `make help`

---

## Lisans

[MIT](LICENSE) — PQCert [organizasyonu](https://github.com/PQCert) altında.
