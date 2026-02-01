# PQCert – Linux Kurulumu

Linux’ta PQCert ile localhost HTTPS sertifikası oluşturmak için aşağıdaki adımları kullanın. Dağıtımınız **Debian/Ubuntu** veya **Fedora/RHEL/CentOS** olabilir; CA’yı sisteme ekleme adımı dağıtıma göre farklıdır.

---

## Ön koşullar

**Adım 1.** Terminal’i açın.

**Adım 2.** Gerekli araçları kontrol edin:

```bash
openssl version
python3 --version
curl --version
```

Hepsi çıktı veriyorsa devam edin. Yoksa aşağıdaki gibi kurun.

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install -y openssl python3 curl
```

**Fedora / RHEL / CentOS:**

```bash
sudo dnf install -y openssl python3 curl
```

---

## Yöntem A: Tek komutla kurulum (önerilen)

**Adım 1.** Terminal’de şu komutu çalıştırın:

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Adım 2.** Script sırasıyla:

- Bağımlılıkları kontrol eder (OpenSSL, curl/wget).
- PQCert CLI’ı indirir.
- `~/.pqcert` altına kurar ve PATH’e ekler (genelde `/usr/local/bin/pqcert`).
- Root CA oluşturur.
- Localhost sertifikası oluşturur.
- CA’yı sistem güvenilir sertifika deposuna eklemek ister; **sudo şifreniz** istenir.

**Adım 3.** Şifrenizi girin. CA, dağıtımınıza göre şu konumlardan birine eklenir:

- **Debian/Ubuntu:** `/usr/local/share/ca-certificates/pqcert-ca.crt` sonra `update-ca-certificates`
- **Fedora/RHEL:** `/etc/pki/ca-trust/source/anchors/pqcert-ca.crt` sonra `update-ca-trust extract`

**Adım 4.** “PQCert installed successfully!” mesajını gördüyseniz kurulum tamamdır.

**Adım 5.** Doğrulama:

```bash
pqcert version
```

Çıktı: `pqcert version 1.0.0` benzeri olmalı.

---

## Yöntem B: Proje klasöründen kurulum

PQCert kaynak kodunu indirdiyseniz:

**Adım 1.** Proje klasörüne gidin:

```bash
cd /path/to/pqcert
```

Örnek: `cd ~/Development/pqcert`

**Adım 2.** Kurulum script’ini çalıştırın:

```bash
bash install.sh
```

**Adım 3.** Şifre istenirse (CA’yı sisteme eklemek için) girin.

**Alternatif – Sadece sertifika, CA’yı siz ekleyin:**

```bash
make localhost
```

Sonra CA’yı dağıtımınıza göre ekleyin (aşağıda).

---

## CA’yı sisteme ekleme (dağıtıma göre)

Script bunu otomatik yapmaya çalışır; manuel yapmak isterseniz:

### Debian / Ubuntu

**Adım 1.** CA dosyasını ca-certificates dizinine kopyalayın:

```bash
sudo cp ~/.pqcert/ca/pqcert-ca.crt /usr/local/share/ca-certificates/pqcert-ca.crt
```

**Adım 2.** Sertifika önbelleğini güncelleyin:

```bash
sudo update-ca-certificates
```

**Adım 3.** “1 added” benzeri bir mesaj görürsünüz.

### Fedora / RHEL / CentOS

**Adım 1.** CA dosyasını anchors dizinine kopyalayın:

```bash
sudo cp ~/.pqcert/ca/pqcert-ca.crt /etc/pki/ca-trust/source/anchors/pqcert-ca.crt
```

**Adım 2.** Güven deposunu güncelleyin:

```bash
sudo update-ca-trust extract
```

**Adım 3.** Tarayıcı ve `curl` artık bu CA’yı güvenilir kabul eder.

### Başka bir dağıtım

- CA dosyası: `~/.pqcert/ca/pqcert-ca.crt`
- Genelde `/usr/local/share/ca-certificates/` veya `/etc/pki/ca-trust/source/anchors/` gibi bir dizine kopyalanır ve dağıtımın “update-ca-certificates” / “update-ca-trust” komutu çalıştırılır. Dağıtım dokümantasyonuna bakın.

---

## Dosya konumları (Linux)

| Ne | Konum |
|----|--------|
| Root CA | `~/.pqcert/ca/pqcert-ca.pem` |
| Root CA anahtarı | `~/.pqcert/ca/pqcert-ca-key.pem` |
| Localhost sertifikası | `~/.pqcert/certs/localhost/localhost.pem` |
| Localhost anahtarı | `~/.pqcert/certs/localhost/localhost-key.pem` |
| Tam zincir | `~/.pqcert/certs/localhost/localhost-fullchain.pem` |
| PFX (Windows/.NET) | `~/.pqcert/certs/localhost/localhost.pfx` (şifre: `pqcert`) |

`~` = ev dizininiz (örn. `/home/kullanici`).

---

## HTTPS’i test etme

**Adım 1.** Proje klasöründe:

```bash
make test
```

veya:

```bash
python3 test-server.py
```

**Adım 2.** Tarayıcıda açın: **https://localhost:8443**

**Adım 3.** CA’yı eklediyseniz uyarı çıkmaz; kilit/güvenli görünür.

**Adım 4.** curl ile test:

```bash
curl -v --cacert ~/.pqcert/ca/pqcert-ca.pem https://localhost:8443
```

---

## CA’yı sistemden kaldırma

### Debian / Ubuntu

**Adım 1.** CA dosyasını kaldırın:

```bash
sudo rm -f /usr/local/share/ca-certificates/pqcert-ca.crt
```

**Adım 2.** Önbelleği güncelleyin:

```bash
sudo update-ca-certificates
```

### Fedora / RHEL / CentOS

**Adım 1.** CA dosyasını kaldırın:

```bash
sudo rm -f /etc/pki/ca-trust/source/anchors/pqcert-ca.crt
```

**Adım 2.** Güven deposunu güncelleyin:

```bash
sudo update-ca-trust extract
```

### Tüm dağıtımlar – PQCert dosyalarını silmek

**Adım 1.** Sertifikalar ve CA’yı silmek:

```bash
rm -rf ~/.pqcert
```

**Adım 2.** (İsteğe bağlı) PATH’e eklenen `pqcert` linkini kaldırmak:

```bash
sudo rm -f /usr/local/bin/pqcert
```

Proje içinde `make uninstall-ca` ve `make clean` varsa onları da kullanabilirsiniz.

---

## Kısa özet

| Adım | Debian/Ubuntu | Fedora/RHEL |
|------|----------------|-------------|
| Kurulum | `curl -sSL ... \| bash` veya `bash install.sh` | Aynı |
| CA konumu | `/usr/local/share/ca-certificates/` | `/etc/pki/ca-trust/source/anchors/` |
| Güncelleme | `sudo update-ca-certificates` | `sudo update-ca-trust extract` |
| Kaldırma | `sudo rm .../pqcert-ca.crt` + `update-ca-certificates` | `sudo rm .../pqcert-ca.crt` + `update-ca-trust extract` |

Sorun olursa: `openssl version`, `python3 --version` ve `ls ~/.pqcert/ca/` ile kurulumun varlığını kontrol edin.
