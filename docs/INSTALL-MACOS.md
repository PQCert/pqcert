# PQCert – macOS install

Follow these steps to create a localhost HTTPS certificate with PQCert on macOS.

---

## Prerequisites

Make sure these are installed:

1. **Terminal** — Applications → Utilities → Terminal (or search “Terminal” in Spotlight).
2. **OpenSSL** — Usually preinstalled on macOS. Check:
   ```bash
   openssl version
   ```
   If you see output (e.g. `OpenSSL 3.x`), continue.
3. **Python 3** — Check:
   ```bash
   python3 --version
   ```
   If missing, install from [python.org](https://www.python.org/downloads/) or `brew install python3`.
4. **curl** — Usually preinstalled. Check:
   ```bash
   curl --version
   ```

---

## Method A: One-command install (recommended)

If you are not in the project folder, you can run the install script directly:

**Step 1.** Open Terminal.

**Step 2.** Copy and paste the command below, then press Enter:

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Note:** If the script is in your local project folder:

```bash
cd /path/to/pqcert
bash install.sh
```

**Step 3.** If prompted for a password (sudo): enter your Mac login password. This is used to add the CA certificate to the system keychain.

**Step 4.** If you see “PQCert installed successfully!”, the install is complete.

---

## Method B: Install from project folder with Make

If you have cloned the PQCert project:

**Step 1.** Open Terminal.

**Step 2.** Go to the project folder (example):

```bash
cd ~/Documents/Development/pqcert
```

**Step 3.** Generate the localhost certificate:

```bash
make localhost
```

**Step 4.** Add the CA to the system trust store (so the browser does not warn):

```bash
make install-ca
```

Enter your Mac password if prompted.

**Step 5.** Verify:

```bash
pqcert version
```

You should see something like `pqcert version 1.0.0`.

---

## Method C: Manual steps with Python script

**Step 1.** Go to the project folder:

```bash
cd /path/to/pqcert
```

**Step 2.** Generate certificates only (do not install CA to system):

```bash
python3 cli/pqcert_localhost.py --no-install
```

**Step 3.** Add the CA to macOS Keychain (requires admin password):

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.pqcert/ca/pqcert-ca.crt
```

**Step 4.** Enter your password and press Enter.

---

## File locations (macOS)

| Item | Location |
|------|----------|
| Root CA | `~/.pqcert/ca/pqcert-ca.pem` |
| Root CA key | `~/.pqcert/ca/pqcert-ca-key.pem` |
| Localhost certificate | `~/.pqcert/certs/localhost/localhost.pem` |
| Localhost key | `~/.pqcert/certs/localhost/localhost-key.pem` |
| Full chain | `~/.pqcert/certs/localhost/localhost-fullchain.pem` |
| PFX (Windows/.NET) | `~/.pqcert/certs/localhost/localhost.pfx` (password: `pqcert`) |

`~` is your home folder (e.g. `/Users/yourname`).

---

## Test HTTPS

**Step 1.** Start the test server:

```bash
cd /path/to/pqcert
make test
```

or:

```bash
python3 test-server.py
```

**Step 2.** Open in the browser: **https://localhost:8443**

**Step 3.** If you see “Secure” or a lock icon, the CA is installed correctly.

---

## Remove CA from system

To remove the PQCert CA from the Mac trust store:

**Step 1.** In Terminal:

```bash
sudo security delete-certificate -c "PQCert Local Development CA" /Library/Keychains/System.keychain
```

**Step 2.** Enter your password.

**Step 3.** (Optional) To remove all PQCert files:

```bash
rm -rf ~/.pqcert
```

From the project folder you can also use `make uninstall-ca` and `make clean` if defined in the Makefile.
