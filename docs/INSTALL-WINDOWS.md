# PQCert – Windows install

Use one of the methods below to create a localhost HTTPS certificate with PQCert on Windows. **Method A (WSL)** tends to work with the fewest issues; use **Method B** or **C** if you prefer native Windows.

---

## Prerequisites (general)

- **OpenSSL** — Required for certificate generation.
- **Python 3** — For the `pqcert_localhost.py` script.
- **curl or PowerShell** — For downloading files.

---

## Method A: Install with WSL (Windows Subsystem for Linux) (recommended)

In WSL, commands behave like Linux; the install flow matches the [Linux install guide](./INSTALL-LINUX.md).

**Step 1.** Open WSL (search for “WSL” or “Ubuntu” in the Start menu).

**Step 2.** Go to the project folder. Example for accessing the Windows drive:

```bash
cd /mnt/c/Users/YOUR_USERNAME/Documents/Development/pqcert
```

Replace with your username and path.

**Step 3.** Run the install script:

```bash
bash install.sh
```

**Step 4.** This installs the CA inside WSL’s Linux; for the Windows browser you must also add the CA to Windows (see [Add CA to Windows](#add-ca-to-windows-methods-b-and-c) below).

**Step 5.** Certificate files in WSL: `~/.pqcert/certs/localhost/`. From Windows: `\\wsl$\Ubuntu\home\USER\.pqcert\...` (distribution name may differ).

---

## Method B: Install with Git Bash

**Step 1.** Install [Git for Windows](https://git-scm.com/download/win) (includes Git Bash).

**Step 2.** Make OpenSSL available on Windows:

- **Option 1:** [OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html) — Download and install “Win64 OpenSSL”; during setup, choose “Add to PATH”.
- **Option 2:** With Chocolatey: `choco install openssl` (in an elevated PowerShell).

**Step 3.** Install [Python 3 for Windows](https://www.python.org/downloads/). During setup, check **“Add Python to PATH”**.

**Step 4.** Open Git Bash.

**Step 5.** Go to the project folder:

```bash
cd /c/Users/YOUR_USERNAME/Documents/Development/pqcert
```

**Step 6.** Generate certificates:

```bash
python3 cli/pqcert_localhost.py --no-install
```

**Step 7.** Add the CA to Windows: follow [Add CA to Windows](#add-ca-to-windows-methods-b-and-c) below.

---

## Method C: Install with PowerShell

**Step 1.** Install OpenSSL and Python 3 as in Method B; ensure they are on PATH.

**Step 2.** Open PowerShell **as Administrator** (right-click → Run as administrator).

**Step 3.** Go to the project folder:

```powershell
cd C:\Users\YOUR_USERNAME\Documents\Development\pqcert
```

**Step 4.** Create the PQCert directory:

```powershell
$pqcert = "$env:USERPROFILE\.pqcert"
New-Item -ItemType Directory -Force -Path "$pqcert\ca", "$pqcert\certs\localhost"
```

**Step 5.** Download the CLI script (or skip if the project already has it):

```powershell
New-Item -ItemType Directory -Force -Path "$pqcert\bin"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/PQCert/pqcert/main/cli/pqcert_localhost.py" -OutFile "$pqcert\bin\pqcert_localhost.py"
```

**Step 6.** Run the Python script to generate certificates:

```powershell
python cli/pqcert_localhost.py --no-install
```

The script uses `%USERPROFILE%\.pqcert` by default; when run from the project folder it writes there.

**Step 7.** Add the CA to Windows: follow the steps in [Add CA to Windows](#add-ca-to-windows-methods-b-and-c) below.

---

## Add CA to Windows (Methods B and C)

For the browser to show the site as secure, add the CA to the Windows trusted root store.

**Step 1.** Locate the CA file:

- WSL: `~/.pqcert/ca/pqcert-ca.crt` — from Windows access as `\\wsl$\...\...\pqcert-ca.crt`.
- Git Bash/PowerShell (local): `%USERPROFILE%\.pqcert\ca\pqcert-ca.crt`  
  Example: `C:\Users\YourName\.pqcert\ca\pqcert-ca.crt`

**Step 2.** Open PowerShell **as Administrator**.

**Step 3.** Run (adjust path if needed):

```powershell
Import-Certificate -FilePath "$env:USERPROFILE\.pqcert\ca\pqcert-ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

**Alternative (CMD as Administrator):**

```cmd
certutil -addstore -f ROOT %USERPROFILE%\.pqcert\ca\pqcert-ca.crt
```

**Step 4.** Close and reopen the browser; try https://localhost:8443.

---

## File locations (Windows)

| Item | Location |
|------|----------|
| Root CA | `%USERPROFILE%\.pqcert\ca\pqcert-ca.crt` |
| Localhost certificate | `%USERPROFILE%\.pqcert\certs\localhost\localhost.pem` |
| Localhost key | `%USERPROFILE%\.pqcert\certs\localhost\localhost-key.pem` |
| PFX (IIS, .NET) | `%USERPROFILE%\.pqcert\certs\localhost\localhost.pfx` (password: `pqcert`) |

`%USERPROFILE%` is usually `C:\Users\YourUsername`.

---

## Test HTTPS

**Step 1.** From the project folder (Git Bash or PowerShell):

```bash
python test-server.py
```

**Step 2.** Open in the browser: **https://localhost:8443**

**Step 3.** If you added the CA, the page should show as secure.

---

## Remove CA from system

**Step 1.** Open PowerShell **as Administrator**.

**Step 2.** Remove the PQCert CA from the root store:

```powershell
Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*PQCert*" } | Remove-Item
```

**Step 3.** (Optional) Remove PQCert files:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.pqcert"
```

---

## Quick summary

| Step | WSL | Git Bash / PowerShell |
|------|-----|------------------------|
| 1 | In WSL: `bash install.sh` | Install OpenSSL + Python, run `python cli/pqcert_localhost.py --no-install` |
| 2 | Add CA to Windows: PowerShell `Import-Certificate ...` | Same |
| 3 | Test: `python test-server.py` → https://localhost:8443 | Same |

If something fails, check that OpenSSL and Python are on PATH: `openssl version` and `python --version`.
