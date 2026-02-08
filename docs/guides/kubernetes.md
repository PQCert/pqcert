# Kubernetes Guide

> Deploy applications with PQCert certificates on Kubernetes

---

## Create TLS Secret

### From Certificate Files

```bash
kubectl create secret tls pqcert-tls \
  --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
  --key=$HOME/.pqcert/certs/localhost/localhost-key.pem \
  --namespace=default
```

### From YAML

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pqcert-tls
  namespace: default
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-key>
```

```bash
# Encode certificates
cat ~/.pqcert/certs/localhost/localhost.pem | base64 -w0
cat ~/.pqcert/certs/localhost/localhost-key.pem | base64 -w0
```

---

## Nginx Ingress Controller

### Install Nginx Ingress

```bash
# Using Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx

# Or using kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
```

### Ingress Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - localhost
        - "*.localhost"
      secretName: pqcert-tls
  rules:
    - host: localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-service
                port:
                  number: 80
    - host: api.localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
```

---

## Complete Deployment Example

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: myapp:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: production
          resources:
            limits:
              memory: "256Mi"
              cpu: "500m"
            requests:
              memory: "128Mi"
              cpu: "250m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
  namespace: default
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP
```

### ingress.yaml

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - localhost
      secretName: pqcert-tls
  rules:
    - host: localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-service
                port:
                  number: 80
```

---

## Traefik Ingress Controller

### Install Traefik

```bash
helm repo add traefik https://helm.traefik.io/traefik
helm install traefik traefik/traefik
```

### IngressRoute (Traefik CRD)

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: app-ingress
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`localhost`)
      kind: Rule
      services:
        - name: app-service
          port: 80
  tls:
    secretName: pqcert-tls
```

---

## Kind (Kubernetes in Docker)

### Create Cluster with Ingress

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
```

```bash
# Create cluster
kind create cluster --config kind-config.yaml --name pqcert-cluster

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Create TLS secret
kubectl create secret tls pqcert-tls \
  --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
  --key=$HOME/.pqcert/certs/localhost/localhost-key.pem
```

---

## ConfigMap for CA Certificate

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pqcert-ca
  namespace: default
data:
  ca.crt: |
    -----BEGIN CERTIFICATE-----
    <CA certificate content>
    -----END CERTIFICATE-----
```

### Mount in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:latest
      volumeMounts:
        - name: ca-cert
          mountPath: /etc/ssl/certs/pqcert-ca.crt
          subPath: ca.crt
          readOnly: true
  volumes:
    - name: ca-cert
      configMap:
        name: pqcert-ca
```

---

## mTLS with Istio

### Install Istio

```bash
istioctl install --set profile=demo
kubectl label namespace default istio-injection=enabled
```

### PeerAuthentication (Strict mTLS)

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

### Gateway with TLS

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: app-gateway
  namespace: default
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: pqcert-tls
      hosts:
        - localhost
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-vs
  namespace: default
spec:
  hosts:
    - localhost
  gateways:
    - app-gateway
  http:
    - route:
        - destination:
            host: app-service
            port:
              number: 80
```

---

## Helm Chart Values

### values.yaml

```yaml
replicaCount: 3

image:
  repository: myapp
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: localhost
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: pqcert-tls
      hosts:
        - localhost

resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 250m
    memory: 128Mi
```

---

## Cert-Manager Integration

If you want to manage certificates with cert-manager:

### ClusterIssuer

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: pqcert-ca-issuer
spec:
  ca:
    secretName: pqcert-ca-secret
---
apiVersion: v1
kind: Secret
metadata:
  name: pqcert-ca-secret
  namespace: cert-manager
type: Opaque
data:
  tls.crt: <base64-encoded-CA-cert>
  tls.key: <base64-encoded-CA-key>
```

### Certificate

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app-cert
  namespace: default
spec:
  secretName: app-tls
  issuerRef:
    name: pqcert-ca-issuer
    kind: ClusterIssuer
  commonName: localhost
  dnsNames:
    - localhost
    - "*.localhost"
    - local.dev
    - "*.local.dev"
  ipAddresses:
    - 127.0.0.1
```

---

## Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
  egress:
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443
```

---

## Troubleshooting

### Check Secret

```bash
kubectl get secret pqcert-tls -o yaml
kubectl describe secret pqcert-tls
```

### Check Ingress

```bash
kubectl get ingress
kubectl describe ingress app-ingress
```

### Check Certificate

```bash
# View certificate from ingress
openssl s_client -connect localhost:443 -servername localhost

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Debug Pod

```bash
kubectl run debug --rm -it --image=curlimages/curl -- sh
# Inside pod:
curl -v https://app-service/
```

---

## Next Steps

- [Docker Guide](./docker.md) - Docker basics
- [mTLS Guide](./mtls.md) - Service-to-service auth
- [CI/CD Guide](./cicd.md) - Automated deployments
