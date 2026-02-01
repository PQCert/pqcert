# Güvenlik

## Güvenlik açığı bildirimi

Güvenlik ile ilgili bir sorun bulduğunuzda lütfen bunu **herkese açık bir issue açarak değil**, doğrudan proje maintainer’larına iletin.

### Nasıl bildirilir?

- **E-posta:** [GitHub PQCert organizasyonu](https://github.com/PQCert) üzerinden iletişim kurabilirsiniz; veya
- **GitHub Security:** Repo sayfasında **Security** → **Report a vulnerability** (açıksa) kullanın.

Mümkünse aşağıdakileri ekleyin:

- Sorunun kısa açıklaması
- Etkilenen bileşen (CLI, backend, install script, vb.)
- Adım adım yeniden üretim (mümkünse)
- Önerilen çözüm (varsa)

### Beklenti

- Bildirimi makul sürede inceleyeceğiz.
- Düzeltme yayınlanana kadar detayları gizli tutmaya çalışacağız (koordineli açıklama).
- Bildirimi yapan kişiyi (isteğe bağlı) teşekkürler bölümünde anacağız.

### PQCert’in kapsamı

PQCert **yerel geliştirme** için Root CA ve localhost sertifikası üretir. Bu CA’yı yalnızca güvendiğiniz makinelerde kullanın; production ortamında kendi CA’nızı kullanmanız gerekir.

Sertifika dosyaları (`~/.pqcert`) ve özellikle private key’ler paylaşılmamalı ve güvenli saklanmalıdır.
