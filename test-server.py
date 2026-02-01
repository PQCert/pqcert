#!/usr/bin/env python3
"""
Quick test server for PQCert localhost certificates
Run: python3 test-server.py
Open: https://localhost:8443
"""

import http.server
import ssl
import os
from pathlib import Path

CERT_DIR = Path.home() / ".pqcert" / "certs" / "localhost"

html = """
<!DOCTYPE html>
<html>
<head>
    <title>PQCert - It Works!</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 { font-size: 3rem; margin-bottom: 10px; }
        .icon { font-size: 5rem; margin-bottom: 20px; }
        .success { color: #22c55e; }
        .info { color: #94a3b8; margin-top: 20px; }
        code {
            background: rgba(0,0,0,0.3);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔐</div>
        <h1 class="success">It Works!</h1>
        <p>Your localhost SSL certificate is working perfectly.</p>
        <p class="info">
            Powered by <strong>PQCert</strong><br>
            <code>https://localhost:8443</code>
        </p>
    </div>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        print(f"[HTTPS] {args[0]}")

def main():
    cert_file = CERT_DIR / "localhost.pem"
    key_file = CERT_DIR / "localhost-key.pem"

    if not cert_file.exists():
        print("❌ Certificate not found. Run: python3 cli/pqcert_localhost.py")
        return

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)

    server = http.server.HTTPServer(('localhost', 8443), Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)

    print()
    print("🔐 PQCert Test Server")
    print("=" * 40)
    print(f"🌐 Open: https://localhost:8443")
    print("=" * 40)
    print("Press Ctrl+C to stop")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
