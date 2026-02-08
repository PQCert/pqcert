# PHP Guide

> Use PQCert certificates with PHP applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```php
<?php

class PQCertPaths {
    public static function home(): string {
        return getenv('HOME') ?: posix_getpwuid(posix_getuid())['dir'];
    }

    public static function pqcertDir(): string {
        return self::home() . '/.pqcert';
    }

    public static function certDir(): string {
        return self::pqcertDir() . '/certs/localhost';
    }

    public static function caDir(): string {
        return self::pqcertDir() . '/ca';
    }

    public static function certFile(): string {
        return self::certDir() . '/localhost.pem';
    }

    public static function keyFile(): string {
        return self::certDir() . '/localhost-key.pem';
    }

    public static function caFile(): string {
        return self::caDir() . '/pqcert-ca.pem';
    }
}
```

---

## PHP Built-in Server (Development)

PHP's built-in server doesn't support HTTPS directly. Use a reverse proxy or one of the frameworks below.

```bash
# Start with nginx as HTTPS proxy
php -S localhost:8080 &
# nginx handles HTTPS on port 443 and proxies to 8080
```

---

## Laravel

### Configure in .env

```env
APP_URL=https://localhost
```

### config/app.php

```php
<?php

return [
    'url' => env('APP_URL', 'https://localhost'),
    // ...
];
```

### Use with Laravel Valet

```bash
# Valet uses its own certificates, but you can configure PQCert
valet secure --cert ~/.pqcert/certs/localhost/localhost.pem \
              --key ~/.pqcert/certs/localhost/localhost-key.pem
```

### Use with Laravel Sail (Docker)

```yaml
# docker-compose.yml
services:
  laravel.test:
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/etc/ssl/certs/pqcert:ro
    environment:
      - SSL_CERTIFICATE=/etc/ssl/certs/pqcert/localhost.pem
      - SSL_CERTIFICATE_KEY=/etc/ssl/certs/pqcert/localhost-key.pem
```

### HTTP Client with Custom CA

```php
<?php

use Illuminate\Support\Facades\Http;

// Configure HTTP client to trust PQCert CA
$response = Http::withOptions([
    'verify' => getenv('HOME') . '/.pqcert/ca/pqcert-ca.pem',
])->get('https://localhost:443/api/data');

return $response->json();
```

---

## Symfony

### Configure in .env

```env
APP_URL=https://localhost
```

### Symfony HTTP Client

```php
<?php

use Symfony\Component\HttpClient\HttpClient;

$client = HttpClient::create([
    'cafile' => getenv('HOME') . '/.pqcert/ca/pqcert-ca.pem',
]);

$response = $client->request('GET', 'https://localhost:443/api/data');
$data = $response->toArray();
```

### Using with Symfony Local Server

```bash
# Symfony CLI can use custom certificates
symfony server:ca:install
symfony local:server:start --tls-cert-file=~/.pqcert/certs/localhost/localhost.pem \
                           --tls-key-file=~/.pqcert/certs/localhost/localhost-key.pem
```

---

## Slim Framework

### index.php (with ReactPHP)

```php
<?php

require __DIR__ . '/vendor/autoload.php';

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;
use React\Http\HttpServer;
use React\Socket\SocketServer;
use React\Socket\SecureServer;

// Create Slim app
$app = AppFactory::create();

$app->get('/', function (Request $request, Response $response) {
    $response->getBody()->write(json_encode([
        'message' => 'Hello from Slim HTTPS!',
        'secure' => true
    ]));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/api/status', function (Request $request, Response $response) {
    $response->getBody()->write(json_encode([
        'status' => 'ok',
        'https' => true
    ]));
    return $response->withHeader('Content-Type', 'application/json');
});

// ReactPHP HTTPS server
$home = getenv('HOME');

$loop = React\EventLoop\Loop::get();

$socket = new SocketServer('0.0.0.0:443', [], $loop);
$secureSocket = new SecureServer($socket, $loop, [
    'local_cert' => $home . '/.pqcert/certs/localhost/localhost.pem',
    'local_pk' => $home . '/.pqcert/certs/localhost/localhost-key.pem',
]);

$http = new HttpServer(function ($request) use ($app) {
    // Bridge to Slim
    return $app->handle($request);
});

$http->listen($secureSocket);

echo "🔐 HTTPS server running at https://localhost:443\n";

$loop->run();
```

---

## Swoole

### server.php

```php
<?php

use Swoole\Http\Server;
use Swoole\Http\Request;
use Swoole\Http\Response;

$home = getenv('HOME');

$server = new Server('0.0.0.0', 443, SWOOLE_PROCESS, SWOOLE_SOCK_TCP | SWOOLE_SSL);

$server->set([
    'ssl_cert_file' => $home . '/.pqcert/certs/localhost/localhost.pem',
    'ssl_key_file' => $home . '/.pqcert/certs/localhost/localhost-key.pem',
]);

$server->on('request', function (Request $request, Response $response) {
    $response->header('Content-Type', 'application/json');

    $path = $request->server['request_uri'];

    if ($path === '/') {
        $response->end(json_encode([
            'message' => 'Hello from Swoole HTTPS!',
            'secure' => true
        ]));
    } elseif ($path === '/api/status') {
        $response->end(json_encode([
            'status' => 'ok',
            'https' => true
        ]));
    } else {
        $response->status(404);
        $response->end(json_encode(['error' => 'Not found']));
    }
});

echo "🔐 HTTPS server running at https://localhost:443\n";
$server->start();
```

---

## RoadRunner

### .rr.yaml

```yaml
version: "3"

server:
  command: "php worker.php"

http:
  address: 0.0.0.0:443
  ssl:
    address: 0.0.0.0:443
    cert: "${HOME}/.pqcert/certs/localhost/localhost.pem"
    key: "${HOME}/.pqcert/certs/localhost/localhost-key.pem"
```

### worker.php

```php
<?php

use Spiral\RoadRunner\Http\PSR7Worker;
use Spiral\RoadRunner\Worker;
use Nyholm\Psr7\Factory\Psr17Factory;
use Nyholm\Psr7\Response;

require __DIR__ . '/vendor/autoload.php';

$worker = Worker::create();
$factory = new Psr17Factory();
$psr7 = new PSR7Worker($worker, $factory, $factory, $factory);

while ($request = $psr7->waitRequest()) {
    try {
        $path = $request->getUri()->getPath();

        if ($path === '/') {
            $body = json_encode([
                'message' => 'Hello from RoadRunner HTTPS!',
                'secure' => true
            ]);
        } elseif ($path === '/api/status') {
            $body = json_encode(['status' => 'ok', 'https' => true]);
        } else {
            $psr7->respond(new Response(404));
            continue;
        }

        $response = new Response(200, ['Content-Type' => 'application/json'], $body);
        $psr7->respond($response);
    } catch (\Throwable $e) {
        $psr7->respond(new Response(500, [], $e->getMessage()));
    }
}
```

---

## Guzzle HTTP Client

### Basic Request

```php
<?php

require __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;

$home = getenv('HOME');

$client = new Client([
    'verify' => $home . '/.pqcert/ca/pqcert-ca.pem',
]);

$response = $client->get('https://localhost:443/api/data');

echo $response->getBody();
```

### With Client Certificate (mTLS)

```php
<?php

use GuzzleHttp\Client;

$home = getenv('HOME');
$certDir = $home . '/.pqcert/certs/localhost';

$client = new Client([
    'verify' => $home . '/.pqcert/ca/pqcert-ca.pem',
    'cert' => $certDir . '/localhost.pem',
    'ssl_key' => $certDir . '/localhost-key.pem',
]);

$response = $client->get('https://secure-service.localhost/api');

echo $response->getBody();
```

---

## cURL

### Basic HTTPS Request

```php
<?php

$home = getenv('HOME');

$ch = curl_init('https://localhost:443/api/data');

curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CAINFO => $home . '/.pqcert/ca/pqcert-ca.pem',
]);

$response = curl_exec($ch);

if (curl_errno($ch)) {
    echo 'Error: ' . curl_error($ch);
} else {
    echo $response;
}

curl_close($ch);
```

### With Client Certificate (mTLS)

```php
<?php

$home = getenv('HOME');
$certDir = $home . '/.pqcert/certs/localhost';

$ch = curl_init('https://secure-service.localhost/api');

curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CAINFO => $home . '/.pqcert/ca/pqcert-ca.pem',
    CURLOPT_SSLCERT => $certDir . '/localhost.pem',
    CURLOPT_SSLKEY => $certDir . '/localhost-key.pem',
]);

$response = curl_exec($ch);
curl_close($ch);
```

---

## file_get_contents with SSL

```php
<?php

$home = getenv('HOME');

$context = stream_context_create([
    'ssl' => [
        'cafile' => $home . '/.pqcert/ca/pqcert-ca.pem',
        'verify_peer' => true,
        'verify_peer_name' => true,
    ],
]);

$response = file_get_contents('https://localhost:443/api/data', false, $context);

echo $response;
```

---

## Apache Configuration

### httpd-ssl.conf

```apache
<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile /home/user/.pqcert/certs/localhost/localhost.pem
    SSLCertificateKeyFile /home/user/.pqcert/certs/localhost/localhost-key.pem

    DocumentRoot /var/www/html

    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>

    # PHP-FPM
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/var/run/php/php8.2-fpm.sock|fcgi://localhost"
    </FilesMatch>
</VirtualHost>
```

---

## Nginx + PHP-FPM

### nginx.conf

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /home/user/.pqcert/certs/localhost/localhost.pem;
    ssl_certificate_key /home/user/.pqcert/certs/localhost/localhost-key.pem;

    root /var/www/html;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

---

## Docker with PHP

### Dockerfile

```dockerfile
FROM php:8.2-fpm-alpine

# Install extensions
RUN docker-php-ext-install pdo pdo_mysql

WORKDIR /var/www/html

COPY . .

EXPOSE 9000
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ${HOME}/.pqcert/certs/localhost:/etc/nginx/certs:ro
      - .:/var/www/html:ro
    depends_on:
      - php

  php:
    build: .
    volumes:
      - .:/var/www/html
```

### nginx.conf (for Docker)

```nginx
server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/localhost.pem;
    ssl_certificate_key /etc/nginx/certs/localhost-key.pem;

    root /var/www/html/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

---

## PQCert Helper Class

```php
<?php

class PQCert
{
    private string $home;
    private string $pqcertDir;

    public function __construct()
    {
        $this->home = getenv('HOME') ?: posix_getpwuid(posix_getuid())['dir'];
        $this->pqcertDir = $this->home . '/.pqcert';
    }

    public function certDir(): string
    {
        return $this->pqcertDir . '/certs/localhost';
    }

    public function caDir(): string
    {
        return $this->pqcertDir . '/ca';
    }

    public function certFile(): string
    {
        return $this->certDir() . '/localhost.pem';
    }

    public function keyFile(): string
    {
        return $this->certDir() . '/localhost-key.pem';
    }

    public function caFile(): string
    {
        return $this->caDir() . '/pqcert-ca.pem';
    }

    public function exists(): bool
    {
        return file_exists($this->certFile()) && file_exists($this->caFile());
    }

    public function getGuzzleOptions(): array
    {
        return [
            'verify' => $this->caFile(),
        ];
    }

    public function getMtlsGuzzleOptions(): array
    {
        return [
            'verify' => $this->caFile(),
            'cert' => $this->certFile(),
            'ssl_key' => $this->keyFile(),
        ];
    }

    public function getStreamContext(): resource
    {
        return stream_context_create([
            'ssl' => [
                'cafile' => $this->caFile(),
                'verify_peer' => true,
                'verify_peer_name' => true,
            ],
        ]);
    }
}
```

---

## Troubleshooting

### SSL certificate problem

```php
// Trust PQCert CA
curl_setopt($ch, CURLOPT_CAINFO, getenv('HOME') . '/.pqcert/ca/pqcert-ca.pem');
```

### Permission denied for port 443

Use port 8443 or run PHP-FPM behind nginx/Apache.

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize PHP apps
- [Nginx Guide](../guides/nginx.md) - Nginx + PHP-FPM
- [Apache Guide](../guides/apache.md) - Apache + PHP
