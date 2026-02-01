# PQCert – macOS Kurulumu

macOS’ta PQCert ile localhost HTTPS sertifikası oluşturmak için aşağıdaki adımları sırayla uygulayın.

---

## Ön koşullar

Bunların yüklü olduğundan emin olun:

1. **Terminal** – Uygulamalar → Araçlar → Terminal (veya Spotlight’ta “Terminal” yazın).
2. **OpenSSL** – macOS’ta genelde yüklüdür. Kontrol için:
   ```bash
   openssl version
   ```
   Çıktı görüyorsanız (örn. `OpenSSL 3.x`) devam edin.
3. **Python 3** – Kontrol:
   ```bash
   python3 --version
   ```
   Yoksa [python.org](https://www.python.org/downloads/) veya `brew install python3` ile kurun.
4. **curl** – Genelde yüklüdür. Kontrol:
   ```bash
   curl --version
   ```

---

## Yöntem A: Tek komutla kurulum (önerilen)

Proje klasöründe değilseniz, doğrudan install script’ini çalıştırabilirsiniz:

**Adım 1.** Terminal’i açın.

**Adım 2.** Aşağıdaki komutu kopyalayıp yapıştırın ve Enter’a basın:

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Not:** Eğer script projede yerel olarak duruyorsa:

```bash
cd /path/to/pqcert
bash install.sh
```

**Adım 3.** Şifre istenirse (sudo): Mac giriş şifrenizi girin. Bu, CA sertifikasını sistem anahtarına eklemek için kullanılır.

**Adım 4.** “PQCert installed successfully!” mesajını gördüyseniz kurulum tamamlanmıştır.

---

## Yöntem B: Proje klasöründen Make ile kurulum

PQCert projesini bilgisayarınıza indirdiyseniz:

**Adım 1.** Terminal’i açın.

**Adım 2.** Proje klasörüne gidin (örnek):

```bash
cd ~/Documents/Development/pqcert
```

**Adım 3.** Localhost sertifikasını oluşturun:

```bash
make localhost
```

**Adım 4.** CA’yı sistem güvenilir sertifikalarına ekleyin (tarayıcı uyarı vermesin diye):

```bash
make install-ca
```

Şifre sorulursa Mac giriş şifrenizi girin.

**Adım 5.** Kurulumu doğrulayın:

```bash
pqcert version
```

Çıktı: `pqcert version 1.0.0` benzeri bir satır olmalı.

---

## Yöntem C: Python script ile manuel adımlar

**Adım 1.** Proje klasörüne gidin:

```bash
cd /path/to/pqcert
```

**Adım 2.** Sadece sertifikaları oluşturun (CA’yı sisteme eklemeden):

```bash
python3 cli/pqcert_localhost.py --no-install
```

**Adım 3.** CA’yı macOS Keychain’e ekleyin (yönetici şifresi gerekir):

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.pqcert/ca/pqcert-ca.crt
```

**Adım 4.** Şifrenizi girin ve Enter’a basın.

---

## Dosya konumları (macOS)

| Ne | Konum |
|----|--------|
| Root CA | `~/.pqcert/ca/pqcert-ca.pem` |
| Root CA anahtarı | `~/.pqcert/ca/pqcert-ca-key.pem` |
| Localhost sertifikası | `~/.pqcert/certs/localhost/localhost.pem` |
| Localhost anahtarı | `~/.pqcert/certs/localhost/localhost-key.pem` |
| Tam zincir | `~/.pqcert/certs/localhost/localhost-fullchain.pem` |
| PFX (Windows/.NET) | `~/.pqcert/certs/localhost/localhost.pfx` (şifre: `pqcert`) |

`~` = kullanıcı klasörünüz (örn. `/Users/adiniz`).

---

## HTTPS’i test etme

**Adım 1.** Test sunucusunu başlatın:

```bash
cd /path/to/pqcert
make test
```

veya:

```bash
python3 test-server.py
```

**Adım 2.** Tarayıcıda açın: **https://localhost:8443**

**Adım 3.** “Güvenli” veya kilit simgesi görüyorsanız CA doğru yüklüdür.

---

## CA’yı sistemden kaldırma

PQCert CA’yı Mac’in güvenilir listesinden silmek için:

**Adım 1.** Terminal’de:

```bash
sudo security delete-certificate -c "PQCert Local Development CA" /Library/Keychains/System.keychain
```

**Adım 2.** Şifrenizi girin.

**Adım 3.** (İsteğe bağlı) Tüm PQCert dosyalarını silmek için:

```bash
rm -rf ~/.pqcert
```

Proje klasöründeyken `make uninstall-ca` ve `make clean` da kullanılabilir (Makefile’da tanımlıysa).
