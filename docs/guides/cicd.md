# CI/CD Guide

> Integrate PQCert certificates into your CI/CD pipelines

---

## GitHub Actions

### Generate Certificates in CI

```yaml
# .github/workflows/deploy.yml
name: Deploy with HTTPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install PQCert
        run: |
          curl -sSL https://pqcert.org/install.sh | bash

      - name: Generate Certificates
        run: |
          pqcert localhost
          pqcert api.example.com

      - name: Build Docker Image
        run: |
          docker build \
            --build-context certs=$HOME/.pqcert/certs/localhost \
            -t myapp:${{ github.sha }} .

      - name: Deploy
        run: |
          # Deploy with certificates
          kubectl create secret tls app-tls \
            --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
            --key=$HOME/.pqcert/certs/localhost/localhost-key.pem \
            --dry-run=client -o yaml | kubectl apply -f -
```

### Use Secrets for Certificates

```yaml
# .github/workflows/deploy.yml
name: Deploy with Stored Certificates

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Certificates from Secrets
        run: |
          mkdir -p ~/.pqcert/certs/localhost
          mkdir -p ~/.pqcert/ca

          echo "${{ secrets.PQCERT_CERT }}" > ~/.pqcert/certs/localhost/localhost.pem
          echo "${{ secrets.PQCERT_KEY }}" > ~/.pqcert/certs/localhost/localhost-key.pem
          echo "${{ secrets.PQCERT_CA }}" > ~/.pqcert/ca/pqcert-ca.pem

          chmod 600 ~/.pqcert/certs/localhost/localhost-key.pem

      - name: Run Tests
        run: |
          npm test
        env:
          SSL_CERT: ~/.pqcert/certs/localhost/localhost.pem
          SSL_KEY: ~/.pqcert/certs/localhost/localhost-key.pem
```

### Matrix Testing with HTTPS

```yaml
name: Test HTTPS

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}

      - name: Install PQCert
        shell: bash
        run: |
          if [[ "$RUNNER_OS" == "Windows" ]]; then
            # Windows installation
            powershell -Command "irm https://pqcert.org/install.ps1 | iex"
          else
            curl -sSL https://pqcert.org/install.sh | bash
          fi

      - name: Run HTTPS Tests
        run: npm test
```

---

## GitLab CI

### .gitlab-ci.yml

```yaml
stages:
  - build
  - test
  - deploy

variables:
  PQCERT_DIR: /root/.pqcert

before_script:
  - curl -sSL https://pqcert.org/install.sh | bash

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - pqcert localhost
    - npm test
  variables:
    SSL_CERT: $PQCERT_DIR/certs/localhost/localhost.pem
    SSL_KEY: $PQCERT_DIR/certs/localhost/localhost-key.pem

deploy:
  stage: deploy
  script:
    - echo "$PQCERT_CERT" > /tmp/cert.pem
    - echo "$PQCERT_KEY" > /tmp/key.pem
    - kubectl create secret tls app-tls --cert=/tmp/cert.pem --key=/tmp/key.pem --dry-run=client -o yaml | kubectl apply -f -
    - kubectl rollout restart deployment/app
  only:
    - main
```

### Using GitLab File Variables

```yaml
deploy:
  stage: deploy
  script:
    - kubectl create secret tls app-tls --cert=$PQCERT_CERT --key=$PQCERT_KEY --dry-run=client -o yaml | kubectl apply -f -
```

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        PQCERT_DIR = "${HOME}/.pqcert"
    }

    stages {
        stage('Setup') {
            steps {
                sh 'curl -sSL https://pqcert.org/install.sh | bash'
            }
        }

        stage('Generate Certificates') {
            steps {
                sh 'pqcert localhost'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build \
                        --build-context certs=${PQCERT_DIR}/certs/localhost \
                        -t myapp:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Test') {
            environment {
                SSL_CERT = "${PQCERT_DIR}/certs/localhost/localhost.pem"
                SSL_KEY = "${PQCERT_DIR}/certs/localhost/localhost-key.pem"
            }
            steps {
                sh 'npm test'
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    file(credentialsId: 'pqcert-cert', variable: 'CERT_FILE'),
                    file(credentialsId: 'pqcert-key', variable: 'KEY_FILE')
                ]) {
                    sh '''
                        kubectl create secret tls app-tls \
                            --cert=$CERT_FILE \
                            --key=$KEY_FILE \
                            --dry-run=client -o yaml | kubectl apply -f -
                    '''
                }
            }
        }
    }
}
```

---

## CircleCI

### .circleci/config.yml

```yaml
version: 2.1

executors:
  node-executor:
    docker:
      - image: cimg/node:20.0

jobs:
  setup:
    executor: node-executor
    steps:
      - checkout
      - run:
          name: Install PQCert
          command: curl -sSL https://pqcert.org/install.sh | bash
      - run:
          name: Generate Certificates
          command: pqcert localhost
      - persist_to_workspace:
          root: ~/
          paths:
            - .pqcert

  test:
    executor: node-executor
    steps:
      - checkout
      - attach_workspace:
          at: ~/
      - run:
          name: Install Dependencies
          command: npm ci
      - run:
          name: Run Tests
          command: npm test
          environment:
            SSL_CERT: ~/.pqcert/certs/localhost/localhost.pem
            SSL_KEY: ~/.pqcert/certs/localhost/localhost-key.pem

  deploy:
    executor: node-executor
    steps:
      - checkout
      - attach_workspace:
          at: ~/
      - run:
          name: Deploy to Kubernetes
          command: |
            kubectl create secret tls app-tls \
              --cert=~/.pqcert/certs/localhost/localhost.pem \
              --key=~/.pqcert/certs/localhost/localhost-key.pem \
              --dry-run=client -o yaml | kubectl apply -f -

workflows:
  build-test-deploy:
    jobs:
      - setup
      - test:
          requires:
            - setup
      - deploy:
          requires:
            - test
          filters:
            branches:
              only: main
```

---

## Azure DevOps

### azure-pipelines.yml

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  PQCERT_DIR: $(HOME)/.pqcert

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - task: Bash@3
            displayName: 'Install PQCert'
            inputs:
              targetType: 'inline'
              script: |
                curl -sSL https://pqcert.org/install.sh | bash

          - task: Bash@3
            displayName: 'Generate Certificates'
            inputs:
              targetType: 'inline'
              script: |
                pqcert localhost

          - task: NodeTool@0
            inputs:
              versionSpec: '20.x'

          - task: Bash@3
            displayName: 'Run Tests'
            inputs:
              targetType: 'inline'
              script: |
                npm ci
                npm test
            env:
              SSL_CERT: $(PQCERT_DIR)/certs/localhost/localhost.pem
              SSL_KEY: $(PQCERT_DIR)/certs/localhost/localhost-key.pem

  - stage: Deploy
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: DeployToK8s
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: Bash@3
                  displayName: 'Create TLS Secret'
                  inputs:
                    targetType: 'inline'
                    script: |
                      echo "$(PQCERT_CERT)" > /tmp/cert.pem
                      echo "$(PQCERT_KEY)" > /tmp/key.pem
                      kubectl create secret tls app-tls \
                        --cert=/tmp/cert.pem \
                        --key=/tmp/key.pem \
                        --dry-run=client -o yaml | kubectl apply -f -
```

---

## Drone CI

### .drone.yml

```yaml
kind: pipeline
type: docker
name: default

steps:
  - name: install-pqcert
    image: alpine
    commands:
      - apk add --no-cache curl bash python3
      - curl -sSL https://pqcert.org/install.sh | bash

  - name: test
    image: node:20-alpine
    environment:
      SSL_CERT: /root/.pqcert/certs/localhost/localhost.pem
      SSL_KEY: /root/.pqcert/certs/localhost/localhost-key.pem
    commands:
      - npm ci
      - npm test

  - name: deploy
    image: bitnami/kubectl
    environment:
      PQCERT_CERT:
        from_secret: pqcert_cert
      PQCERT_KEY:
        from_secret: pqcert_key
    commands:
      - echo "$PQCERT_CERT" > /tmp/cert.pem
      - echo "$PQCERT_KEY" > /tmp/key.pem
      - kubectl create secret tls app-tls --cert=/tmp/cert.pem --key=/tmp/key.pem --dry-run=client -o yaml | kubectl apply -f -
    when:
      branch:
        - main
```

---

## Docker Build with Certificates

### Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# Copy certificates at build time (for testing)
ARG CERT_DIR
COPY ${CERT_DIR}/localhost.pem /certs/
COPY ${CERT_DIR}/localhost-key.pem /certs/

ENV SSL_CERT=/certs/localhost.pem
ENV SSL_KEY=/certs/localhost-key.pem

EXPOSE 443
CMD ["node", "dist/server.js"]
```

### Build Command

```bash
docker build \
  --build-arg CERT_DIR=$HOME/.pqcert/certs/localhost \
  -t myapp:latest .
```

---

## Kubernetes Deployment with CI/CD

### Deploy Script

```bash
#!/bin/bash
set -e

NAMESPACE=${NAMESPACE:-default}
SECRET_NAME=${SECRET_NAME:-pqcert-tls}
CERT_PATH=${CERT_PATH:-$HOME/.pqcert/certs/localhost/localhost.pem}
KEY_PATH=${KEY_PATH:-$HOME/.pqcert/certs/localhost/localhost-key.pem}

# Create or update TLS secret
kubectl create secret tls $SECRET_NAME \
  --cert=$CERT_PATH \
  --key=$KEY_PATH \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests
kubectl apply -f k8s/

# Wait for deployment
kubectl rollout status deployment/app --namespace=$NAMESPACE

echo "✅ Deployment complete!"
```

---

## Certificate Rotation in CI/CD

### Rotation Script

```bash
#!/bin/bash
set -e

# Generate new certificates
pqcert localhost --force

# Update Kubernetes secret
kubectl create secret tls pqcert-tls \
  --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
  --key=$HOME/.pqcert/certs/localhost/localhost-key.pem \
  --dry-run=client -o yaml | kubectl apply -f -

# Rolling restart to pick up new certificates
kubectl rollout restart deployment/app

echo "✅ Certificate rotation complete!"
```

### GitHub Action for Rotation

```yaml
name: Rotate Certificates

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Install PQCert
        run: curl -sSL https://pqcert.org/install.sh | bash

      - name: Generate New Certificates
        run: pqcert localhost --force

      - name: Update Secret
        run: |
          kubectl create secret tls pqcert-tls \
            --cert=$HOME/.pqcert/certs/localhost/localhost.pem \
            --key=$HOME/.pqcert/certs/localhost/localhost-key.pem \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Restart Deployment
        run: kubectl rollout restart deployment/app
```

---

## Security Best Practices

1. **Never commit certificates** - Use CI/CD secrets
2. **Rotate regularly** - Set up automated rotation
3. **Limit access** - Only CI/CD system should have access
4. **Use short-lived certs** - For CI testing, use ephemeral certs
5. **Encrypt at rest** - Use encrypted secret storage

---

## Next Steps

- [Docker Guide](./docker.md) - Docker with certificates
- [Kubernetes Guide](./kubernetes.md) - K8s deployments
- [mTLS Guide](./mtls.md) - Service-to-service auth
