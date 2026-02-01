#!/usr/bin/env python3
"""
PQCert Localhost - Zero-Config Local SSL Certificates
https://pqcert.org

One command. All platforms. No more localhost SSL pain.

Usage:
    pqcert localhost              # Generate & install localhost cert
    pqcert localhost --install    # Install root CA to system
    pqcert localhost --uninstall  # Remove root CA from system
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

# ============== Configuration ==============

PQCERT_DIR = Path.home() / ".pqcert"
CA_DIR = PQCERT_DIR / "ca"
CERTS_DIR = PQCERT_DIR / "certs"

CA_KEY = CA_DIR / "pqcert-ca-key.pem"
CA_CERT = CA_DIR / "pqcert-ca.pem"
CA_CERT_CRT = CA_DIR / "pqcert-ca.crt"

LOCALHOST_DOMAINS = [
    "localhost",
    "*.localhost",
    "127.0.0.1",
    "::1",
    "local.dev",
    "*.local.dev",
    "dev.local",
    "*.dev.local",
    "test.local",
    "*.test.local",
]

# Colors
class C:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    print(f"""
{C.CYAN}╔═══════════════════════════════════════════════════════╗
║  {C.BOLD}🔐 PQCert Localhost{C.END}{C.CYAN}                                    ║
║     Zero-config local SSL certificates                  ║
║     Works on: Windows • macOS • Linux                   ║
╚═══════════════════════════════════════════════════════╝{C.END}
""")


def print_step(num, total, msg):
    print(f"{C.BLUE}[{num}/{total}]{C.END} {msg}")


def print_success(msg):
    print(f"{C.GREEN}✅ {msg}{C.END}")


def print_error(msg):
    print(f"{C.RED}❌ {msg}{C.END}")


def print_warning(msg):
    print(f"{C.YELLOW}⚠️  {msg}{C.END}")


def print_info(msg):
    print(f"{C.CYAN}ℹ️  {msg}{C.END}")


def get_platform():
    """Detect current platform"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def ensure_directories():
    """Create necessary directories"""
    CA_DIR.mkdir(parents=True, exist_ok=True)
    CERTS_DIR.mkdir(parents=True, exist_ok=True)

    # Secure permissions
    os.chmod(CA_DIR, 0o700)
    os.chmod(CERTS_DIR, 0o700)


def check_openssl():
    """Check if OpenSSL is available"""
    try:
        result = subprocess.run(["openssl", "version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def generate_root_ca():
    """Generate PQCert Root CA"""

    if CA_KEY.exists() and CA_CERT.exists():
        print_info("Root CA already exists, using existing CA")
        return True

    print_step(1, 4, "Generating Root CA private key...")

    # Generate CA private key
    result = subprocess.run([
        "openssl", "genrsa",
        "-out", str(CA_KEY),
        "4096"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print_error(f"Failed to generate CA key: {result.stderr}")
        return False

    os.chmod(CA_KEY, 0o600)

    print_step(2, 4, "Creating Root CA certificate...")

    # CA config
    ca_config = f"""
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = PQCert Local Development CA
O = PQCert
OU = Local Development
C = US

[v3_ca]
basicConstraints = critical, CA:TRUE, pathlen:0
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always, issuer
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as f:
        f.write(ca_config)
        ca_config_path = f.name

    try:
        result = subprocess.run([
            "openssl", "req",
            "-x509", "-new", "-nodes",
            "-key", str(CA_KEY),
            "-sha256",
            "-days", "3650",  # 10 years
            "-out", str(CA_CERT),
            "-config", ca_config_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print_error(f"Failed to generate CA certificate: {result.stderr}")
            return False

        # Also create .crt version for Windows
        shutil.copy(CA_CERT, CA_CERT_CRT)

    finally:
        os.unlink(ca_config_path)

    print_success("Root CA generated successfully!")
    return True


def generate_localhost_cert():
    """Generate localhost certificate signed by our CA"""

    localhost_dir = CERTS_DIR / "localhost"
    localhost_dir.mkdir(parents=True, exist_ok=True)

    key_file = localhost_dir / "localhost-key.pem"
    csr_file = localhost_dir / "localhost.csr"
    cert_file = localhost_dir / "localhost.pem"
    cert_crt = localhost_dir / "localhost.crt"
    cert_pfx = localhost_dir / "localhost.pfx"
    fullchain = localhost_dir / "localhost-fullchain.pem"

    print_step(3, 4, "Generating localhost certificate...")

    # Generate private key
    subprocess.run([
        "openssl", "genrsa",
        "-out", str(key_file),
        "2048"
    ], capture_output=True, check=True)

    os.chmod(key_file, 0o600)

    # Create SAN config
    san_entries = []
    ip_count = 1
    dns_count = 1

    for domain in LOCALHOST_DOMAINS:
        if domain.replace(".", "").replace(":", "").isdigit() or ":" in domain:
            san_entries.append(f"IP.{ip_count} = {domain}")
            ip_count += 1
        else:
            san_entries.append(f"DNS.{dns_count} = {domain}")
            dns_count += 1

    cert_config = f"""
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = localhost
O = PQCert
OU = Local Development

[v3_req]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
{chr(10).join(san_entries)}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as f:
        f.write(cert_config)
        cert_config_path = f.name

    try:
        # Generate CSR
        subprocess.run([
            "openssl", "req",
            "-new",
            "-key", str(key_file),
            "-out", str(csr_file),
            "-config", cert_config_path
        ], capture_output=True, check=True)

        # Sign with CA
        subprocess.run([
            "openssl", "x509",
            "-req",
            "-in", str(csr_file),
            "-CA", str(CA_CERT),
            "-CAkey", str(CA_KEY),
            "-CAcreateserial",
            "-out", str(cert_file),
            "-days", "825",  # Max for browser trust
            "-sha256",
            "-extensions", "v3_req",
            "-extfile", cert_config_path
        ], capture_output=True, check=True)

        # Create .crt copy
        shutil.copy(cert_file, cert_crt)

        # Create fullchain (cert + CA)
        with open(fullchain, 'w') as f:
            f.write(cert_file.read_text())
            f.write(CA_CERT.read_text())

        # Create PFX/P12 for Windows/Java
        subprocess.run([
            "openssl", "pkcs12",
            "-export",
            "-out", str(cert_pfx),
            "-inkey", str(key_file),
            "-in", str(cert_file),
            "-certfile", str(CA_CERT),
            "-password", "pass:pqcert"
        ], capture_output=True, check=True)

        # Clean up CSR
        csr_file.unlink()

    finally:
        os.unlink(cert_config_path)

    print_success("Localhost certificate generated!")
    return localhost_dir


def install_ca_macos():
    """Install CA to macOS Keychain"""
    print_info("Installing CA to macOS Keychain...")

    result = subprocess.run([
        "sudo", "security", "add-trusted-cert",
        "-d", "-r", "trustRoot",
        "-k", "/Library/Keychains/System.keychain",
        str(CA_CERT)
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print_success("CA installed to macOS Keychain")
        return True
    else:
        print_error(f"Failed to install CA: {result.stderr}")
        return False


def install_ca_linux():
    """Install CA to Linux trust store"""
    print_info("Installing CA to Linux trust store...")

    # Detect distro and copy to appropriate location
    ca_paths = [
        "/usr/local/share/ca-certificates/pqcert-ca.crt",  # Debian/Ubuntu
        "/etc/pki/ca-trust/source/anchors/pqcert-ca.crt",  # RHEL/CentOS/Fedora
        "/etc/ca-certificates/trust-source/anchors/pqcert-ca.crt",  # Arch
    ]

    installed = False
    for ca_path in ca_paths:
        ca_dir = os.path.dirname(ca_path)
        if os.path.exists(ca_dir):
            try:
                subprocess.run(["sudo", "cp", str(CA_CERT_CRT), ca_path], check=True)
                installed = True
                break
            except subprocess.CalledProcessError:
                continue

    if not installed:
        print_warning("Could not find CA certificates directory")
        return False

    # Update CA trust
    update_commands = [
        ["sudo", "update-ca-certificates"],  # Debian/Ubuntu
        ["sudo", "update-ca-trust", "extract"],  # RHEL/CentOS/Fedora
        ["sudo", "trust", "extract-compat"],  # Arch
    ]

    for cmd in update_commands:
        try:
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                print_success("CA installed to Linux trust store")
                return True
        except FileNotFoundError:
            continue

    print_warning("CA copied but trust store not updated")
    return True


def install_ca_windows():
    """Install CA to Windows Certificate Store"""
    print_info("Installing CA to Windows Certificate Store...")

    # Use certutil to install
    result = subprocess.run([
        "certutil", "-addstore", "-f", "ROOT", str(CA_CERT_CRT)
    ], capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        print_success("CA installed to Windows Certificate Store")
        return True
    else:
        # Try PowerShell method
        ps_cmd = f'''
        Import-Certificate -FilePath "{CA_CERT_CRT}" -CertStoreLocation Cert:\\LocalMachine\\Root
        '''
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("CA installed to Windows Certificate Store")
            return True

        print_error("Failed to install CA. Run as Administrator.")
        return False


def install_ca():
    """Install CA to system trust store based on platform"""
    plat = get_platform()

    print_step(4, 4, f"Installing CA to {plat} trust store...")

    if plat == "macos":
        return install_ca_macos()
    elif plat == "linux":
        return install_ca_linux()
    elif plat == "windows":
        return install_ca_windows()
    else:
        print_warning(f"Unknown platform: {plat}")
        return False


def uninstall_ca():
    """Remove CA from system trust store"""
    plat = get_platform()

    print_info(f"Removing CA from {plat} trust store...")

    if plat == "macos":
        subprocess.run([
            "sudo", "security", "delete-certificate",
            "-c", "PQCert Local Development CA",
            "/Library/Keychains/System.keychain"
        ])
    elif plat == "linux":
        for path in [
            "/usr/local/share/ca-certificates/pqcert-ca.crt",
            "/etc/pki/ca-trust/source/anchors/pqcert-ca.crt",
            "/etc/ca-certificates/trust-source/anchors/pqcert-ca.crt",
        ]:
            if os.path.exists(path):
                subprocess.run(["sudo", "rm", "-f", path])
        subprocess.run(["sudo", "update-ca-certificates"], capture_output=True)
    elif plat == "windows":
        subprocess.run([
            "certutil", "-delstore", "ROOT", "PQCert Local Development CA"
        ], shell=True)

    print_success("CA removed from system trust store")


def print_certificate_info(cert_dir: Path):
    """Print certificate file locations and usage"""

    print(f"""
{C.GREEN}{'═' * 60}{C.END}
{C.BOLD}🎉 Localhost certificates ready!{C.END}
{C.GREEN}{'═' * 60}{C.END}

{C.BOLD}📁 Certificate Files:{C.END}

   {C.CYAN}PEM (nginx, Apache, Node.js):{C.END}
   • Certificate: {cert_dir}/localhost.pem
   • Private Key: {cert_dir}/localhost-key.pem
   • Full Chain:  {cert_dir}/localhost-fullchain.pem

   {C.CYAN}CRT (General use):{C.END}
   • Certificate: {cert_dir}/localhost.crt

   {C.CYAN}PFX/P12 (Windows, Java, .NET):{C.END}
   • Bundle:      {cert_dir}/localhost.pfx
   • Password:    pqcert

{C.BOLD}📋 Supported Domains:{C.END}
   {', '.join(LOCALHOST_DOMAINS[:6])}
   {', '.join(LOCALHOST_DOMAINS[6:])}

{C.BOLD}🚀 Quick Start Examples:{C.END}

   {C.YELLOW}# Node.js / Express:{C.END}
   const https = require('https');
   const fs = require('fs');
   https.createServer({{
     key: fs.readFileSync('{cert_dir}/localhost-key.pem'),
     cert: fs.readFileSync('{cert_dir}/localhost.pem')
   }}, app).listen(443);

   {C.YELLOW}# nginx:{C.END}
   ssl_certificate     {cert_dir}/localhost-fullchain.pem;
   ssl_certificate_key {cert_dir}/localhost-key.pem;

   {C.YELLOW}# Python / Flask:{C.END}
   app.run(ssl_context=('{cert_dir}/localhost.pem',
                        '{cert_dir}/localhost-key.pem'))

   {C.YELLOW}# .NET / Kestrel:{C.END}
   dotnet dev-certs https --import {cert_dir}/localhost.pfx -p pqcert

{C.GREEN}{'═' * 60}{C.END}
{C.BOLD}🔐 Your localhost is now secure!{C.END}
   Open https://localhost - no more certificate warnings!
{C.GREEN}{'═' * 60}{C.END}
""")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="PQCert Localhost - Zero-config local SSL certificates"
    )
    parser.add_argument("command", nargs="?", default="localhost",
                       help="Command: localhost (default), install, uninstall")
    parser.add_argument("--install-only", action="store_true",
                       help="Only install CA to trust store")
    parser.add_argument("--uninstall", action="store_true",
                       help="Remove CA from trust store")
    parser.add_argument("--no-install", action="store_true",
                       help="Generate certs but don't install CA")

    args = parser.parse_args()

    print_banner()

    # Check OpenSSL
    if not check_openssl():
        print_error("OpenSSL not found. Please install OpenSSL first.")
        sys.exit(1)

    # Uninstall
    if args.uninstall:
        uninstall_ca()
        return

    # Ensure directories
    ensure_directories()

    # Generate Root CA
    if not generate_root_ca():
        sys.exit(1)

    # Install CA only
    if args.install_only:
        install_ca()
        return

    # Generate localhost cert
    cert_dir = generate_localhost_cert()

    # Install CA to system
    if not args.no_install:
        install_ca()

    # Print info
    print_certificate_info(cert_dir)


if __name__ == "__main__":
    main()
