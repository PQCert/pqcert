# ╔═══════════════════════════════════════════════════════════════╗
# ║  PQCert - Post-Quantum Certificates                           ║
# ║  https://pqcert.org                                           ║
# ╚═══════════════════════════════════════════════════════════════╝

.PHONY: help install localhost test clean dev docker k8s deploy all

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m
BOLD := \033[1m

# Paths
PQCERT_DIR := $(HOME)/.pqcert
CERT_DIR := $(PQCERT_DIR)/certs/localhost
CA_DIR := $(PQCERT_DIR)/ca
PROJECT_DIR := $(shell pwd)

# ══════════════════════════════════════════════════════════════════
# HELP
# ══════════════════════════════════════════════════════════════════

help: ## Show this help
	@echo ""
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  $(BOLD)🔐 PQCert - Post-Quantum Certificates$(NC)$(CYAN)                        ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)Usage:$(NC) make $(CYAN)<target>$(NC)"
	@echo ""
	@echo "$(BOLD)🚀 Quick Start:$(NC)"
	@echo "  $(CYAN)make localhost$(NC)     Generate & install localhost certificates"
	@echo "  $(CYAN)make test$(NC)          Start test HTTPS server"
	@echo ""
	@echo "$(BOLD)📦 Development:$(NC)"
	@echo "  $(CYAN)make dev$(NC)           Start development environment"
	@echo "  $(CYAN)make docker$(NC)        Build Docker images"
	@echo "  $(CYAN)make k8s$(NC)           Deploy to Kubernetes (kind)"
	@echo ""
	@echo "$(BOLD)🔧 Maintenance:$(NC)"
	@echo "  $(CYAN)make clean$(NC)         Remove all generated certificates"
	@echo "  $(CYAN)make uninstall$(NC)     Remove CA from system trust store"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ══════════════════════════════════════════════════════════════════
# LOCALHOST CERTIFICATES
# ══════════════════════════════════════════════════════════════════

localhost: ## Generate localhost certificates and install CA
	@echo "$(CYAN)🔐 PQCert - Generating localhost certificates...$(NC)"
	@python3 $(PROJECT_DIR)/cli/pqcert_localhost.py --no-install
	@echo ""
	@echo "$(YELLOW)📝 To install CA to system (requires sudo):$(NC)"
	@echo "   make install-ca"

install-ca: ## Install CA to macOS Keychain (requires sudo)
	@echo "$(CYAN)🔐 Installing CA to system trust store...$(NC)"
ifeq ($(shell uname),Darwin)
	@sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $(CA_DIR)/pqcert-ca.pem
	@echo "$(GREEN)✅ CA installed to macOS Keychain$(NC)"
else ifeq ($(shell uname),Linux)
	@sudo cp $(CA_DIR)/pqcert-ca.crt /usr/local/share/ca-certificates/ 2>/dev/null || \
		sudo cp $(CA_DIR)/pqcert-ca.crt /etc/pki/ca-trust/source/anchors/
	@sudo update-ca-certificates 2>/dev/null || sudo update-ca-trust extract
	@echo "$(GREEN)✅ CA installed to Linux trust store$(NC)"
endif

uninstall-ca: ## Remove CA from system trust store
	@echo "$(YELLOW)🗑️  Removing CA from system...$(NC)"
ifeq ($(shell uname),Darwin)
	@sudo security delete-certificate -c "PQCert Local Development CA" /Library/Keychains/System.keychain 2>/dev/null || true
	@echo "$(GREEN)✅ CA removed from macOS Keychain$(NC)"
else ifeq ($(shell uname),Linux)
	@sudo rm -f /usr/local/share/ca-certificates/pqcert-ca.crt 2>/dev/null || true
	@sudo rm -f /etc/pki/ca-trust/source/anchors/pqcert-ca.crt 2>/dev/null || true
	@sudo update-ca-certificates 2>/dev/null || sudo update-ca-trust extract 2>/dev/null || true
	@echo "$(GREEN)✅ CA removed from Linux trust store$(NC)"
endif

generate-ca: ## Generate Root CA only
	@echo "$(CYAN)🔐 Generating Root CA...$(NC)"
	@mkdir -p $(CA_DIR)
	@chmod 700 $(CA_DIR)
	@openssl genrsa -out $(CA_DIR)/pqcert-ca-key.pem 4096
	@chmod 600 $(CA_DIR)/pqcert-ca-key.pem
	@openssl req -x509 -new -nodes \
		-key $(CA_DIR)/pqcert-ca-key.pem \
		-sha256 -days 3650 \
		-out $(CA_DIR)/pqcert-ca.pem \
		-subj "/CN=PQCert Local Development CA/O=PQCert/OU=Local Development/C=US"
	@cp $(CA_DIR)/pqcert-ca.pem $(CA_DIR)/pqcert-ca.crt
	@echo "$(GREEN)✅ Root CA generated at $(CA_DIR)$(NC)"

generate-cert: ## Generate localhost certificate (requires CA)
	@echo "$(CYAN)🔐 Generating localhost certificate...$(NC)"
	@mkdir -p $(CERT_DIR)
	@chmod 700 $(CERT_DIR)
	@openssl genrsa -out $(CERT_DIR)/localhost-key.pem 2048
	@chmod 600 $(CERT_DIR)/localhost-key.pem
	@openssl req -new \
		-key $(CERT_DIR)/localhost-key.pem \
		-out $(CERT_DIR)/localhost.csr \
		-subj "/CN=localhost/O=PQCert/OU=Local Development" \
		-addext "subjectAltName=DNS:localhost,DNS:*.localhost,DNS:local.dev,DNS:*.local.dev,IP:127.0.0.1,IP:::1"
	@openssl x509 -req \
		-in $(CERT_DIR)/localhost.csr \
		-CA $(CA_DIR)/pqcert-ca.pem \
		-CAkey $(CA_DIR)/pqcert-ca-key.pem \
		-CAcreateserial \
		-out $(CERT_DIR)/localhost.pem \
		-days 825 -sha256 \
		-copy_extensions copyall
	@cp $(CERT_DIR)/localhost.pem $(CERT_DIR)/localhost.crt
	@cat $(CERT_DIR)/localhost.pem $(CA_DIR)/pqcert-ca.pem > $(CERT_DIR)/localhost-fullchain.pem
	@openssl pkcs12 -export \
		-out $(CERT_DIR)/localhost.pfx \
		-inkey $(CERT_DIR)/localhost-key.pem \
		-in $(CERT_DIR)/localhost.pem \
		-certfile $(CA_DIR)/pqcert-ca.pem \
		-password pass:pqcert
	@rm -f $(CERT_DIR)/localhost.csr
	@echo "$(GREEN)✅ Certificates generated at $(CERT_DIR)$(NC)"

# ══════════════════════════════════════════════════════════════════
# TESTING
# ══════════════════════════════════════════════════════════════════

test: ## Start HTTPS test server on localhost:8443
	@echo "$(CYAN)🧪 Starting HTTPS test server...$(NC)"
	@echo "$(GREEN)🌐 Open: https://localhost:8443$(NC)"
	@python3 $(PROJECT_DIR)/test-server.py

test-cert: ## Verify certificate details
	@echo "$(CYAN)📋 Certificate Details:$(NC)"
	@echo ""
	@openssl x509 -in $(CERT_DIR)/localhost.pem -text -noout | head -20
	@echo ""
	@echo "$(CYAN)📋 Subject Alternative Names:$(NC)"
	@openssl x509 -in $(CERT_DIR)/localhost.pem -text -noout | grep -A1 "Subject Alternative Name"

test-curl: ## Test HTTPS connection with curl
	@echo "$(CYAN)🧪 Testing HTTPS with curl...$(NC)"
	@curl -v --cacert $(CA_DIR)/pqcert-ca.pem https://localhost:8443 2>&1 | head -30

# ══════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ══════════════════════════════════════════════════════════════════

dev: ## Start development environment
	@echo "$(CYAN)🚀 Starting development environment...$(NC)"
	@echo ""
	@echo "$(BOLD)Frontend:$(NC) http://localhost:3000"
	@echo "$(BOLD)API:$(NC)      http://localhost:8000"
	@echo "$(BOLD)Docs:$(NC)     http://localhost:8000/docs"
	@echo ""
	@cd $(PROJECT_DIR)/backend && pip install -r requirements.txt -q
	@cd $(PROJECT_DIR)/backend && uvicorn main:app --reload --port 8000 &
	@cd $(PROJECT_DIR)/frontend && python3 -m http.server 3000

dev-api: ## Start API server only
	@echo "$(CYAN)🚀 Starting API server...$(NC)"
	@cd $(PROJECT_DIR)/backend && pip install -r requirements.txt -q
	@cd $(PROJECT_DIR)/backend && uvicorn main:app --reload --port 8000

dev-frontend: ## Start frontend server only
	@echo "$(CYAN)🚀 Starting frontend server...$(NC)"
	@echo "$(GREEN)🌐 Open: http://localhost:3000$(NC)"
	@cd $(PROJECT_DIR)/frontend && python3 -m http.server 3000

# ══════════════════════════════════════════════════════════════════
# DOCKER
# ══════════════════════════════════════════════════════════════════

docker: docker-build docker-up ## Build and start Docker containers

docker-build: ## Build Docker images
	@echo "$(CYAN)🐳 Building Docker images...$(NC)"
	@docker-compose build

docker-up: ## Start Docker containers
	@echo "$(CYAN)🐳 Starting Docker containers...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Services running:$(NC)"
	@echo "   Frontend: http://localhost:80"
	@echo "   API:      http://localhost:8000"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)🐳 Stopping Docker containers...$(NC)"
	@docker-compose down

docker-logs: ## View Docker logs
	@docker-compose logs -f

# ══════════════════════════════════════════════════════════════════
# KUBERNETES
# ══════════════════════════════════════════════════════════════════

k8s: k8s-deploy k8s-forward ## Deploy to Kubernetes and port-forward

k8s-deploy: ## Deploy to Kubernetes
	@echo "$(CYAN)☸️  Deploying to Kubernetes...$(NC)"
	@kubectl apply -f $(PROJECT_DIR)/k8s/namespace.yaml
	@kubectl -n pqcert create configmap pqcert-api-code \
		--from-file=main.py=$(PROJECT_DIR)/backend/main.py \
		--dry-run=client -o yaml | kubectl apply -f -
	@kubectl -n pqcert create configmap pqcert-frontend-html \
		--from-file=index.html=$(PROJECT_DIR)/frontend/index.html \
		--from-file=style.css=$(PROJECT_DIR)/frontend/style.css \
		--dry-run=client -o yaml | kubectl apply -f -
	@kubectl apply -f $(PROJECT_DIR)/k8s/
	@echo "$(GREEN)✅ Deployed to namespace: pqcert$(NC)"

k8s-forward: ## Port-forward Kubernetes services
	@echo "$(CYAN)☸️  Port-forwarding services...$(NC)"
	@kubectl -n pqcert port-forward svc/pqcert-frontend 8080:80 &
	@kubectl -n pqcert port-forward svc/pqcert-api 8000:8000 &
	@echo "$(GREEN)✅ Services available:$(NC)"
	@echo "   Frontend: http://localhost:8080"
	@echo "   API:      http://localhost:8000"

k8s-status: ## Show Kubernetes deployment status
	@echo "$(CYAN)☸️  Kubernetes Status:$(NC)"
	@kubectl -n pqcert get pods,svc

k8s-delete: ## Delete Kubernetes deployment
	@echo "$(YELLOW)☸️  Deleting Kubernetes deployment...$(NC)"
	@kubectl delete namespace pqcert --ignore-not-found

# ══════════════════════════════════════════════════════════════════
# CLEANUP
# ══════════════════════════════════════════════════════════════════

clean: ## Remove all generated certificates
	@echo "$(YELLOW)🗑️  Cleaning up certificates...$(NC)"
	@rm -rf $(PQCERT_DIR)
	@echo "$(GREEN)✅ Certificates removed$(NC)"

clean-all: clean uninstall-ca ## Remove certificates and uninstall CA
	@echo "$(GREEN)✅ Full cleanup complete$(NC)"

# ══════════════════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════════════════

release: ## Build release binaries
	@echo "$(CYAN)📦 Building release...$(NC)"
	@mkdir -p $(PROJECT_DIR)/dist
	@echo "TODO: Build Go/Rust binary"

# ══════════════════════════════════════════════════════════════════
# INFO
# ══════════════════════════════════════════════════════════════════

info: ## Show certificate locations
	@echo ""
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  $(BOLD)📁 PQCert File Locations$(NC)$(CYAN)                                     ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)Root CA:$(NC)"
	@echo "  Certificate: $(CA_DIR)/pqcert-ca.pem"
	@echo "  Private Key: $(CA_DIR)/pqcert-ca-key.pem"
	@echo ""
	@echo "$(BOLD)Localhost Certificate:$(NC)"
	@echo "  Certificate: $(CERT_DIR)/localhost.pem"
	@echo "  Private Key: $(CERT_DIR)/localhost-key.pem"
	@echo "  Full Chain:  $(CERT_DIR)/localhost-fullchain.pem"
	@echo "  PFX Bundle:  $(CERT_DIR)/localhost.pfx (password: pqcert)"
	@echo ""

version: ## Show version
	@echo "PQCert v1.0.0"
