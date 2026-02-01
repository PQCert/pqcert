# Katkıda Bulunma

PQCert projesine katkılarınızı bekliyoruz. Aşağıdaki adımlar işinizi kolaylaştırır.

## Davranış kuralları

Bu proje [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) ile uyumludur. Katkıda bulunurken saygılı ve yapıcı olun.

## Nasıl katkıda bulunulur?

1. **Issue açın** — Hata veya özellik önerisi için [GitHub Issues](https://github.com/PQCert/pqcert/issues) kullanın.
2. **Fork edin** — Repoyu kendi hesabınıza fork edin.
3. **Branch oluşturun** — `main` üzerinde çalışmayın; örneğin `fix/install-linux` veya `feat/windows-powershell`.
4. **Değişiklik yapın** — Kodunuzu yazın; mümkünse test ekleyin.
5. **Pull request açın** — `main` dalına PR gönderin; açıklayıcı bir başlık ve gerekirse issue numarası ekleyin.

## Geliştirme ortamı

- **Python 3.10+** — CLI ve backend için.
- **OpenSSL** — Sertifika üretimi için.
- Yerel test: `make localhost` ve `make test`.

## Kod stili

- Python: PEP 8; proje kökünde `.editorconfig` kullanılır.
- Shell: `install.sh` bash ile yazılmıştır; taşınabilir olmaya dikkat edin.

## Dokümanlar

- Kurulum kılavuzları `docs/` altındadır (macOS, Windows, Linux).
- Değişiklik yaparken ilgili `docs/*.md` dosyasını da güncelleyin.

## Sorular

- **Bug:** [Issue](https://github.com/PQCert/pqcert/issues) açın; işletim sistemi ve adımları belirtin.
- **Özellik:** Önce bir issue ile tartışın; PR’ı ona bağlayın.

Teşekkürler.
