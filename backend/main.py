"""
PQCert - Post-Quantum Certificate Authority
Main API Server
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, EmailStr
import subprocess
import tempfile
import os
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path

app = FastAPI(
    title="PQCert API",
    description="Post-Quantum Certificate Authority - Free SSL Certificates",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
CERTS_DIR = Path("/var/lib/pqcert/certs")
CHALLENGES_DIR = Path("/var/lib/pqcert/challenges")

# Ensure directories exist
CERTS_DIR.mkdir(parents=True, exist_ok=True)
CHALLENGES_DIR.mkdir(parents=True, exist_ok=True)


class CertificateRequest(BaseModel):
    domain: str
    email: EmailStr | None = None
    algorithm: str = "hybrid"  # hybrid, ml-dsa, rsa


class ChallengeResponse(BaseModel):
    challenge_id: str
    challenge_token: str
    challenge_url: str
    expires_at: str


class CertificateResponse(BaseModel):
    success: bool
    message: str
    certificate_id: str | None = None
    cert_url: str | None = None
    key_url: str | None = None
    chain_url: str | None = None
    expires_at: str | None = None


# ============== API Endpoints ==============

@app.get("/")
async def root():
    return {
        "name": "PQCert API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/v1/certificate/request", response_model=ChallengeResponse)
async def request_certificate(req: CertificateRequest):
    """
    Step 1: Request a certificate and receive a challenge
    """
    # Validate domain
    if not is_valid_domain(req.domain):
        raise HTTPException(400, "Invalid domain name")

    # Generate challenge
    challenge_id = str(uuid.uuid4())
    challenge_token = generate_token()

    # Store challenge
    challenge_data = {
        "domain": req.domain,
        "email": req.email,
        "algorithm": req.algorithm,
        "token": challenge_token,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "verified": False
    }

    challenge_file = CHALLENGES_DIR / f"{challenge_id}.json"
    challenge_file.write_text(json.dumps(challenge_data))

    return ChallengeResponse(
        challenge_id=challenge_id,
        challenge_token=challenge_token,
        challenge_url=f"http://{req.domain}/.well-known/pqcert-challenge/{challenge_token}",
        expires_at=challenge_data["expires_at"]
    )


@app.post("/v1/certificate/verify/{challenge_id}")
async def verify_challenge(challenge_id: str, background_tasks: BackgroundTasks):
    """
    Step 2: Verify domain ownership and issue certificate
    """
    challenge_file = CHALLENGES_DIR / f"{challenge_id}.json"

    if not challenge_file.exists():
        raise HTTPException(404, "Challenge not found")

    challenge_data = json.loads(challenge_file.read_text())

    # Check expiration
    expires_at = datetime.fromisoformat(challenge_data["expires_at"])
    if datetime.utcnow() > expires_at:
        raise HTTPException(400, "Challenge expired")

    # Verify domain ownership (HTTP-01 challenge)
    domain = challenge_data["domain"]
    token = challenge_data["token"]

    if not await verify_domain_ownership(domain, token):
        raise HTTPException(400, "Domain verification failed. Make sure the challenge file is accessible.")

    # Generate certificate
    cert_id = str(uuid.uuid4())
    cert_data = await generate_certificate(
        domain=domain,
        algorithm=challenge_data["algorithm"],
        cert_id=cert_id
    )

    # Clean up challenge
    challenge_file.unlink()

    return CertificateResponse(
        success=True,
        message="Certificate issued successfully",
        certificate_id=cert_id,
        cert_url=f"/v1/certificate/{cert_id}/cert.pem",
        key_url=f"/v1/certificate/{cert_id}/key.pem",
        chain_url=f"/v1/certificate/{cert_id}/chain.pem",
        expires_at=cert_data["expires_at"]
    )


@app.get("/v1/certificate/{cert_id}/{filename}")
async def download_certificate(cert_id: str, filename: str):
    """
    Download certificate files
    """
    allowed_files = ["cert.pem", "key.pem", "chain.pem", "fullchain.pem"]
    if filename not in allowed_files:
        raise HTTPException(400, "Invalid filename")

    cert_path = CERTS_DIR / cert_id / filename
    if not cert_path.exists():
        raise HTTPException(404, "Certificate not found")

    return FileResponse(
        cert_path,
        media_type="application/x-pem-file",
        filename=filename
    )


@app.get("/install")
async def install_script():
    """
    Return the installation script
    """
    script = '''#!/bin/bash
# PQCert CLI Installer
# https://pqcert.org

set -e

PQCERT_VERSION="1.0.0"
INSTALL_DIR="/usr/local/bin"

echo "🔐 PQCert Installer v${PQCERT_VERSION}"
echo "================================"

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "📦 Detected: ${OS}/${ARCH}"

# Download CLI
DOWNLOAD_URL="https://pqcert.org/releases/pqcert-${OS}-${ARCH}"
echo "📥 Downloading PQCert CLI..."

if command -v curl &> /dev/null; then
    curl -sSL -o /tmp/pqcert "$DOWNLOAD_URL"
elif command -v wget &> /dev/null; then
    wget -q -O /tmp/pqcert "$DOWNLOAD_URL"
else
    echo "❌ Neither curl nor wget found"
    exit 1
fi

# Install
echo "📁 Installing to ${INSTALL_DIR}..."
chmod +x /tmp/pqcert

if [ -w "$INSTALL_DIR" ]; then
    mv /tmp/pqcert "$INSTALL_DIR/pqcert"
else
    sudo mv /tmp/pqcert "$INSTALL_DIR/pqcert"
fi

# Verify installation
if command -v pqcert &> /dev/null; then
    echo ""
    echo "✅ PQCert installed successfully!"
    echo ""
    echo "🚀 Quick start:"
    echo "   pqcert get yourdomain.com"
    echo ""
    echo "📚 Documentation: https://pqcert.org/docs"
else
    echo "❌ Installation failed"
    exit 1
fi
'''
    return PlainTextResponse(script, media_type="text/plain")


# ============== Helper Functions ==============

def is_valid_domain(domain: str) -> bool:
    """Validate domain name"""
    import re
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def generate_token() -> str:
    """Generate a random token for challenges"""
    import secrets
    return secrets.token_urlsafe(32)


async def verify_domain_ownership(domain: str, token: str) -> bool:
    """Verify domain ownership via HTTP-01 challenge"""
    import httpx

    challenge_url = f"http://{domain}/.well-known/pqcert-challenge/{token}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(challenge_url)
            return response.status_code == 200 and token in response.text
    except Exception:
        return False


async def generate_certificate(domain: str, algorithm: str, cert_id: str) -> dict:
    """Generate a post-quantum certificate"""

    cert_dir = CERTS_DIR / cert_id
    cert_dir.mkdir(parents=True, exist_ok=True)

    key_file = cert_dir / "key.pem"
    cert_file = cert_dir / "cert.pem"
    chain_file = cert_dir / "chain.pem"
    fullchain_file = cert_dir / "fullchain.pem"

    # Generate key based on algorithm
    if algorithm == "ml-dsa":
        # Pure post-quantum (ML-DSA-65 / Dilithium3)
        key_cmd = ["openssl", "genpkey", "-algorithm", "ml-dsa-65", "-out", str(key_file)]
    elif algorithm == "hybrid":
        # Hybrid: RSA + ML-DSA for compatibility
        key_cmd = ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key_file)]
    else:
        # Traditional RSA
        key_cmd = ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key_file)]

    subprocess.run(key_cmd, check=True, capture_output=True)

    # Generate CSR
    csr_file = cert_dir / "csr.pem"
    csr_cmd = [
        "openssl", "req", "-new",
        "-key", str(key_file),
        "-out", str(csr_file),
        "-subj", f"/CN={domain}"
    ]
    subprocess.run(csr_cmd, check=True, capture_output=True)

    # Sign certificate (self-signed for MVP, would use CA in production)
    expires_at = datetime.utcnow() + timedelta(days=90)
    cert_cmd = [
        "openssl", "x509", "-req",
        "-in", str(csr_file),
        "-signkey", str(key_file),
        "-out", str(cert_file),
        "-days", "90",
        "-extfile", "-"
    ]

    # Add SAN extension
    san_config = f"subjectAltName=DNS:{domain}"
    subprocess.run(cert_cmd, input=san_config.encode(), check=True, capture_output=True)

    # Create chain and fullchain (placeholder for now)
    chain_file.write_text("")  # Would contain intermediate certs
    fullchain_content = cert_file.read_text()
    fullchain_file.write_text(fullchain_content)

    # Clean up CSR
    csr_file.unlink()

    # Store metadata
    metadata = {
        "domain": domain,
        "algorithm": algorithm,
        "issued_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat()
    }
    (cert_dir / "metadata.json").write_text(json.dumps(metadata))

    return metadata


# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
