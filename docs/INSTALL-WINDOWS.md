# PQCert – Windows Kurulumu

Windows’ta PQCert ile localhost HTTPS sertifikası oluşturmak için aşağıdaki yöntemlerden birini kullanın. **Yöntem A (WSL)** en az sorunla çalışır; doğrudan Windows kullanmak isterseniz **Yöntem B** veya **C**’yi izleyin.

---

## Ön koşullar (genel)

- **OpenSSL** – Sertifika üretimi için gerekli.
- **Python 3** – `pqcert_localhost.py` script’i için.
- **curl veya PowerShell** – Dosya indirmek için.

---

## Yöntem A: WSL (Windows Subsystem for Linux) ile kurulum (önerilen)

WSL’de komutlar Linux gibi çalışır; kurulum [Linux kurulum kılavuzuna](./INSTALL-LINUX.md) çok benzer.

**Adım 1.** WSL’i açın (Windows Başlat menüsünde “WSL” veya “Ubuntu” yazın).

**Adım 2.** Proje klasörüne gidin. Windows diskine erişim örneği:

```bash
cd /mnt/c/Users/KULLANICI_ADINIZ/Documents/Development/pqcert
```

Kendi kullanıcı adınızı ve yolu yazın.

**Adım 3.** Kurulum script’ini çalıştırın:

```bash
bash install.sh
```

**Adım 4.** CA’yı WSL içindeki Linux’a yükler; Windows tarayıcısı için CA’yı Windows’a da eklemeniz gerekir (aşağıda [Windows’a CA ekleme](#windowsa-ca-ekleme-yöntem-b-ve-c-icin) bölümüne bakın).

**Adım 5.** Sertifika dosyaları WSL içinde: `~/.pqcert/certs/localhost/`. Windows’tan erişim: `\\wsl$\Ubuntu\home\KULLANICI\.pqcert\...` (dağıtım adı farklı olabilir).

---

## Yöntem B: Git Bash ile kurulum

**Adım 1.** [Git for Windows](https://git-scm.com/download/win) kurun (Git Bash ile gelir).

**Adım 2.** OpenSSL’i Windows’ta kullanılabilir yapın:

- **Seçenek 1:** [OpenSSL Windows indirme](https://slproweb.com/products/Win32OpenSSL.html) – “Win64 OpenSSL” indirip kurun; kurulumda “PATH’e ekle” seçeneğini işaretleyin.
- **Seçenek 2:** Chocolatey ile: `choco install openssl` (yönetici PowerShell’de).

**Adım 3.** [Python 3 for Windows](https://www.python.org/downloads/) kurun. Kurulumda **“Add Python to PATH”** kutusunu işaretleyin.

**Adım 4.** Git Bash’i açın.

**Adım 5.** Proje klasörüne gidin:

```bash
cd /c/Users/KULLANICI_ADINIZ/Documents/Development/pqcert
```

**Adım 6.** Sertifikaları oluşturun:

```bash
python3 cli/pqcert_localhost.py --no-install
```

**Adım 7.** CA’yı Windows’a ekleyin: [Windows’a CA ekleme](#windowsa-ca-ekleme-yöntem-b-ve-c-icin) bölümüne gidin.

---

## Yöntem C: PowerShell ile kurulum

**Adım 1.** OpenSSL ve Python 3’ü Yöntem B’deki gibi kurun; PATH’te olduklarından emin olun.

**Adım 2.** PowerShell’i **Yönetici olarak** açın (sağ tık → Yönetici olarak çalıştır).

**Adım 3.** Proje klasörüne gidin:

```powershell
cd C:\Users\KULLANICI_ADINIZ\Documents\Development\pqcert
```

**Adım 4.** PQCert dizinini oluşturun:

```powershell
$pqcert = "$env:USERPROFILE\.pqcert"
New-Item -ItemType Directory -Force -Path "$pqcert\ca", "$pqcert\certs\localhost"
```

**Adım 5.** CLI script’ini indirin (veya projede zaten varsa bu adımı atlayın):

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/PQCert/pqcert/main/cli/pqcert_localhost.py" -OutFile "$pqcert\bin\pqcert_localhost.py"
```

`$pqcert\bin` klasörünü önce oluşturun: `New-Item -ItemType Directory -Force -Path "$pqcert\bin"`

**Adım 6.** Sertifikaları oluşturmak için Python script’ini çalıştırın:

```powershell
python cli/pqcert_localhost.py --no-install
```

Script varsayılan olarak `%USERPROFILE%\.pqcert` kullanır; proje içinden çalıştırdığınızda aynı dizine yazar.

**Adım 7.** CA’yı Windows’a ekleyin: aşağıdaki “Windows’a CA ekleme” adımlarını uygulayın.

---

## Windows’a CA ekleme (Yöntem B ve C için)

Tarayıcının “Güvenli” demesi için CA’yı Windows güvenilir kök deposuna eklemeniz gerekir.

**Adım 1.** CA dosyasının konumunu bulun:

- WSL: `~/.pqcert/ca/pqcert-ca.crt` → Windows’ta `\\wsl$\...\...\pqcert-ca.crt` olarak erişin.
- Git Bash/PowerShell (yerel): `%USERPROFILE%\.pqcert\ca\pqcert-ca.crt`  
  Örnek: `C:\Users\Adiniz\.pqcert\ca\pqcert-ca.crt`

**Adım 2.** PowerShell’i **Yönetici olarak** açın.

**Adım 3.** Aşağıdaki komutu çalıştırın (yolu kendi CA dosya yolunuzla değiştirin):

```powershell
Import-Certificate -FilePath "$env:USERPROFILE\.pqcert\ca\pqcert-ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

**Alternatif (CMD – Yönetici):**

```cmd
certutil -addstore -f ROOT %USERPROFILE%\.pqcert\ca\pqcert-ca.crt
```

**Adım 4.** Tarayıcıyı kapatıp tekrar açın; https://localhost:8443 adresini deneyin.

---

## Dosya konumları (Windows)

| Ne | Konum |
|----|--------|
| Root CA | `%USERPROFILE%\.pqcert\ca\pqcert-ca.crt` |
| Localhost sertifikası | `%USERPROFILE%\.pqcert\certs\localhost\localhost.pem` |
| Localhost anahtarı | `%USERPROFILE%\.pqcert\certs\localhost\localhost-key.pem` |
| PFX (IIS, .NET) | `%USERPROFILE%\.pqcert\certs\localhost\localhost.pfx` (şifre: `pqcert`) |

`%USERPROFILE%` genelde `C:\Users\KullaniciAdiniz` olur.

---

## HTTPS’i test etme

**Adım 1.** Proje klasöründe (Git Bash veya PowerShell):

```bash
python test-server.py
```

**Adım 2.** Tarayıcıda açın: **https://localhost:8443**

**Adım 3.** CA’yı eklediyseniz sayfa güvenli görünmeli.

---

## CA’yı sistemden kaldırma

**Adım 1.** PowerShell’i **Yönetici olarak** açın.

**Adım 2.** PQCert CA’yı kök depodan kaldırın:

```powershell
Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*PQCert*" } | Remove-Item
```

**Adım 3.** (İsteğe bağlı) PQCert dosyalarını silmek için:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.pqcert"
```

---

## Kısa özet

| Adım | WSL | Git Bash / PowerShell |
|------|-----|------------------------|
| 1 | WSL’de `bash install.sh` | OpenSSL + Python kur, `python cli/pqcert_localhost.py --no-install` |
| 2 | CA’yı Windows’a eklemek için PowerShell: `Import-Certificate ...` | Aynı |
| 3 | Test: `python test-server.py` → https://localhost:8443 | Aynı |

Sorun yaşarsanız önce OpenSSL ve Python’un PATH’te olduğunu kontrol edin: `openssl version` ve `python --version`.
