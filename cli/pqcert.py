#!/usr/bin/env python3
"""
PQCert CLI - Get Post-Quantum Certificates in Seconds
https://pqcert.org

Usage:
    pqcert get example.com
    pqcert get example.com --algorithm hybrid
    pqcert renew
    pqcert status
"""

import argparse
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx

# Configuration
API_URL = os.environ.get("PQCERT_API", "https://api.pqcert.org")
CERT_DIR = Path(os.environ.get("PQCERT_DIR", "/etc/pqcert"))
CONFIG_FILE = CERT_DIR / "config.json"

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    print(f"""
{Colors.BLUE}╔═══════════════════════════════════════════╗
║  {Colors.BOLD}🔐 PQCert - Post-Quantum Certificates{Colors.END}{Colors.BLUE}     ║
║     Quantum-safe security for everyone      ║
╚═══════════════════════════════════════════╝{Colors.END}
""")


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def ensure_cert_dir():
    """Ensure certificate directory exists"""
    if not CERT_DIR.exists():
        try:
            CERT_DIR.mkdir(parents=True, mode=0o700)
        except PermissionError:
            print_error(f"Cannot create {CERT_DIR}. Try running with sudo.")
            sys.exit(1)


def get_certificate(domain: str, algorithm: str = "hybrid", email: str = None):
    """Main function to obtain a certificate"""

    print_banner()
    print_info(f"Requesting certificate for: {Colors.BOLD}{domain}{Colors.END}")
    print_info(f"Algorithm: {algorithm}")
    print()

    # Step 1: Request certificate
    print(f"[1/4] Requesting certificate...")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{API_URL}/v1/certificate/request",
                json={
                    "domain": domain,
                    "email": email,
                    "algorithm": algorithm
                }
            )
            response.raise_for_status()
            challenge = response.json()
    except httpx.HTTPError as e:
        print_error(f"Failed to request certificate: {e}")
        sys.exit(1)

    # Step 2: Setup challenge
    print(f"[2/4] Setting up domain verification...")

    challenge_token = challenge["challenge_token"]
    challenge_id = challenge["challenge_id"]

    # Create challenge directory and file
    challenge_dir = Path(f"/var/www/html/.well-known/pqcert-challenge")
    challenge_file = challenge_dir / challenge_token

    try:
        challenge_dir.mkdir(parents=True, exist_ok=True)
        challenge_file.write_text(challenge_token)
        print_success("Challenge file created")
    except PermissionError:
        print_warning("Could not auto-create challenge file.")
        print()
        print(f"Please create this file manually:")
        print(f"  Path: {Colors.YELLOW}.well-known/pqcert-challenge/{challenge_token}{Colors.END}")
        print(f"  Content: {Colors.YELLOW}{challenge_token}{Colors.END}")
        print()
        input("Press Enter when ready...")

    # Step 3: Verify domain
    print(f"[3/4] Verifying domain ownership...")

    # Wait a moment for DNS/web server
    time.sleep(2)

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(f"{API_URL}/v1/certificate/verify/{challenge_id}")
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError as e:
        print_error(f"Domain verification failed: {e}")
        print_info("Make sure your web server is running and the challenge file is accessible.")
        sys.exit(1)

    if not result.get("success"):
        print_error(result.get("message", "Verification failed"))
        sys.exit(1)

    print_success("Domain verified!")

    # Step 4: Download certificates
    print(f"[4/4] Downloading certificates...")

    cert_id = result["certificate_id"]
    domain_dir = CERT_DIR / domain

    ensure_cert_dir()
    domain_dir.mkdir(parents=True, exist_ok=True)

    files_to_download = ["cert.pem", "key.pem", "chain.pem", "fullchain.pem"]

    try:
        with httpx.Client(timeout=30) as client:
            for filename in files_to_download:
                url = f"{API_URL}/v1/certificate/{cert_id}/{filename}"
                response = client.get(url)

                if response.status_code == 200:
                    file_path = domain_dir / filename
                    file_path.write_bytes(response.content)

                    # Secure permissions for key file
                    if filename == "key.pem":
                        os.chmod(file_path, 0o600)
                    else:
                        os.chmod(file_path, 0o644)

    except httpx.HTTPError as e:
        print_error(f"Failed to download certificates: {e}")
        sys.exit(1)

    # Save config
    config = {
        "domain": domain,
        "algorithm": algorithm,
        "cert_id": cert_id,
        "issued_at": datetime.utcnow().isoformat(),
        "expires_at": result.get("expires_at"),
        "cert_dir": str(domain_dir)
    }
    (domain_dir / "config.json").write_text(json.dumps(config, indent=2))

    # Clean up challenge file
    try:
        challenge_file.unlink()
    except:
        pass

    # Success!
    print()
    print(f"{Colors.GREEN}{'═' * 50}{Colors.END}")
    print_success(f"Certificate issued for {domain}!")
    print(f"{Colors.GREEN}{'═' * 50}{Colors.END}")
    print()
    print(f"📁 Certificate location: {Colors.BOLD}{domain_dir}{Colors.END}")
    print()
    print("   Files:")
    print(f"   • cert.pem      - Your certificate")
    print(f"   • key.pem       - Private key (keep secure!)")
    print(f"   • chain.pem     - Certificate chain")
    print(f"   • fullchain.pem - Full chain for nginx/apache")
    print()
    print(f"📅 Expires: {result.get('expires_at', 'N/A')}")
    print()
    print(f"{Colors.BLUE}Nginx config example:{Colors.END}")
    print(f"""
    ssl_certificate     {domain_dir}/fullchain.pem;
    ssl_certificate_key {domain_dir}/key.pem;
""")


def renew_certificates():
    """Renew all certificates"""
    print_banner()
    print_info("Checking certificates for renewal...")

    if not CERT_DIR.exists():
        print_warning("No certificates found")
        return

    for domain_dir in CERT_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        config_file = domain_dir / "config.json"
        if not config_file.exists():
            continue

        config = json.loads(config_file.read_text())
        domain = config.get("domain")

        # Check if renewal needed (30 days before expiry)
        expires_at = datetime.fromisoformat(config["expires_at"].replace("Z", ""))
        days_left = (expires_at - datetime.utcnow()).days

        if days_left <= 30:
            print_info(f"Renewing {domain} ({days_left} days left)")
            get_certificate(domain, config.get("algorithm", "hybrid"))
        else:
            print_success(f"{domain}: {days_left} days remaining")


def show_status():
    """Show status of all certificates"""
    print_banner()

    if not CERT_DIR.exists():
        print_warning("No certificates found")
        print_info(f"Get your first certificate: pqcert get yourdomain.com")
        return

    print(f"{'Domain':<30} {'Algorithm':<10} {'Expires':<20} {'Status'}")
    print("─" * 75)

    for domain_dir in CERT_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        config_file = domain_dir / "config.json"
        if not config_file.exists():
            continue

        config = json.loads(config_file.read_text())
        domain = config.get("domain", domain_dir.name)
        algorithm = config.get("algorithm", "unknown")
        expires_at = config.get("expires_at", "unknown")

        # Calculate status
        if expires_at != "unknown":
            exp_date = datetime.fromisoformat(expires_at.replace("Z", ""))
            days_left = (exp_date - datetime.utcnow()).days

            if days_left < 0:
                status = f"{Colors.RED}EXPIRED{Colors.END}"
            elif days_left <= 7:
                status = f"{Colors.RED}CRITICAL ({days_left}d){Colors.END}"
            elif days_left <= 30:
                status = f"{Colors.YELLOW}RENEW SOON ({days_left}d){Colors.END}"
            else:
                status = f"{Colors.GREEN}OK ({days_left}d){Colors.END}"
        else:
            status = "UNKNOWN"

        print(f"{domain:<30} {algorithm:<10} {expires_at[:10]:<20} {status}")


def main():
    parser = argparse.ArgumentParser(
        description="PQCert - Post-Quantum Certificates in Seconds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pqcert get example.com              Get a certificate
  pqcert get example.com -a ml-dsa    Get pure post-quantum cert
  pqcert renew                        Renew all certificates
  pqcert status                       Show certificate status

More info: https://pqcert.org/docs
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a new certificate")
    get_parser.add_argument("domain", help="Domain name (e.g., example.com)")
    get_parser.add_argument("-a", "--algorithm", default="hybrid",
                           choices=["hybrid", "ml-dsa", "rsa"],
                           help="Algorithm: hybrid (default), ml-dsa, or rsa")
    get_parser.add_argument("-e", "--email", help="Contact email (optional)")

    # Renew command
    subparsers.add_parser("renew", help="Renew certificates")

    # Status command
    subparsers.add_parser("status", help="Show certificate status")

    # Version
    parser.add_argument("-v", "--version", action="version", version="pqcert 1.0.0")

    args = parser.parse_args()

    if args.command == "get":
        get_certificate(args.domain, args.algorithm, args.email)
    elif args.command == "renew":
        renew_certificates()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
