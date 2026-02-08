# Apache Guide

> Configure Apache with PQCert certificates

---

## Basic HTTPS Configuration

### /etc/apache2/sites-available/default-ssl.conf

```apache
<VirtualHost *:443>
    ServerName localhost
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    SSLHonorCipherOrder off

    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000"

    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

---

## HTTP to HTTPS Redirect

### /etc/apache2/sites-available/000-default.conf

```apache
<VirtualHost *:80>
    ServerName localhost

    # Redirect all HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>
```

---

## Enable Required Modules

```bash
# Enable SSL and required modules
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod headers
sudo a2enmod proxy
sudo a2enmod proxy_http

# Enable the SSL site
sudo a2ensite default-ssl

# Restart Apache
sudo systemctl restart apache2
```

---

## Reverse Proxy to Application

### Proxy to Node.js/Python app

```apache
<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    # Proxy to backend
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/

    # WebSocket support
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://127.0.0.1:3000/$1" [P,L]

    # Headers
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Real-IP %{REMOTE_ADDR}s
</VirtualHost>
```

---

## Multiple Virtual Hosts

```apache
# API on api.localhost
<VirtualHost *:443>
    ServerName api.localhost

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    ProxyPass / http://127.0.0.1:3001/
    ProxyPassReverse / http://127.0.0.1:3001/
</VirtualHost>

# App on app.localhost
<VirtualHost *:443>
    ServerName app.localhost

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/
</VirtualHost>
```

---

## PHP with Apache

### /etc/apache2/sites-available/php-ssl.conf

```apache
<VirtualHost *:443>
    ServerName localhost
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>

    # PHP-FPM
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/var/run/php/php8.2-fpm.sock|fcgi://localhost"
    </FilesMatch>

    # Or mod_php
    # <FilesMatch \.php$>
    #     SetHandler application/x-httpd-php
    # </FilesMatch>
</VirtualHost>
```

---

## Load Balancing

```apache
<Proxy "balancer://mycluster">
    BalancerMember "http://127.0.0.1:3001"
    BalancerMember "http://127.0.0.1:3002"
    BalancerMember "http://127.0.0.1:3003"
    ProxySet lbmethod=byrequests
</Proxy>

<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    ProxyPass / balancer://mycluster/
    ProxyPassReverse / balancer://mycluster/
</VirtualHost>
```

---

## SSL Best Practices

```apache
<VirtualHost *:443>
    ServerName localhost

    # SSL Engine
    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    # Protocols - TLS 1.2 and 1.3 only
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

    # Modern ciphers
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off

    # HSTS (2 years)
    Header always set Strict-Transport-Security "max-age=63072000"

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"

    # OCSP Stapling (not applicable for local certs)
    # SSLUseStapling on
    # SSLStaplingCache "shmcb:logs/stapling-cache(150000)"

    DocumentRoot /var/www/html
</VirtualHost>
```

---

## Docker with Apache

### Dockerfile

```dockerfile
FROM httpd:2.4-alpine

# Copy configuration
COPY httpd-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf

# Enable SSL module
RUN sed -i \
    -e 's/^#\(LoadModule ssl_module\)/\1/' \
    -e 's/^#\(LoadModule socache_shmcb_module\)/\1/' \
    -e 's/^#\(Include conf\/extra\/httpd-ssl.conf\)/\1/' \
    /usr/local/apache2/conf/httpd.conf

EXPOSE 80 443
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  apache:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/usr/local/apache2/certs:ro
      - ./html:/usr/local/apache2/htdocs:ro
```

### httpd-ssl.conf

```apache
Listen 443

SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
SSLHonorCipherOrder off

<VirtualHost *:443>
    DocumentRoot "/usr/local/apache2/htdocs"
    ServerName localhost

    SSLEngine on
    SSLCertificateFile "/usr/local/apache2/certs/localhost.pem"
    SSLCertificateKeyFile "/usr/local/apache2/certs/localhost-key.pem"
</VirtualHost>
```

---

## Environment Variables

### Using envsubst

```apache
# /etc/apache2/sites-available/ssl.conf.template
<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile ${PQCERT_DIR}/certs/localhost/localhost.pem
    SSLCertificateKeyFile ${PQCERT_DIR}/certs/localhost/localhost-key.pem

    DocumentRoot /var/www/html
</VirtualHost>
```

```bash
# Generate config
export PQCERT_DIR=$HOME/.pqcert
envsubst < /etc/apache2/sites-available/ssl.conf.template > /etc/apache2/sites-available/ssl.conf
```

---

## Test Configuration

```bash
# Test Apache config
sudo apachectl configtest

# Reload Apache
sudo systemctl reload apache2

# Check SSL certificate
openssl s_client -connect localhost:443 -servername localhost
```

---

## Troubleshooting

### Permission denied

```bash
# Make sure Apache can read the certificates
sudo chmod 644 ~/.pqcert/certs/localhost/*.pem
sudo chmod 600 ~/.pqcert/certs/localhost/*-key.pem
sudo chown www-data:www-data ~/.pqcert/certs/localhost/*.pem
```

### Certificate not trusted

The CA must be installed on the **client** machine:

```bash
# On the machine accessing the site
make install-ca
```

### AH02572: Failed to configure certificate

Make sure the certificate and key files are in the correct format (PEM).

---

## Next Steps

- [Docker Guide](./docker.md) - Containerize with Apache
- [Nginx Guide](./nginx.md) - Alternative: Nginx configuration
- [Kubernetes Guide](./kubernetes.md) - K8s ingress
