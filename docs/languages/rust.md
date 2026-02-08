# Rust Guide

> Use PQCert certificates with Rust applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```rust
use std::path::PathBuf;

fn pqcert_dir() -> PathBuf {
    dirs::home_dir()
        .expect("Could not find home directory")
        .join(".pqcert")
}

fn cert_dir() -> PathBuf {
    pqcert_dir().join("certs").join("localhost")
}

fn ca_dir() -> PathBuf {
    pqcert_dir().join("ca")
}

// Certificate files
fn cert_file() -> PathBuf { cert_dir().join("localhost.pem") }
fn key_file() -> PathBuf { cert_dir().join("localhost-key.pem") }
fn ca_file() -> PathBuf { ca_dir().join("pqcert-ca.pem") }
```

---

## Actix Web

### Cargo.toml

```toml
[dependencies]
actix-web = "4"
rustls = "0.21"
rustls-pemfile = "1"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### main.rs

```rust
use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use rustls::{Certificate, PrivateKey, ServerConfig};
use rustls_pemfile::{certs, pkcs8_private_keys};
use std::fs::File;
use std::io::BufReader;
use std::path::PathBuf;
use serde::Serialize;

#[derive(Serialize)]
struct Response {
    message: String,
    secure: bool,
}

async fn index() -> impl Responder {
    HttpResponse::Ok().json(Response {
        message: "Hello from Actix Web HTTPS!".to_string(),
        secure: true,
    })
}

async fn status() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "ok",
        "https": true
    }))
}

fn load_rustls_config() -> ServerConfig {
    let home = dirs::home_dir().expect("Could not find home directory");
    let cert_path = home.join(".pqcert/certs/localhost/localhost.pem");
    let key_path = home.join(".pqcert/certs/localhost/localhost-key.pem");

    // Load certificate
    let cert_file = File::open(&cert_path)
        .expect(&format!("Cannot open {:?}", cert_path));
    let mut cert_reader = BufReader::new(cert_file);
    let certs: Vec<Certificate> = certs(&mut cert_reader)
        .expect("Failed to parse certificate")
        .into_iter()
        .map(Certificate)
        .collect();

    // Load private key
    let key_file = File::open(&key_path)
        .expect(&format!("Cannot open {:?}", key_path));
    let mut key_reader = BufReader::new(key_file);
    let keys: Vec<PrivateKey> = pkcs8_private_keys(&mut key_reader)
        .expect("Failed to parse private key")
        .into_iter()
        .map(PrivateKey)
        .collect();

    let key = keys.into_iter().next().expect("No private key found");

    ServerConfig::builder()
        .with_safe_defaults()
        .with_no_client_auth()
        .with_single_cert(certs, key)
        .expect("Failed to create TLS config")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let config = load_rustls_config();

    println!("🔐 HTTPS server running at https://localhost:443");

    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(index))
            .route("/api/status", web::get().to(status))
    })
    .bind_rustls("0.0.0.0:443", config)?
    .run()
    .await
}
```

---

## Axum

### Cargo.toml

```toml
[dependencies]
axum = "0.7"
axum-server = { version = "0.6", features = ["tls-rustls"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower = "0.4"
```

### main.rs

```rust
use axum::{routing::get, Router, Json};
use axum_server::tls_rustls::RustlsConfig;
use serde::Serialize;
use std::net::SocketAddr;

#[derive(Serialize)]
struct Response {
    message: String,
    secure: bool,
}

async fn index() -> Json<Response> {
    Json(Response {
        message: "Hello from Axum HTTPS!".to_string(),
        secure: true,
    })
}

async fn status() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "https": true
    }))
}

#[tokio::main]
async fn main() {
    let home = dirs::home_dir().expect("Could not find home directory");
    let cert_path = home.join(".pqcert/certs/localhost/localhost.pem");
    let key_path = home.join(".pqcert/certs/localhost/localhost-key.pem");

    let config = RustlsConfig::from_pem_file(cert_path, key_path)
        .await
        .expect("Failed to load TLS config");

    let app = Router::new()
        .route("/", get(index))
        .route("/api/status", get(status));

    let addr = SocketAddr::from(([0, 0, 0, 0], 443));
    println!("🔐 HTTPS server running at https://localhost:443");

    axum_server::bind_rustls(addr, config)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
```

---

## Rocket

### Cargo.toml

```toml
[dependencies]
rocket = { version = "0.5", features = ["json"] }
serde = { version = "1", features = ["derive"] }
```

### Rocket.toml

```toml
[default.tls]
certs = "${HOME}/.pqcert/certs/localhost/localhost.pem"
key = "${HOME}/.pqcert/certs/localhost/localhost-key.pem"

[default]
port = 443
address = "0.0.0.0"
```

### main.rs

```rust
#[macro_use] extern crate rocket;

use rocket::serde::json::Json;
use serde::Serialize;

#[derive(Serialize)]
struct Response {
    message: String,
    secure: bool,
}

#[get("/")]
fn index() -> Json<Response> {
    Json(Response {
        message: "Hello from Rocket HTTPS!".to_string(),
        secure: true,
    })
}

#[get("/api/status")]
fn status() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "https": true
    }))
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .mount("/", routes![index, status])
}
```

---

## Warp

### Cargo.toml

```toml
[dependencies]
warp = { version = "0.3", features = ["tls"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### main.rs

```rust
use warp::Filter;
use serde::Serialize;

#[derive(Serialize)]
struct Response {
    message: String,
    secure: bool,
}

#[tokio::main]
async fn main() {
    let home = dirs::home_dir().expect("Could not find home directory");
    let cert_path = home.join(".pqcert/certs/localhost/localhost.pem");
    let key_path = home.join(".pqcert/certs/localhost/localhost-key.pem");

    let index = warp::path::end()
        .map(|| {
            warp::reply::json(&Response {
                message: "Hello from Warp HTTPS!".to_string(),
                secure: true,
            })
        });

    let status = warp::path!("api" / "status")
        .map(|| {
            warp::reply::json(&serde_json::json!({
                "status": "ok",
                "https": true
            }))
        });

    let routes = index.or(status);

    println!("🔐 HTTPS server running at https://localhost:443");

    warp::serve(routes)
        .tls()
        .cert_path(&cert_path)
        .key_path(&key_path)
        .run(([0, 0, 0, 0], 443))
        .await;
}
```

---

## Hyper (Low-level)

### Cargo.toml

```toml
[dependencies]
hyper = { version = "1", features = ["full"] }
hyper-util = { version = "0.1", features = ["full"] }
tokio = { version = "1", features = ["full"] }
tokio-rustls = "0.25"
rustls = "0.22"
rustls-pemfile = "2"
http-body-util = "0.1"
```

### main.rs

```rust
use hyper::{Request, Response, body::Incoming, service::service_fn};
use hyper_util::rt::TokioIo;
use http_body_util::Full;
use hyper::body::Bytes;
use std::convert::Infallible;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio_rustls::TlsAcceptor;
use tokio_rustls::rustls::{self, pki_types::PrivateKeyDer};

async fn handle(_req: Request<Incoming>) -> Result<Response<Full<Bytes>>, Infallible> {
    let body = r#"{"message": "Hello from Hyper HTTPS!", "secure": true}"#;
    Ok(Response::builder()
        .header("Content-Type", "application/json")
        .body(Full::new(Bytes::from(body)))
        .unwrap())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    let cert_path = home.join(".pqcert/certs/localhost/localhost.pem");
    let key_path = home.join(".pqcert/certs/localhost/localhost-key.pem");

    // Load certificates
    let certs = rustls_pemfile::certs(&mut std::io::BufReader::new(
        std::fs::File::open(&cert_path)?
    )).collect::<Result<Vec<_>, _>>()?;

    let key = rustls_pemfile::private_key(&mut std::io::BufReader::new(
        std::fs::File::open(&key_path)?
    ))?.expect("No private key found");

    let config = rustls::ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, key)?;

    let acceptor = TlsAcceptor::from(Arc::new(config));
    let addr = SocketAddr::from(([0, 0, 0, 0], 443));
    let listener = TcpListener::bind(addr).await?;

    println!("🔐 HTTPS server running at https://localhost:443");

    loop {
        let (stream, _) = listener.accept().await?;
        let acceptor = acceptor.clone();

        tokio::spawn(async move {
            if let Ok(stream) = acceptor.accept(stream).await {
                let io = TokioIo::new(stream);
                let _ = hyper_util::server::conn::auto::Builder::new(
                    hyper_util::rt::TokioExecutor::new()
                )
                .serve_connection(io, service_fn(handle))
                .await;
            }
        });
    }
}
```

---

## HTTPS Client with reqwest

### Cargo.toml

```toml
[dependencies]
reqwest = { version = "0.11", features = ["json", "rustls-tls"] }
tokio = { version = "1", features = ["full"] }
```

### main.rs

```rust
use reqwest::Certificate;
use std::fs;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    let ca_path = home.join(".pqcert/ca/pqcert-ca.pem");

    // Load CA certificate
    let ca_cert = fs::read(&ca_path)?;
    let ca = Certificate::from_pem(&ca_cert)?;

    // Create client with custom CA
    let client = reqwest::Client::builder()
        .add_root_certificate(ca)
        .build()?;

    let response = client
        .get("https://localhost:443")
        .send()
        .await?
        .text()
        .await?;

    println!("Response: {}", response);
    Ok(())
}
```

---

## mTLS Client

```rust
use reqwest::{Certificate, Identity};
use std::fs;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    let ca_path = home.join(".pqcert/ca/pqcert-ca.pem");
    let cert_path = home.join(".pqcert/certs/localhost/localhost.pem");
    let key_path = home.join(".pqcert/certs/localhost/localhost-key.pem");

    // Load CA
    let ca_cert = fs::read(&ca_path)?;
    let ca = Certificate::from_pem(&ca_cert)?;

    // Load client certificate and key
    let cert = fs::read_to_string(&cert_path)?;
    let key = fs::read_to_string(&key_path)?;
    let identity = Identity::from_pem(format!("{}{}", cert, key).as_bytes())?;

    // Create mTLS client
    let client = reqwest::Client::builder()
        .add_root_certificate(ca)
        .identity(identity)
        .build()?;

    let response = client
        .get("https://secure-service.localhost/api")
        .send()
        .await?
        .text()
        .await?;

    println!("Response: {}", response);
    Ok(())
}
```

---

## gRPC with Tonic

### Cargo.toml

```toml
[dependencies]
tonic = { version = "0.10", features = ["tls"] }
prost = "0.12"
tokio = { version = "1", features = ["full"] }

[build-dependencies]
tonic-build = "0.10"
```

### Server

```rust
use tonic::transport::{Server, Identity, ServerTlsConfig};
use std::fs;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    let cert = fs::read_to_string(home.join(".pqcert/certs/localhost/localhost.pem"))?;
    let key = fs::read_to_string(home.join(".pqcert/certs/localhost/localhost-key.pem"))?;

    let identity = Identity::from_pem(cert, key);
    let tls = ServerTlsConfig::new().identity(identity);

    println!("🔐 gRPC server running on https://localhost:50051");

    Server::builder()
        .tls_config(tls)?
        // .add_service(YourServiceServer::new(YourService::default()))
        .serve("[::]:50051".parse()?)
        .await?;

    Ok(())
}
```

### Client

```rust
use tonic::transport::{Channel, ClientTlsConfig, Certificate};
use std::fs;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    let ca = fs::read_to_string(home.join(".pqcert/ca/pqcert-ca.pem"))?;

    let tls = ClientTlsConfig::new()
        .ca_certificate(Certificate::from_pem(&ca))
        .domain_name("localhost");

    let channel = Channel::from_static("https://localhost:50051")
        .tls_config(tls)?
        .connect()
        .await?;

    // let client = YourServiceClient::new(channel);
    Ok(())
}
```

---

## WebSocket with tokio-tungstenite

### Server

```rust
use tokio::net::TcpListener;
use tokio_tungstenite::accept_async;
use tokio_rustls::TlsAcceptor;
use futures_util::{StreamExt, SinkExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = dirs::home_dir().expect("Could not find home directory");
    // ... load TLS config as shown above ...

    let listener = TcpListener::bind("0.0.0.0:443").await?;
    let acceptor = TlsAcceptor::from(Arc::new(config));

    println!("🔐 WebSocket server running at wss://localhost:443");

    while let Ok((stream, _)) = listener.accept().await {
        let acceptor = acceptor.clone();

        tokio::spawn(async move {
            if let Ok(tls_stream) = acceptor.accept(stream).await {
                if let Ok(ws_stream) = accept_async(tls_stream).await {
                    let (mut write, mut read) = ws_stream.split();

                    while let Some(Ok(msg)) = read.next().await {
                        if msg.is_text() || msg.is_binary() {
                            let _ = write.send(msg).await;
                        }
                    }
                }
            }
        });
    }

    Ok(())
}
```

---

## PQCert Helper Module

### pqcert.rs

```rust
use std::path::PathBuf;
use std::fs;
use rustls::{Certificate, PrivateKey, RootCertStore};
use rustls_pemfile::{certs, pkcs8_private_keys};
use std::io::BufReader;

pub struct PQCert {
    home: PathBuf,
}

impl PQCert {
    pub fn new() -> Self {
        let home = dirs::home_dir().expect("Could not find home directory");
        Self { home }
    }

    pub fn pqcert_dir(&self) -> PathBuf {
        self.home.join(".pqcert")
    }

    pub fn cert_dir(&self) -> PathBuf {
        self.pqcert_dir().join("certs").join("localhost")
    }

    pub fn ca_dir(&self) -> PathBuf {
        self.pqcert_dir().join("ca")
    }

    pub fn cert_file(&self) -> PathBuf {
        self.cert_dir().join("localhost.pem")
    }

    pub fn key_file(&self) -> PathBuf {
        self.cert_dir().join("localhost-key.pem")
    }

    pub fn ca_file(&self) -> PathBuf {
        self.ca_dir().join("pqcert-ca.pem")
    }

    pub fn exists(&self) -> bool {
        self.cert_file().exists() && self.key_file().exists()
    }

    pub fn load_certs(&self) -> Vec<Certificate> {
        let file = fs::File::open(self.cert_file()).expect("Cannot open cert file");
        let mut reader = BufReader::new(file);
        certs(&mut reader)
            .expect("Failed to parse certs")
            .into_iter()
            .map(Certificate)
            .collect()
    }

    pub fn load_key(&self) -> PrivateKey {
        let file = fs::File::open(self.key_file()).expect("Cannot open key file");
        let mut reader = BufReader::new(file);
        let keys: Vec<PrivateKey> = pkcs8_private_keys(&mut reader)
            .expect("Failed to parse key")
            .into_iter()
            .map(PrivateKey)
            .collect();
        keys.into_iter().next().expect("No key found")
    }

    pub fn load_ca_store(&self) -> RootCertStore {
        let file = fs::File::open(self.ca_file()).expect("Cannot open CA file");
        let mut reader = BufReader::new(file);
        let certs = certs(&mut reader).expect("Failed to parse CA");

        let mut store = RootCertStore::empty();
        for cert in certs {
            store.add(&Certificate(cert)).expect("Failed to add CA");
        }
        store
    }
}

impl Default for PQCert {
    fn default() -> Self {
        Self::new()
    }
}
```

---

## Troubleshooting

### Certificate not trusted

Add CA to system store or use custom root store in your client.

### Permission denied for port 443

Use port 8443 or run with elevated privileges:

```rust
.run(([0, 0, 0, 0], 8443))
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize Rust apps
- [Kubernetes Guide](../guides/kubernetes.md) - Deploy to K8s
- [Nginx Guide](../guides/nginx.md) - Reverse proxy
