# Ruby Guide

> Use PQCert certificates with Ruby applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```ruby
module PQCertPaths
  HOME = ENV['HOME']
  PQCERT_DIR = File.join(HOME, '.pqcert')
  CERT_DIR = File.join(PQCERT_DIR, 'certs', 'localhost')
  CA_DIR = File.join(PQCERT_DIR, 'ca')

  CERT_FILE = File.join(CERT_DIR, 'localhost.pem')
  KEY_FILE = File.join(CERT_DIR, 'localhost-key.pem')
  CA_FILE = File.join(CA_DIR, 'pqcert-ca.pem')
end
```

---

## Ruby on Rails

### Configure SSL in config/puma.rb

```ruby
# config/puma.rb

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

if ENV['RAILS_ENV'] == 'development'
  ssl_bind '0.0.0.0', '443', {
    cert: File.join(cert_dir, 'localhost.pem'),
    key: File.join(cert_dir, 'localhost-key.pem'),
    verify_mode: 'none'
  }
else
  bind "tcp://0.0.0.0:#{ENV.fetch('PORT', 3000)}"
end
```

### Run with SSL

```bash
rails server -b 'ssl://0.0.0.0:443?key=~/.pqcert/certs/localhost/localhost-key.pem&cert=~/.pqcert/certs/localhost/localhost.pem'
```

### HTTP Client with Custom CA

```ruby
# app/services/secure_http_client.rb

require 'net/http'
require 'openssl'

class SecureHttpClient
  def initialize
    @ca_file = File.join(ENV['HOME'], '.pqcert', 'ca', 'pqcert-ca.pem')
  end

  def get(url)
    uri = URI.parse(url)

    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.ca_file = @ca_file
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER

    request = Net::HTTP::Get.new(uri.request_uri)
    response = http.request(request)

    response.body
  end
end

# Usage
client = SecureHttpClient.new
data = client.get('https://localhost:443/api/data')
```

---

## Sinatra

### app.rb

```ruby
require 'sinatra'
require 'sinatra/json'
require 'webrick'
require 'webrick/https'
require 'openssl'

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

get '/' do
  json message: 'Hello from Sinatra HTTPS!', secure: true
end

get '/api/status' do
  json status: 'ok', https: true
end

# Configure WEBrick with SSL
webrick_options = {
  Port: 443,
  SSLEnable: true,
  SSLCertificate: OpenSSL::X509::Certificate.new(File.read(File.join(cert_dir, 'localhost.pem'))),
  SSLPrivateKey: OpenSSL::PKey::RSA.new(File.read(File.join(cert_dir, 'localhost-key.pem')))
}

Rack::Handler::WEBrick.run Sinatra::Application, **webrick_options
```

### With Puma

```ruby
# config.ru
require './app'

run Sinatra::Application
```

```ruby
# puma.rb
home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

ssl_bind '0.0.0.0', '443', {
  cert: File.join(cert_dir, 'localhost.pem'),
  key: File.join(cert_dir, 'localhost-key.pem')
}
```

---

## Grape API

### config.ru

```ruby
require 'grape'
require 'rack'
require 'webrick'
require 'webrick/https'
require 'openssl'

class API < Grape::API
  format :json

  get '/' do
    { message: 'Hello from Grape HTTPS!', secure: true }
  end

  namespace :api do
    get :status do
      { status: 'ok', https: true }
    end
  end
end

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

webrick_options = {
  Port: 443,
  SSLEnable: true,
  SSLCertificate: OpenSSL::X509::Certificate.new(File.read(File.join(cert_dir, 'localhost.pem'))),
  SSLPrivateKey: OpenSSL::PKey::RSA.new(File.read(File.join(cert_dir, 'localhost-key.pem')))
}

Rack::Handler::WEBrick.run API, **webrick_options
```

---

## Roda

### app.rb

```ruby
require 'roda'
require 'json'

class App < Roda
  plugin :json

  route do |r|
    r.root do
      { message: 'Hello from Roda HTTPS!', secure: true }
    end

    r.on 'api' do
      r.get 'status' do
        { status: 'ok', https: true }
      end
    end
  end
end

# config.ru
require './app'

run App
```

### puma.rb

```ruby
home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

ssl_bind '0.0.0.0', '443', {
  cert: File.join(cert_dir, 'localhost.pem'),
  key: File.join(cert_dir, 'localhost-key.pem')
}
```

---

## Hanami

### config/puma.rb

```ruby
home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

if Hanami.env?(:development)
  ssl_bind '0.0.0.0', '443', {
    cert: File.join(cert_dir, 'localhost.pem'),
    key: File.join(cert_dir, 'localhost-key.pem')
  }
end
```

---

## Net::HTTP Client

### Basic HTTPS Request

```ruby
require 'net/http'
require 'openssl'
require 'json'

home = ENV['HOME']
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

uri = URI.parse('https://localhost:443/api/data')

http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true
http.ca_file = ca_file
http.verify_mode = OpenSSL::SSL::VERIFY_PEER

request = Net::HTTP::Get.new(uri.request_uri)
response = http.request(request)

data = JSON.parse(response.body)
puts data
```

### mTLS Client

```ruby
require 'net/http'
require 'openssl'

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

uri = URI.parse('https://secure-service.localhost/api')

http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

# CA certificate
http.ca_file = ca_file
http.verify_mode = OpenSSL::SSL::VERIFY_PEER

# Client certificate
http.cert = OpenSSL::X509::Certificate.new(File.read(File.join(cert_dir, 'localhost.pem')))
http.key = OpenSSL::PKey::RSA.new(File.read(File.join(cert_dir, 'localhost-key.pem')))

request = Net::HTTP::Get.new(uri.request_uri)
response = http.request(request)

puts response.body
```

---

## Faraday

### Basic Usage

```ruby
require 'faraday'

home = ENV['HOME']
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

conn = Faraday.new(url: 'https://localhost:443') do |faraday|
  faraday.ssl.ca_file = ca_file
  faraday.adapter Faraday.default_adapter
end

response = conn.get('/api/data')
puts response.body
```

### With Client Certificate (mTLS)

```ruby
require 'faraday'
require 'openssl'

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

conn = Faraday.new(url: 'https://secure-service.localhost') do |faraday|
  faraday.ssl.ca_file = ca_file
  faraday.ssl.client_cert = OpenSSL::X509::Certificate.new(File.read(File.join(cert_dir, 'localhost.pem')))
  faraday.ssl.client_key = OpenSSL::PKey::RSA.new(File.read(File.join(cert_dir, 'localhost-key.pem')))
  faraday.adapter Faraday.default_adapter
end

response = conn.get('/api')
puts response.body
```

---

## HTTParty

```ruby
require 'httparty'

home = ENV['HOME']

class SecureAPI
  include HTTParty
  base_uri 'https://localhost:443'

  def initialize
    ca_file = File.join(ENV['HOME'], '.pqcert', 'ca', 'pqcert-ca.pem')
    self.class.default_options.merge!(ssl_ca_file: ca_file)
  end

  def status
    self.class.get('/api/status')
  end
end

api = SecureAPI.new
response = api.status
puts response.parsed_response
```

---

## RestClient

```ruby
require 'rest-client'

home = ENV['HOME']
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

response = RestClient::Request.execute(
  method: :get,
  url: 'https://localhost:443/api/data',
  ssl_ca_file: ca_file
)

puts response.body
```

---

## WebSocket (faye-websocket)

### Server

```ruby
require 'faye/websocket'
require 'eventmachine'
require 'rack'

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

App = lambda do |env|
  if Faye::WebSocket.websocket?(env)
    ws = Faye::WebSocket.new(env)

    ws.on :message do |event|
      ws.send(event.data)
    end

    ws.on :close do |event|
      puts "Connection closed: #{event.code}"
    end

    ws.rack_response
  else
    [200, { 'Content-Type' => 'text/plain' }, ['Hello']]
  end
end

EM.run do
  Rack::Handler::Thin.run App, {
    Host: '0.0.0.0',
    Port: 443,
    ssl: true,
    ssl_options: {
      private_key_file: File.join(cert_dir, 'localhost-key.pem'),
      cert_chain_file: File.join(cert_dir, 'localhost.pem')
    }
  }
end
```

### Client

```ruby
require 'faye/websocket'
require 'eventmachine'

home = ENV['HOME']
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

EM.run do
  ws = Faye::WebSocket::Client.new('wss://localhost:443/ws', nil, {
    tls: { ca_file: ca_file }
  })

  ws.on :open do |event|
    puts 'Connected!'
    ws.send('Hello Server!')
  end

  ws.on :message do |event|
    puts "Received: #{event.data}"
  end

  ws.on :close do |event|
    puts "Closed: #{event.code}"
    EM.stop
  end
end
```

---

## gRPC

### Server

```ruby
require 'grpc'

home = ENV['HOME']
cert_dir = File.join(home, '.pqcert', 'certs', 'localhost')

credentials = GRPC::Core::ServerCredentials.new(
  nil, # Root certs (optional for server)
  [{
    private_key: File.read(File.join(cert_dir, 'localhost-key.pem')),
    cert_chain: File.read(File.join(cert_dir, 'localhost.pem'))
  }],
  false # Don't require client certs
)

server = GRPC::RpcServer.new
server.add_http2_port('0.0.0.0:50051', credentials)
# server.handle(YourServiceImpl.new)

puts '🔐 gRPC server running on https://localhost:50051'
server.run_till_terminated
```

### Client

```ruby
require 'grpc'

home = ENV['HOME']
ca_file = File.join(home, '.pqcert', 'ca', 'pqcert-ca.pem')

credentials = GRPC::Core::ChannelCredentials.new(
  File.read(ca_file)
)

# stub = YourService::Stub.new('localhost:50051', credentials)
```

---

## PQCert Helper Module

```ruby
# lib/pqcert.rb

require 'openssl'
require 'net/http'

module PQCert
  class << self
    def home
      ENV['HOME']
    end

    def pqcert_dir
      File.join(home, '.pqcert')
    end

    def cert_dir
      File.join(pqcert_dir, 'certs', 'localhost')
    end

    def ca_dir
      File.join(pqcert_dir, 'ca')
    end

    def cert_file
      File.join(cert_dir, 'localhost.pem')
    end

    def key_file
      File.join(cert_dir, 'localhost-key.pem')
    end

    def ca_file
      File.join(ca_dir, 'pqcert-ca.pem')
    end

    def exists?
      File.exist?(cert_file) && File.exist?(ca_file)
    end

    def load_cert
      OpenSSL::X509::Certificate.new(File.read(cert_file))
    end

    def load_key
      OpenSSL::PKey::RSA.new(File.read(key_file))
    end

    def load_ca
      OpenSSL::X509::Certificate.new(File.read(ca_file))
    end

    def configure_http(http)
      http.use_ssl = true
      http.ca_file = ca_file
      http.verify_mode = OpenSSL::SSL::VERIFY_PEER
      http
    end

    def configure_mtls_http(http)
      configure_http(http)
      http.cert = load_cert
      http.key = load_key
      http
    end

    def ssl_options
      {
        cert: cert_file,
        key: key_file
      }
    end

    def puma_ssl_bind(host = '0.0.0.0', port = 443)
      {
        cert: cert_file,
        key: key_file
      }
    end
  end
end

# Usage example
# require 'pqcert'
#
# if PQCert.exists?
#   uri = URI.parse('https://localhost:443')
#   http = Net::HTTP.new(uri.host, uri.port)
#   PQCert.configure_http(http)
#   response = http.get('/')
# end
```

---

## Docker Configuration

### Dockerfile

```dockerfile
FROM ruby:3.2-alpine

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE 443
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "443:443"
    volumes:
      - ${HOME}/.pqcert/certs/localhost:/certs:ro
    environment:
      - PQCERT_DIR=/certs
```

---

## Troubleshooting

### SSL_connect returned=1 errno=0 (certificate verify failed)

```ruby
# Trust PQCert CA
http.ca_file = File.join(ENV['HOME'], '.pqcert', 'ca', 'pqcert-ca.pem')
```

### Permission denied for port 443

Use port 8443 or run with sudo:

```ruby
ssl_bind '0.0.0.0', '8443', { ... }
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize Ruby apps
- [Nginx Guide](../guides/nginx.md) - Nginx reverse proxy
- [Kubernetes Guide](../guides/kubernetes.md) - Deploy to K8s
