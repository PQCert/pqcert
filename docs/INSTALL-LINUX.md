# PQCert – Linux install

Use the steps below to create a localhost HTTPS certificate with PQCert on Linux. Your distribution may be **Debian/Ubuntu** or **Fedora/RHEL/CentOS**; the step to add the CA to the system trust store differs by distribution.

---

## Prerequisites

**Step 1.** Open a terminal.

**Step 2.** Check that required tools are installed:

```bash
openssl version
python3 --version
curl --version
```

If all show output, continue. Otherwise install as below.

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

## Method A: One-command install (recommended)

**Step 1.** In the terminal, run:

```bash
curl -sSL https://raw.githubusercontent.com/PQCert/pqcert/main/install.sh | bash
```

**Step 2.** The script will:

- Check dependencies (OpenSSL, curl/wget).
- Download the PQCert CLI.
- Install under `~/.pqcert` and add it to PATH (usually `/usr/local/bin/pqcert`).
- Generate the Root CA.
- Generate the localhost certificate.
- Ask to add the CA to the system trust store; your **sudo password** will be prompted.

**Step 3.** Enter your password. The CA is added to one of these locations depending on your distribution:

- **Debian/Ubuntu:** `/usr/local/share/ca-certificates/pqcert-ca.crt` then `update-ca-certificates`
- **Fedora/RHEL:** `/etc/pki/ca-trust/source/anchors/pqcert-ca.crt` then `update-ca-trust extract`

**Step 4.** If you see “PQCert installed successfully!”, the install is complete.

**Step 5.** Verify:

```bash
pqcert version
```

You should see something like `pqcert version 1.0.0`.

---

## Method B: Install from project folder

If you have cloned the PQCert source:

**Step 1.** Go to the project folder:

```bash
cd /path/to/pqcert
```

Example: `cd ~/Development/pqcert`

**Step 2.** Run the install script:

```bash
bash install.sh
```

**Step 3.** Enter your password when prompted (to add the CA to the system).

**Alternative — Generate certificates only, add CA yourself:**

```bash
make localhost
```

Then add the CA as described for your distribution below.

---

## Add CA to system (by distribution)

The script tries to do this automatically; to do it manually:

### Debian / Ubuntu

**Step 1.** Copy the CA file into the ca-certificates directory:

```bash
sudo cp ~/.pqcert/ca/pqcert-ca.crt /usr/local/share/ca-certificates/pqcert-ca.crt
```

**Step 2.** Update the certificate store:

```bash
sudo update-ca-certificates
```

**Step 3.** You should see a message like “1 added”.

### Fedora / RHEL / CentOS

**Step 1.** Copy the CA file into the anchors directory:

```bash
sudo cp ~/.pqcert/ca/pqcert-ca.crt /etc/pki/ca-trust/source/anchors/pqcert-ca.crt
```

**Step 2.** Update the trust store:

```bash
sudo update-ca-trust extract
```

**Step 3.** The browser and `curl` will now trust this CA.

### Other distributions

- CA file: `~/.pqcert/ca/pqcert-ca.crt`
- Typically it is copied to something like `/usr/local/share/ca-certificates/` or `/etc/pki/ca-trust/source/anchors/`, then the distribution’s “update-ca-certificates” or “update-ca-trust” command is run. Check your distribution’s documentation.

---

## File locations (Linux)

| Item | Location |
|------|----------|
| Root CA | `~/.pqcert/ca/pqcert-ca.pem` |
| Root CA key | `~/.pqcert/ca/pqcert-ca-key.pem` |
| Localhost certificate | `~/.pqcert/certs/localhost/localhost.pem` |
| Localhost key | `~/.pqcert/certs/localhost/localhost-key.pem` |
| Full chain | `~/.pqcert/certs/localhost/localhost-fullchain.pem` |
| PFX (Windows/.NET) | `~/.pqcert/certs/localhost/localhost.pfx` (password: `pqcert`) |

`~` is your home directory (e.g. `/home/user`).

---

## Test HTTPS

**Step 1.** From the project folder:

```bash
make test
```

or:

```bash
python3 test-server.py
```

**Step 2.** Open in the browser: **https://localhost:8443**

**Step 3.** If you added the CA, there should be no warning; you should see a lock/secure indicator.

**Step 4.** Test with curl:

```bash
curl -v --cacert ~/.pqcert/ca/pqcert-ca.pem https://localhost:8443
```

---

## Remove CA from system

### Debian / Ubuntu

**Step 1.** Remove the CA file:

```bash
sudo rm -f /usr/local/share/ca-certificates/pqcert-ca.crt
```

**Step 2.** Update the store:

```bash
sudo update-ca-certificates
```

### Fedora / RHEL / CentOS

**Step 1.** Remove the CA file:

```bash
sudo rm -f /etc/pki/ca-trust/source/anchors/pqcert-ca.crt
```

**Step 2.** Update the trust store:

```bash
sudo update-ca-trust extract
```

### All distributions — Remove PQCert files

**Step 1.** Remove certificates and CA data:

```bash
rm -rf ~/.pqcert
```

**Step 2.** (Optional) Remove the `pqcert` link from PATH:

```bash
sudo rm -f /usr/local/bin/pqcert
```

From the project folder you can also use `make uninstall-ca` and `make clean` if defined in the Makefile.

---

## Quick summary

| Step | Debian/Ubuntu | Fedora/RHEL |
|------|----------------|-------------|
| Install | `curl -sSL ... \| bash` or `bash install.sh` | Same |
| CA location | `/usr/local/share/ca-certificates/` | `/etc/pki/ca-trust/source/anchors/` |
| Update | `sudo update-ca-certificates` | `sudo update-ca-trust extract` |
| Remove | `sudo rm .../pqcert-ca.crt` + `update-ca-certificates` | `sudo rm .../pqcert-ca.crt` + `update-ca-trust extract` |

If you run into issues, check that the install exists with: `openssl version`, `python3 --version`, and `ls ~/.pqcert/ca/`.
