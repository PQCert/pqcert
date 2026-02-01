# PQCert organizasyonu – Başlangıç kontrol listesi

GitHub organizasyonu: **[https://github.com/PQCert](https://github.com/PQCert)**

Aşağıdaki adımlar organizasyon sayfasındaki önerilerle uyumludur.

---

## 1. Repo oluşturma veya import

**Seçenek A – Yeni repo (önerilen)**

1. [PQCert](https://github.com/PQCert) sayfasında **Repositories** → **New repository**.
2. Repository name: **pqcert**.
3. Public, README eklemeden oluşturun (yerel projede zaten var).
4. Yerel projede:
   ```bash
   cd /path/to/pqcert
   git remote add origin https://github.com/PQCert/pqcert.git
   git branch -M main
   git push -u origin main
   ```

**Seçenek B – Import**

1. **Repositories** → **Import repository**.
2. Eski repo URL’sini girin (varsa); veya önce boş repo oluşturup yukarıdaki gibi push edin.

---

## 2. Organizasyon profilini gösterme (README)

Organizasyon profilinde “README and pinned repositories” herkese açık görünür.

- **Profil README:** `PQCert` organizasyonunda `.github` adlı **public** repo oluşturun, içinde `profile/README.md` yerine repo kökünde **README.md** ekleyin. Bu dosya organizasyon sayfasında görünür.
- İçeriğe örnek: “PQCert – Post-Quantum Certificates for local development. https://github.com/PQCert/pqcert”

---

## 3. İlk üyeyi davet etme

1. **People** → **Invite member**.
2. GitHub kullanıcı adı veya e-posta ile ara (örn. **kursatarslan**).
3. Rol: **Owner** (kurucu) veya **Member**.
4. Davet gönderin.

---

## 4. Branch protection (isteğe bağlı)

`main` dalını korumak için:

1. **pqcert** repo → **Settings** → **Branches** → **Add branch protection rule**.
2. Branch name pattern: **main**.
3. İstediğiniz kurallar:
   - **Require a pull request before merging** (en az 1 onay).
   - **Require status checks to pass** (CI yeşil olsun).
4. **Create** ile kaydedin.

---

## 5. CI/CD – Basit test (isteğe bağlı)

Repo’da GitHub Actions ile kurulum script’ini veya testleri çalıştırmak için:

1. **pqcert** repo → **Actions** → **New workflow** → **set up a workflow yourself**.
2. Örnek `.github/workflows/ci.yml` (projede oluşturulabilir):
   - `install.sh` çalıştırma (Linux runner).
   - veya `make test` / `python test-server.py` (kısa süreli).

Böylece “Run a continuous integration test” önerisi karşılanmış olur.

---

## 6. Discussions (isteğe bağlı)

1. **pqcert** repo → **Settings** → **General** → **Features**.
2. **Discussions** kutusunu işaretleyin.
3. Organizasyon sayfasında **Set up discussions** ile topluluk tartışmalarını açabilirsiniz.

---

## Özet

| Öneri | Yapılacak |
|-------|-----------|
| Repo | `PQCert/pqcert` oluşturup yerel kodu push edin. |
| Invite | People → Invite member (kursatarslan veya diğerleri). |
| Branch protection | main için kural ekleyin (PR + status check). |
| CI | Actions ile basit workflow (install/test). |
| Discussions | Repo veya org’da Discussions’ı açın. |
| Profil | İsteğe bağlı: Org’da `.github` repo + README. |

Önce **repo oluşturup push**, sonra **People** ve **Settings** ile diğer adımlar yapılabilir.
