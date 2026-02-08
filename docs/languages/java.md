# Java Guide

> Use PQCert certificates with Java applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```java
import java.nio.file.Path;
import java.nio.file.Paths;

public class PQCertPaths {
    private static final Path HOME = Paths.get(System.getProperty("user.home"));
    private static final Path PQCERT_DIR = HOME.resolve(".pqcert");
    private static final Path CERT_DIR = PQCERT_DIR.resolve("certs/localhost");
    private static final Path CA_DIR = PQCERT_DIR.resolve("ca");

    public static Path getCertFile() { return CERT_DIR.resolve("localhost.pem"); }
    public static Path getKeyFile() { return CERT_DIR.resolve("localhost-key.pem"); }
    public static Path getPfxFile() { return CERT_DIR.resolve("localhost.pfx"); }
    public static Path getCaFile() { return CA_DIR.resolve("pqcert-ca.pem"); }
}
```

---

## Import PFX to Java KeyStore

PQCert generates a `localhost.pfx` file that Java can use directly:

```bash
# The PFX password is: pqcert
# Located at: ~/.pqcert/certs/localhost/localhost.pfx
```

### Convert to JKS (if needed)

```bash
keytool -importkeystore \
  -srckeystore ~/.pqcert/certs/localhost/localhost.pfx \
  -srcstoretype PKCS12 \
  -srcstorepass pqcert \
  -destkeystore keystore.jks \
  -deststoretype JKS \
  -deststorepass changeit
```

---

## Spring Boot

### application.properties

```properties
# HTTPS Configuration
server.port=443
server.ssl.enabled=true

# Using PFX directly
server.ssl.key-store=${user.home}/.pqcert/certs/localhost/localhost.pfx
server.ssl.key-store-type=PKCS12
server.ssl.key-store-password=pqcert
server.ssl.key-alias=1
```

### application.yml

```yaml
server:
  port: 443
  ssl:
    enabled: true
    key-store: ${user.home}/.pqcert/certs/localhost/localhost.pfx
    key-store-type: PKCS12
    key-store-password: pqcert
    key-alias: "1"
```

### Controller Example

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class HelloController {

    @GetMapping("/")
    public Map<String, Object> hello() {
        return Map.of(
            "message", "Hello from Spring Boot HTTPS!",
            "secure", true
        );
    }

    @GetMapping("/api/status")
    public Map<String, Object> status() {
        return Map.of("status", "ok", "https", true);
    }
}
```

### HTTP to HTTPS Redirect

```java
package com.example.demo.config;

import org.apache.catalina.Context;
import org.apache.catalina.connector.Connector;
import org.apache.tomcat.util.descriptor.web.SecurityCollection;
import org.apache.tomcat.util.descriptor.web.SecurityConstraint;
import org.springframework.boot.web.embedded.tomcat.TomcatServletWebServerFactory;
import org.springframework.boot.web.servlet.server.ServletWebServerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class HttpsRedirectConfig {

    @Bean
    public ServletWebServerFactory servletContainer() {
        TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory() {
            @Override
            protected void postProcessContext(Context context) {
                SecurityConstraint securityConstraint = new SecurityConstraint();
                securityConstraint.setUserConstraint("CONFIDENTIAL");
                SecurityCollection collection = new SecurityCollection();
                collection.addPattern("/*");
                securityConstraint.addCollection(collection);
                context.addConstraint(securityConstraint);
            }
        };
        tomcat.addAdditionalTomcatConnectors(httpConnector());
        return tomcat;
    }

    private Connector httpConnector() {
        Connector connector = new Connector(TomcatServletWebServerFactory.DEFAULT_PROTOCOL);
        connector.setScheme("http");
        connector.setPort(80);
        connector.setSecure(false);
        connector.setRedirectPort(443);
        return connector;
    }
}
```

---

## Quarkus

### application.properties

```properties
# HTTPS
quarkus.http.ssl-port=443
quarkus.http.ssl.certificate.key-store-file=${user.home}/.pqcert/certs/localhost/localhost.pfx
quarkus.http.ssl.certificate.key-store-file-type=PKCS12
quarkus.http.ssl.certificate.key-store-password=pqcert
```

### Resource Example

```java
package org.acme;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;

@Path("/")
public class HelloResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> hello() {
        return Map.of("message", "Hello from Quarkus HTTPS!");
    }
}
```

---

## Micronaut

### application.yml

```yaml
micronaut:
  server:
    port: 443
    ssl:
      enabled: true
      key-store:
        path: file:${user.home}/.pqcert/certs/localhost/localhost.pfx
        type: PKCS12
        password: pqcert
```

### Controller

```java
package com.example;

import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import java.util.Map;

@Controller("/")
public class HelloController {

    @Get
    public Map<String, Object> index() {
        return Map.of("message", "Hello from Micronaut HTTPS!");
    }
}
```

---

## Plain Java HTTPS Server

```java
import com.sun.net.httpserver.HttpsServer;
import com.sun.net.httpserver.HttpsConfigurator;
import javax.net.ssl.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.nio.file.*;
import java.security.*;

public class SimpleHttpsServer {
    public static void main(String[] args) throws Exception {
        String home = System.getProperty("user.home");
        Path pfxPath = Paths.get(home, ".pqcert", "certs", "localhost", "localhost.pfx");

        // Load keystore
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        try (InputStream is = Files.newInputStream(pfxPath)) {
            keyStore.load(is, "pqcert".toCharArray());
        }

        // Setup key manager
        KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
        kmf.init(keyStore, "pqcert".toCharArray());

        // Setup SSL context
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(kmf.getKeyManagers(), null, null);

        // Create HTTPS server
        HttpsServer server = HttpsServer.create(new InetSocketAddress(443), 0);
        server.setHttpsConfigurator(new HttpsConfigurator(sslContext));

        server.createContext("/", exchange -> {
            String response = "{\"message\": \"Hello from Java HTTPS!\"}";
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, response.length());
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes());
            }
        });

        server.start();
        System.out.println("🔐 HTTPS server running at https://localhost:443");
    }
}
```

---

## HTTPS Client

### Using HttpClient (Java 11+)

```java
import javax.net.ssl.*;
import java.net.URI;
import java.net.http.*;
import java.nio.file.*;
import java.security.*;
import java.security.cert.*;

public class HttpsClientExample {
    public static void main(String[] args) throws Exception {
        String home = System.getProperty("user.home");
        Path caPath = Paths.get(home, ".pqcert", "ca", "pqcert-ca.pem");

        // Load CA certificate
        CertificateFactory cf = CertificateFactory.getInstance("X.509");
        Certificate ca = cf.generateCertificate(Files.newInputStream(caPath));

        // Create truststore with CA
        KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
        trustStore.load(null);
        trustStore.setCertificateEntry("pqcert-ca", ca);

        TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(trustStore);

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, tmf.getTrustManagers(), null);

        // Create HTTP client
        HttpClient client = HttpClient.newBuilder()
            .sslContext(sslContext)
            .build();

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://localhost:443"))
            .GET()
            .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println(response.body());
    }
}
```

### Using RestTemplate (Spring)

```java
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;
import org.apache.http.impl.client.*;
import org.apache.http.ssl.*;
import javax.net.ssl.SSLContext;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.security.cert.*;

public class RestTemplateExample {

    public RestTemplate createSecureRestTemplate() throws Exception {
        String home = System.getProperty("user.home");
        Path caPath = Paths.get(home, ".pqcert", "ca", "pqcert-ca.pem");

        // Load CA
        CertificateFactory cf = CertificateFactory.getInstance("X.509");
        Certificate ca = cf.generateCertificate(Files.newInputStream(caPath));

        KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
        trustStore.load(null);
        trustStore.setCertificateEntry("pqcert-ca", ca);

        SSLContext sslContext = SSLContextBuilder.create()
            .loadTrustMaterial(trustStore, null)
            .build();

        CloseableHttpClient httpClient = HttpClients.custom()
            .setSSLContext(sslContext)
            .build();

        return new RestTemplate(new HttpComponentsClientHttpRequestFactory(httpClient));
    }
}
```

---

## mTLS Client

```java
import javax.net.ssl.*;
import java.nio.file.*;
import java.security.*;

public class MtlsClient {
    public static SSLContext createMtlsContext() throws Exception {
        String home = System.getProperty("user.home");

        // Load client certificate (PFX)
        Path pfxPath = Paths.get(home, ".pqcert", "certs", "localhost", "localhost.pfx");
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        keyStore.load(Files.newInputStream(pfxPath), "pqcert".toCharArray());

        KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
        kmf.init(keyStore, "pqcert".toCharArray());

        // Load CA
        Path caPath = Paths.get(home, ".pqcert", "ca", "pqcert-ca.pem");
        CertificateFactory cf = CertificateFactory.getInstance("X.509");
        Certificate ca = cf.generateCertificate(Files.newInputStream(caPath));

        KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
        trustStore.load(null);
        trustStore.setCertificateEntry("pqcert-ca", ca);

        TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
        tmf.init(trustStore);

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);

        return sslContext;
    }
}
```

---

## gRPC with TLS

### Server

```java
import io.grpc.*;
import io.grpc.netty.shaded.io.grpc.netty.*;
import java.io.*;
import java.nio.file.*;

public class GrpcServer {
    public static void main(String[] args) throws Exception {
        String home = System.getProperty("user.home");
        Path certPath = Paths.get(home, ".pqcert", "certs", "localhost", "localhost.pem");
        Path keyPath = Paths.get(home, ".pqcert", "certs", "localhost", "localhost-key.pem");

        Server server = NettyServerBuilder.forPort(443)
            .useTransportSecurity(certPath.toFile(), keyPath.toFile())
            // .addService(new YourServiceImpl())
            .build()
            .start();

        System.out.println("🔐 gRPC server running on port 443");
        server.awaitTermination();
    }
}
```

---

## Troubleshooting

### PKIX path building failed

The CA is not trusted. Add it to Java's truststore:

```bash
# Add PQCert CA to Java truststore
sudo keytool -import -trustcacerts \
  -alias pqcert-ca \
  -file ~/.pqcert/ca/pqcert-ca.pem \
  -keystore $JAVA_HOME/lib/security/cacerts \
  -storepass changeit
```

### Permission denied for port 443

Use port 8443 or run with elevated privileges:

```properties
server.port=8443
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize Java apps
- [Kubernetes Guide](../guides/kubernetes.md) - Deploy to K8s
- [Nginx Guide](../guides/nginx.md) - Reverse proxy
