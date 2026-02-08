# .NET / C# Guide

> Use PQCert certificates with ASP.NET Core and .NET applications

## Prerequisites

```bash
# Install PQCert
curl -sSL https://pqcert.org/install.sh | bash
```

---

## Certificate Paths

```csharp
using System;
using System.IO;

public static class PQCertPaths
{
    private static readonly string Home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    public static readonly string PQCertDir = Path.Combine(Home, ".pqcert");
    public static readonly string CertDir = Path.Combine(PQCertDir, "certs", "localhost");
    public static readonly string CADir = Path.Combine(PQCertDir, "ca");

    public static string CertFile => Path.Combine(CertDir, "localhost.pem");
    public static string KeyFile => Path.Combine(CertDir, "localhost-key.pem");
    public static string PfxFile => Path.Combine(CertDir, "localhost.pfx");
    public static string CAFile => Path.Combine(CADir, "pqcert-ca.pem");

    public const string PfxPassword = "pqcert";
}
```

---

## ASP.NET Core (Kestrel)

### Program.cs (.NET 6+)

```csharp
using System.Security.Cryptography.X509Certificates;

var builder = WebApplication.CreateBuilder(args);

// Get certificate paths
var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");

// Configure Kestrel with HTTPS
builder.WebHost.ConfigureKestrel(serverOptions =>
{
    serverOptions.ListenAnyIP(443, listenOptions =>
    {
        listenOptions.UseHttps(pfxPath, "pqcert");
    });

    // Optional: HTTP redirect
    serverOptions.ListenAnyIP(80);
});

var app = builder.Build();

// Redirect HTTP to HTTPS
app.UseHttpsRedirection();

app.MapGet("/", () => new { Message = "Hello from ASP.NET Core HTTPS!" });

app.MapGet("/api/status", () => new { Status = "ok", Secure = true });

app.Run();
```

### appsettings.json

```json
{
  "Kestrel": {
    "Endpoints": {
      "Https": {
        "Url": "https://localhost:443",
        "Certificate": {
          "Path": "~/.pqcert/certs/localhost/localhost.pfx",
          "Password": "pqcert"
        }
      },
      "Http": {
        "Url": "http://localhost:80"
      }
    }
  }
}
```

### Load from Environment

```csharp
builder.WebHost.ConfigureKestrel((context, serverOptions) =>
{
    var pfxPath = Environment.GetEnvironmentVariable("PQCERT_PFX_PATH")
        ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            ".pqcert", "certs", "localhost", "localhost.pfx");

    var pfxPassword = Environment.GetEnvironmentVariable("PQCERT_PFX_PASSWORD") ?? "pqcert";

    serverOptions.ListenAnyIP(443, listenOptions =>
    {
        listenOptions.UseHttps(pfxPath, pfxPassword);
    });
});
```

---

## Import PFX Certificate

### Using dotnet dev-certs

```bash
# Import PQCert certificate for development
dotnet dev-certs https --import ~/.pqcert/certs/localhost/localhost.pfx -p pqcert
```

### Load Certificate in Code

```csharp
using System.Security.Cryptography.X509Certificates;

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");

var certificate = new X509Certificate2(pfxPath, "pqcert");

Console.WriteLine($"Subject: {certificate.Subject}");
Console.WriteLine($"Expires: {certificate.NotAfter}");
```

---

## Minimal API Example

```csharp
using System.Security.Cryptography.X509Certificates;

var builder = WebApplication.CreateBuilder(args);

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(443, listenOptions =>
    {
        listenOptions.UseHttps(pfxPath, "pqcert");
    });
});

var app = builder.Build();

app.MapGet("/", () => "Hello, HTTPS!");

app.MapGet("/api/users/{id}", (int id) => new { Id = id, Name = $"User {id}" });

app.MapPost("/api/data", (DataRequest request) => new { Received = request });

app.Run();

record DataRequest(string Name, int Value);
```

---

## Controller-Based API

### Controllers/HomeController.cs

```csharp
using Microsoft.AspNetCore.Mvc;

namespace MyApp.Controllers;

[ApiController]
[Route("[controller]")]
public class HomeController : ControllerBase
{
    [HttpGet("/")]
    public IActionResult Index()
    {
        return Ok(new { Message = "Hello from ASP.NET Core HTTPS!" });
    }

    [HttpGet("/api/secure")]
    public IActionResult SecureEndpoint()
    {
        return Ok(new
        {
            Secure = HttpContext.Request.IsHttps,
            Protocol = HttpContext.Request.Protocol
        });
    }
}
```

---

## HttpClient with Custom CA

### Basic Request

```csharp
using System.Net.Http;
using System.Security.Cryptography.X509Certificates;

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var caPath = Path.Combine(home, ".pqcert", "ca", "pqcert-ca.pem");

// Load CA certificate
var caCert = X509Certificate2.CreateFromPemFile(caPath);

// Create handler with custom CA
var handler = new HttpClientHandler();
handler.ClientCertificateOptions = ClientCertificateOption.Manual;
handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
{
    // Add CA to chain
    chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
    chain.ChainPolicy.CustomTrustStore.Add(caCert);
    return chain.Build(cert);
};

var client = new HttpClient(handler);
var response = await client.GetStringAsync("https://localhost:443");
Console.WriteLine(response);
```

### Using IHttpClientFactory

```csharp
// Program.cs
builder.Services.AddHttpClient("PQCertClient", client =>
{
    client.BaseAddress = new Uri("https://localhost:443");
})
.ConfigurePrimaryHttpMessageHandler(() =>
{
    var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    var caPath = Path.Combine(home, ".pqcert", "ca", "pqcert-ca.pem");
    var caCert = X509Certificate2.CreateFromPemFile(caPath);

    var handler = new HttpClientHandler();
    handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
    {
        chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
        chain.ChainPolicy.CustomTrustStore.Add(caCert);
        return chain.Build(cert);
    };

    return handler;
});

// Usage in controller
public class MyController : ControllerBase
{
    private readonly IHttpClientFactory _clientFactory;

    public MyController(IHttpClientFactory clientFactory)
    {
        _clientFactory = clientFactory;
    }

    [HttpGet]
    public async Task<IActionResult> CallSecureService()
    {
        var client = _clientFactory.CreateClient("PQCertClient");
        var response = await client.GetStringAsync("/api/data");
        return Ok(response);
    }
}
```

---

## mTLS Client

```csharp
using System.Net.Http;
using System.Security.Cryptography.X509Certificates;

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");
var caPath = Path.Combine(home, ".pqcert", "ca", "pqcert-ca.pem");

// Load client certificate
var clientCert = new X509Certificate2(pfxPath, "pqcert");
var caCert = X509Certificate2.CreateFromPemFile(caPath);

var handler = new HttpClientHandler();

// Add client certificate
handler.ClientCertificates.Add(clientCert);

// Trust CA
handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
{
    chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
    chain.ChainPolicy.CustomTrustStore.Add(caCert);
    return chain.Build(cert);
};

var client = new HttpClient(handler);
var response = await client.GetStringAsync("https://secure-service.localhost/api");
```

---

## gRPC with TLS

### Server

```csharp
using Microsoft.AspNetCore.Server.Kestrel.Core;

var builder = WebApplication.CreateBuilder(args);

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(443, listenOptions =>
    {
        listenOptions.Protocols = HttpProtocols.Http2;
        listenOptions.UseHttps(pfxPath, "pqcert");
    });
});

builder.Services.AddGrpc();

var app = builder.Build();

app.MapGrpcService<GreeterService>();

app.Run();
```

### Client

```csharp
using Grpc.Net.Client;
using System.Security.Cryptography.X509Certificates;

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var caPath = Path.Combine(home, ".pqcert", "ca", "pqcert-ca.pem");
var caCert = X509Certificate2.CreateFromPemFile(caPath);

var handler = new HttpClientHandler();
handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
{
    chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
    chain.ChainPolicy.CustomTrustStore.Add(caCert);
    return chain.Build(cert);
};

var channel = GrpcChannel.ForAddress("https://localhost:443", new GrpcChannelOptions
{
    HttpHandler = handler
});

var client = new Greeter.GreeterClient(channel);
var reply = await client.SayHelloAsync(new HelloRequest { Name = "World" });
```

---

## SignalR with HTTPS

### Server

```csharp
var builder = WebApplication.CreateBuilder(args);

var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
var pfxPath = Path.Combine(home, ".pqcert", "certs", "localhost", "localhost.pfx");

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(443, listenOptions =>
    {
        listenOptions.UseHttps(pfxPath, "pqcert");
    });
});

builder.Services.AddSignalR();

var app = builder.Build();

app.MapHub<ChatHub>("/chat");

app.Run();
```

### Client

```csharp
using Microsoft.AspNetCore.SignalR.Client;

var connection = new HubConnectionBuilder()
    .WithUrl("https://localhost:443/chat", options =>
    {
        options.HttpMessageHandlerFactory = _ =>
        {
            var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var caPath = Path.Combine(home, ".pqcert", "ca", "pqcert-ca.pem");
            var caCert = X509Certificate2.CreateFromPemFile(caPath);

            var handler = new HttpClientHandler();
            handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
            {
                chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
                chain.ChainPolicy.CustomTrustStore.Add(caCert);
                return chain.Build(cert);
            };
            return handler;
        };
    })
    .Build();

await connection.StartAsync();
```

---

## PQCert Helper Class

```csharp
using System.Security.Cryptography.X509Certificates;

public class PQCert
{
    private readonly string _home;
    private readonly string _pqcertDir;

    public PQCert()
    {
        _home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        _pqcertDir = Path.Combine(_home, ".pqcert");
    }

    public string CertDir => Path.Combine(_pqcertDir, "certs", "localhost");
    public string CADir => Path.Combine(_pqcertDir, "ca");

    public string CertFile => Path.Combine(CertDir, "localhost.pem");
    public string KeyFile => Path.Combine(CertDir, "localhost-key.pem");
    public string PfxFile => Path.Combine(CertDir, "localhost.pfx");
    public string CAFile => Path.Combine(CADir, "pqcert-ca.pem");

    public const string PfxPassword = "pqcert";

    public X509Certificate2 LoadCertificate()
        => new X509Certificate2(PfxFile, PfxPassword);

    public X509Certificate2 LoadCA()
        => X509Certificate2.CreateFromPemFile(CAFile);

    public bool Exists()
        => File.Exists(PfxFile) && File.Exists(CAFile);

    public HttpClientHandler CreateHandler()
    {
        var caCert = LoadCA();
        var handler = new HttpClientHandler();
        handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
        {
            chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
            chain.ChainPolicy.CustomTrustStore.Add(caCert);
            return chain.Build(cert);
        };
        return handler;
    }
}
```

---

## Troubleshooting

### Certificate not trusted

Install CA to Windows certificate store:

```powershell
# Run as Administrator
Import-Certificate -FilePath "$env:USERPROFILE\.pqcert\ca\pqcert-ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

### Permission denied for port 443

Use port 5001 or run as administrator:

```csharp
options.ListenAnyIP(5001, listenOptions => { ... });
```

---

## Next Steps

- [Docker Guide](../guides/docker.md) - Containerize .NET apps
- [Kubernetes Guide](../guides/kubernetes.md) - Deploy to K8s
- [Nginx Guide](../guides/nginx.md) - Reverse proxy
