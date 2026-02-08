# Go Guide

> Use PQCert certificates with Go applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```go
package main

import (
    "os"
    "path/filepath"
)

func getCertPaths() (certFile, keyFile, caFile string) {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")
    caDir := filepath.Join(home, ".pqcert", "ca")

    return filepath.Join(certDir, "localhost.pem"),
           filepath.Join(certDir, "localhost-key.pem"),
           filepath.Join(caDir, "pqcert-ca.pem")
}
```

---

## net/http HTTPS Server

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, `{"message": "Hello from Go HTTPS!"}`)
    })

    fmt.Println("🔐 HTTPS server running at https://localhost:443")
    log.Fatal(http.ListenAndServeTLS(":443", certFile, keyFile, nil))
}
```

---

## Gin

```go
package main

import (
    "os"
    "path/filepath"

    "github.com/gin-gonic/gin"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    r := gin.Default()

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello from Gin HTTPS!"})
    })

    r.GET("/api/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(200, gin.H{"id": id, "secure": true})
    })

    r.RunTLS(":443", certFile, keyFile)
}
```

---

## Echo

```go
package main

import (
    "net/http"
    "os"
    "path/filepath"

    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    e := echo.New()
    e.Use(middleware.Logger())

    e.GET("/", func(c echo.Context) error {
        return c.JSON(http.StatusOK, map[string]interface{}{
            "message": "Hello from Echo HTTPS!",
        })
    })

    e.Logger.Fatal(e.StartTLS(":443", certFile, keyFile))
}
```

---

## Fiber

```go
package main

import (
    "log"
    "os"
    "path/filepath"

    "github.com/gofiber/fiber/v2"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    app := fiber.New()

    app.Get("/", func(c *fiber.Ctx) error {
        return c.JSON(fiber.Map{"message": "Hello from Fiber HTTPS!"})
    })

    log.Fatal(app.ListenTLS(":443", certFile, keyFile))
}
```

---

## Chi

```go
package main

import (
    "encoding/json"
    "net/http"
    "os"
    "path/filepath"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    r := chi.NewRouter()
    r.Use(middleware.Logger)

    r.Get("/", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]interface{}{
            "message": "Hello from Chi HTTPS!",
        })
    })

    http.ListenAndServeTLS(":443", certFile, keyFile, r)
}
```

---

## HTTPS Client

### Basic Request

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "io"
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    caFile := filepath.Join(home, ".pqcert", "ca", "pqcert-ca.pem")

    // Load CA certificate
    caCert, err := os.ReadFile(caFile)
    if err != nil {
        panic(err)
    }

    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // Create HTTPS client with custom CA
    client := &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{
                RootCAs: caCertPool,
            },
        },
    }

    // Make request
    resp, err := client.Get("https://localhost:443")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

### mTLS Client (Mutual TLS)

```go
package main

import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "io"
    "net/http"
    "os"
    "path/filepath"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")
    caFile := filepath.Join(home, ".pqcert", "ca", "pqcert-ca.pem")

    // Load CA
    caCert, _ := os.ReadFile(caFile)
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // Load client certificate
    cert, err := tls.LoadX509KeyPair(
        filepath.Join(certDir, "localhost.pem"),
        filepath.Join(certDir, "localhost-key.pem"),
    )
    if err != nil {
        panic(err)
    }

    // Create mTLS client
    client := &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{
                RootCAs:      caCertPool,
                Certificates: []tls.Certificate{cert},
            },
        },
    }

    resp, _ := client.Get("https://secure-service.localhost/api")
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

---

## gRPC with TLS

### Server

```go
package main

import (
    "log"
    "net"
    "os"
    "path/filepath"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    certFile := filepath.Join(certDir, "localhost.pem")
    keyFile := filepath.Join(certDir, "localhost-key.pem")

    // Load TLS credentials
    creds, err := credentials.NewServerTLSFromFile(certFile, keyFile)
    if err != nil {
        log.Fatalf("Failed to load TLS: %v", err)
    }

    // Create gRPC server
    server := grpc.NewServer(grpc.Creds(creds))

    // Register your service
    // pb.RegisterYourServiceServer(server, &yourServer{})

    lis, _ := net.Listen("tcp", ":443")
    log.Println("🔐 gRPC server running on port 443")
    server.Serve(lis)
}
```

### Client

```go
package main

import (
    "log"
    "os"
    "path/filepath"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

func main() {
    home, _ := os.UserHomeDir()
    caFile := filepath.Join(home, ".pqcert", "ca", "pqcert-ca.pem")

    // Load TLS credentials
    creds, err := credentials.NewClientTLSFromFile(caFile, "localhost")
    if err != nil {
        log.Fatalf("Failed to load TLS: %v", err)
    }

    // Connect
    conn, err := grpc.Dial("localhost:443", grpc.WithTransportCredentials(creds))
    if err != nil {
        log.Fatalf("Failed to connect: %v", err)
    }
    defer conn.Close()

    // Use your client
    // client := pb.NewYourServiceClient(conn)
}
```

---

## WebSocket (gorilla/websocket)

### Server

```go
package main

import (
    "log"
    "net/http"
    "os"
    "path/filepath"

    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
}

func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }
    defer conn.Close()

    for {
        messageType, message, err := conn.ReadMessage()
        if err != nil {
            break
        }
        log.Printf("Received: %s", message)
        conn.WriteMessage(messageType, append([]byte("Echo: "), message...))
    }
}

func main() {
    home, _ := os.UserHomeDir()
    certDir := filepath.Join(home, ".pqcert", "certs", "localhost")

    http.HandleFunc("/ws", wsHandler)

    log.Println("🔐 WSS server running at wss://localhost:443/ws")
    http.ListenAndServeTLS(":443",
        filepath.Join(certDir, "localhost.pem"),
        filepath.Join(certDir, "localhost-key.pem"),
        nil)
}
```

---

## PQCert Helper Package

### pqcert/pqcert.go

```go
package pqcert

import (
    "crypto/tls"
    "crypto/x509"
    "net/http"
    "os"
    "path/filepath"
)

type PQCert struct {
    Home    string
    CertDir string
    CADir   string
}

func New() *PQCert {
    home, _ := os.UserHomeDir()
    pqcertDir := filepath.Join(home, ".pqcert")

    return &PQCert{
        Home:    pqcertDir,
        CertDir: filepath.Join(pqcertDir, "certs", "localhost"),
        CADir:   filepath.Join(pqcertDir, "ca"),
    }
}

func (p *PQCert) CertFile() string {
    return filepath.Join(p.CertDir, "localhost.pem")
}

func (p *PQCert) KeyFile() string {
    return filepath.Join(p.CertDir, "localhost-key.pem")
}

func (p *PQCert) CAFile() string {
    return filepath.Join(p.CADir, "pqcert-ca.pem")
}

func (p *PQCert) TLSConfig() (*tls.Config, error) {
    cert, err := tls.LoadX509KeyPair(p.CertFile(), p.KeyFile())
    if err != nil {
        return nil, err
    }

    return &tls.Config{
        Certificates: []tls.Certificate{cert},
    }, nil
}

func (p *PQCert) ClientTLSConfig() (*tls.Config, error) {
    caCert, err := os.ReadFile(p.CAFile())
    if err != nil {
        return nil, err
    }

    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    return &tls.Config{
        RootCAs: caCertPool,
    }, nil
}

func (p *PQCert) HTTPClient() (*http.Client, error) {
    tlsConfig, err := p.ClientTLSConfig()
    if err != nil {
        return nil, err
    }

    return &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: tlsConfig,
        },
    }, nil
}
```

### Usage

```go
package main

import (
    "fmt"
    "net/http"

    "yourmodule/pqcert"
)

func main() {
    pq := pqcert.New()

    // Server
    http.HandleFunc("/", handler)
    http.ListenAndServeTLS(":443", pq.CertFile(), pq.KeyFile(), nil)

    // Client
    client, _ := pq.HTTPClient()
    resp, _ := client.Get("https://localhost:443")
    fmt.Println(resp.Status)
}
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize Go apps
- [Kubernetes Guide](../guides/kubernetes.md) - Deploy to K8s
- [mTLS Guide](../guides/mtls.md) - Service mesh security
