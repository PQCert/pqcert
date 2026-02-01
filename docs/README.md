# PQCert – Dokümanlar

PQCert ile yerel geliştirme için HTTPS sertifikaları (localhost) oluşturabilirsiniz. Bu sayfa tüm dokümanların indeksidir.

---

## Kurulum (platforma göre)

| İşletim Sistemi | Kılavuz | Özet |
|-----------------|---------|------|
| **macOS** | [INSTALL-MACOS.md](./INSTALL-MACOS.md) | Terminal, `install.sh` veya `make` ile kurulum |
| **Windows** | [INSTALL-WINDOWS.md](./INSTALL-WINDOWS.md) | WSL, Git Bash veya PowerShell ile adım adım |
| **Linux** | [INSTALL-LINUX.md](./INSTALL-LINUX.md) | Debian/Ubuntu ve Fedora/RHEL için ayrı adımlar |

---

## Diğer dokümanlar

| Konu | Dosya |
|------|--------|
| Organizasyon kurulumu (GitHub) | [ORGANIZATION_SETUP.md](./ORGANIZATION_SETUP.md) |
| Katkıda bulunma | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Güvenlik | [SECURITY.md](../SECURITY.md) |
| Davranış kuralları | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) |
| Sürüm geçmişi | [CHANGELOG.md](../CHANGELOG.md) |

---

## Kurulumdan sonra

- **Sertifika dosyaları:** `~/.pqcert/certs/localhost/` (Linux/macOS) veya `%USERPROFILE%\.pqcert\certs\localhost` (Windows)
- **HTTPS test:** `make test` veya `python test-server.py` → tarayıcıda https://localhost:8443
- **CA’yı kaldırma:** Aşağıdaki platform kılavuzlarındaki “CA’yı sistemden kaldırma” bölümüne bakın

---

## CA’yı sistemden kaldırma

- **macOS:** [INSTALL-MACOS.md#ca-yi-sistemden-kaldirma](./INSTALL-MACOS.md#ca-yi-sistemden-kaldirma)
- **Windows:** [INSTALL-WINDOWS.md#ca-yi-sistemden-kaldirma](./INSTALL-WINDOWS.md#ca-yi-sistemden-kaldirma)
- **Linux:** [INSTALL-LINUX.md#ca-yi-sistemden-kaldirma](./INSTALL-LINUX.md#ca-yi-sistemden-kaldirma)
