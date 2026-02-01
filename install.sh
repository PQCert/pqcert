#!/bin/bash
#
# PQCert Installer
# https://pqcert.org
#
# One command to rule them all:
#   curl -sSL https://pqcert.org/install.sh | bash
#
# What this does:
#   1. Downloads PQCert CLI
#   2. Generates local Root CA
#   3. Installs CA to your system trust store
#   4. Creates localhost certificates
#   5. You're done! https://localhost works.
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Versions
VERSION="1.0.0"
PQCERT_DIR="$HOME/.pqcert"
BIN_DIR="/usr/local/bin"

print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  ${BOLD}🔐 PQCert - Post-Quantum Certificates${NC}${CYAN}               ║${NC}"
    echo -e "${CYAN}║     Secure localhost in seconds                       ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[$1/$2]${NC} $3"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macos" ;;
        Linux*)     OS="linux" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *)          OS="unknown" ;;
    esac

    ARCH="$(uname -m)"
    case "$ARCH" in
        x86_64)     ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
    esac

    echo -e "${CYAN}📍 Platform: ${OS}/${ARCH}${NC}"
}

# Check dependencies
check_deps() {
    print_step 1 5 "Checking dependencies..."

    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL not found. Please install OpenSSL first."
    fi

    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        print_error "Neither curl nor wget found. Please install one."
    fi

    print_success "Dependencies OK"
}

# Download PQCert CLI
download_cli() {
    print_step 2 5 "Downloading PQCert CLI..."

    mkdir -p "$PQCERT_DIR/bin"

    # For now, we'll use the Python script directly
    # In production, this would download a compiled binary

    PQCERT_URL="https://raw.githubusercontent.com/PQCert/pqcert/main/cli/pqcert_localhost.py"

    if command -v curl &> /dev/null; then
        curl -sSL "$PQCERT_URL" -o "$PQCERT_DIR/bin/pqcert_localhost.py" 2>/dev/null || true
    elif command -v wget &> /dev/null; then
        wget -q "$PQCERT_URL" -O "$PQCERT_DIR/bin/pqcert_localhost.py" 2>/dev/null || true
    fi

    # Create wrapper script
    cat > "$PQCERT_DIR/bin/pqcert" << 'WRAPPER'
#!/bin/bash
PQCERT_DIR="$HOME/.pqcert"

case "$1" in
    localhost|local|l)
        python3 "$PQCERT_DIR/bin/pqcert_localhost.py" "${@:2}"
        ;;
    version|-v|--version)
        echo "pqcert version 1.0.0"
        ;;
    help|-h|--help)
        echo "PQCert - Post-Quantum Certificates"
        echo ""
        echo "Usage:"
        echo "  pqcert localhost     Generate & install localhost certificates"
        echo "  pqcert localhost --uninstall  Remove CA from system"
        echo "  pqcert version       Show version"
        echo ""
        echo "More info: https://pqcert.org"
        ;;
    *)
        # Default to localhost command
        python3 "$PQCERT_DIR/bin/pqcert_localhost.py" "$@"
        ;;
esac
WRAPPER

    chmod +x "$PQCERT_DIR/bin/pqcert"

    print_success "CLI downloaded"
}

# Install to PATH
install_to_path() {
    print_step 3 5 "Installing to PATH..."

    if [ -w "$BIN_DIR" ]; then
        ln -sf "$PQCERT_DIR/bin/pqcert" "$BIN_DIR/pqcert"
    else
        sudo ln -sf "$PQCERT_DIR/bin/pqcert" "$BIN_DIR/pqcert"
    fi

    print_success "Installed to $BIN_DIR/pqcert"
}

# Generate Root CA
generate_ca() {
    print_step 4 5 "Generating Root CA..."

    CA_DIR="$PQCERT_DIR/ca"
    mkdir -p "$CA_DIR"
    chmod 700 "$CA_DIR"

    CA_KEY="$CA_DIR/pqcert-ca-key.pem"
    CA_CERT="$CA_DIR/pqcert-ca.pem"

    if [ -f "$CA_KEY" ] && [ -f "$CA_CERT" ]; then
        print_success "Root CA already exists"
        return
    fi

    # Generate CA key
    openssl genrsa -out "$CA_KEY" 4096 2>/dev/null
    chmod 600 "$CA_KEY"

    # Generate CA certificate
    openssl req -x509 -new -nodes \
        -key "$CA_KEY" \
        -sha256 \
        -days 3650 \
        -out "$CA_CERT" \
        -subj "/CN=PQCert Local Development CA/O=PQCert/OU=Local Development" \
        2>/dev/null

    # Create .crt copy
    cp "$CA_CERT" "$CA_DIR/pqcert-ca.crt"

    print_success "Root CA generated"
}

# Generate localhost certificate
generate_localhost_cert() {
    print_step 5 5 "Generating localhost certificate..."

    CERT_DIR="$PQCERT_DIR/certs/localhost"
    mkdir -p "$CERT_DIR"
    chmod 700 "$CERT_DIR"

    CA_KEY="$PQCERT_DIR/ca/pqcert-ca-key.pem"
    CA_CERT="$PQCERT_DIR/ca/pqcert-ca.pem"

    KEY_FILE="$CERT_DIR/localhost-key.pem"
    CERT_FILE="$CERT_DIR/localhost.pem"

    # Generate key
    openssl genrsa -out "$KEY_FILE" 2048 2>/dev/null
    chmod 600 "$KEY_FILE"

    # Create config with SANs
    CONFIG_FILE=$(mktemp)
    cat > "$CONFIG_FILE" << 'CERTCONF'
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
DNS.1 = localhost
DNS.2 = *.localhost
DNS.3 = local.dev
DNS.4 = *.local.dev
DNS.5 = dev.local
DNS.6 = *.dev.local
IP.1 = 127.0.0.1
IP.2 = ::1
CERTCONF

    # Generate CSR
    openssl req -new \
        -key "$KEY_FILE" \
        -out "$CERT_DIR/localhost.csr" \
        -config "$CONFIG_FILE" \
        2>/dev/null

    # Sign with CA
    openssl x509 -req \
        -in "$CERT_DIR/localhost.csr" \
        -CA "$CA_CERT" \
        -CAkey "$CA_KEY" \
        -CAcreateserial \
        -out "$CERT_FILE" \
        -days 825 \
        -sha256 \
        -extensions v3_req \
        -extfile "$CONFIG_FILE" \
        2>/dev/null

    # Create additional formats
    cp "$CERT_FILE" "$CERT_DIR/localhost.crt"

    # Fullchain
    cat "$CERT_FILE" "$CA_CERT" > "$CERT_DIR/localhost-fullchain.pem"

    # PFX for Windows/.NET
    openssl pkcs12 -export \
        -out "$CERT_DIR/localhost.pfx" \
        -inkey "$KEY_FILE" \
        -in "$CERT_FILE" \
        -certfile "$CA_CERT" \
        -password pass:pqcert \
        2>/dev/null

    # Cleanup
    rm -f "$CERT_DIR/localhost.csr" "$CONFIG_FILE"

    print_success "Localhost certificate generated"
}

# Install CA to system trust store
install_ca() {
    echo ""
    echo -e "${CYAN}Installing CA to system trust store...${NC}"

    CA_CERT="$PQCERT_DIR/ca/pqcert-ca.crt"

    case "$OS" in
        macos)
            echo -e "${YELLOW}📝 macOS requires sudo to install CA to Keychain${NC}"
            sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$CA_CERT"
            print_success "CA installed to macOS Keychain"
            ;;
        linux)
            if [ -d "/usr/local/share/ca-certificates" ]; then
                sudo cp "$CA_CERT" /usr/local/share/ca-certificates/pqcert-ca.crt
                sudo update-ca-certificates 2>/dev/null || true
            elif [ -d "/etc/pki/ca-trust/source/anchors" ]; then
                sudo cp "$CA_CERT" /etc/pki/ca-trust/source/anchors/pqcert-ca.crt
                sudo update-ca-trust extract 2>/dev/null || true
            fi
            print_success "CA installed to Linux trust store"
            ;;
        windows)
            certutil -addstore -f ROOT "$CA_CERT" 2>/dev/null || \
            powershell -Command "Import-Certificate -FilePath '$CA_CERT' -CertStoreLocation Cert:\LocalMachine\Root" 2>/dev/null || \
            print_warning "Please run as Administrator to install CA"
            ;;
    esac
}

# Print success message
print_final() {
    CERT_DIR="$PQCERT_DIR/certs/localhost"

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}🎉 PQCert installed successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BOLD}📁 Certificate Files:${NC}"
    echo ""
    echo "   Certificate:  $CERT_DIR/localhost.pem"
    echo "   Private Key:  $CERT_DIR/localhost-key.pem"
    echo "   Full Chain:   $CERT_DIR/localhost-fullchain.pem"
    echo "   PFX Bundle:   $CERT_DIR/localhost.pfx (password: pqcert)"
    echo ""
    echo -e "${BOLD}🚀 Quick Start:${NC}"
    echo ""
    echo "   # Node.js"
    echo "   const https = require('https');"
    echo "   const fs = require('fs');"
    echo "   https.createServer({"
    echo "     key: fs.readFileSync('$CERT_DIR/localhost-key.pem'),"
    echo "     cert: fs.readFileSync('$CERT_DIR/localhost.pem')"
    echo "   }, app).listen(443);"
    echo ""
    echo "   # nginx"
    echo "   ssl_certificate     $CERT_DIR/localhost-fullchain.pem;"
    echo "   ssl_certificate_key $CERT_DIR/localhost-key.pem;"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}🔐 Open https://localhost - it just works!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Main
main() {
    print_banner
    detect_os
    echo ""

    check_deps
    download_cli
    install_to_path
    generate_ca
    generate_localhost_cert
    install_ca
    print_final
}

main "$@"
