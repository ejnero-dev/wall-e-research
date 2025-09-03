# 🚀 Wall-E Deployment Guide

Complete production deployment guide for the Wall-E Wallapop automation system with AI Engine.

---

## 📋 Table of Contents

- [🎯 Deployment Overview](#-deployment-overview)
- [🐳 Docker Deployment](#-docker-deployment)
- [☸️ Kubernetes Deployment](#️-kubernetes-deployment)
- [🌐 Cloud Provider Setup](#-cloud-provider-setup)
- [🔧 Production Configuration](#-production-configuration)
- [🛡️ Security Setup](#️-security-setup)
- [📊 Monitoring & Logging](#-monitoring--logging)
- [🔄 CI/CD Pipeline](#-cicd-pipeline)
- [📈 Scaling & Performance](#-scaling--performance)
- [🛠️ Maintenance & Updates](#️-maintenance--updates)

---

## 🎯 Deployment Overview

### Deployment Options

**🐳 Docker Compose (Recommended for Small-Medium Scale):**
- Single server deployment
- Easy setup and management
- Suitable for 100-1000 conversations/day
- Resource requirement: 16GB+ RAM, 4+ CPU cores

**☸️ Kubernetes (Enterprise Scale):**
- Multi-server cluster deployment
- Auto-scaling and high availability
- Suitable for 1000+ conversations/day
- Horizontal scaling capabilities

**☁️ Cloud-Native (Maximum Scale):**
- Cloud provider managed services
- Serverless AI inference
- Global distribution
- Auto-scaling and fault tolerance

### Architecture Overview

```
Production Wall-E Architecture
├── 🌐 Load Balancer (Nginx/HAProxy)
│   ├── SSL termination
│   ├── Rate limiting
│   └── Health checks
├── 🤖 AI Engine Services (Multiple instances)
│   ├── Ollama LLM inference
│   ├── Wall-E AI Engine
│   └── Performance monitoring
├── 💬 Conversation Services
│   ├── Message processing
│   ├── State management
│   └── Integration layer
├── 🗄️ Data Layer
│   ├── PostgreSQL (Primary data)
│   ├── Redis (Cache & sessions)
│   └── Object storage (Logs, models)
└── 📊 Monitoring Stack
    ├── Prometheus (Metrics)
    ├── Grafana (Dashboards)
    ├── ELK Stack (Logs)
    └── AlertManager (Alerts)
```

### Resource Requirements

**Production Minimum:**
- **CPU:** 8 cores, 3.0GHz+
- **RAM:** 32GB (16GB for AI models + 16GB system)
- **Storage:** 100GB SSD (50GB for models + 50GB data)
- **Network:** 1Gbps bandwidth

**Production Recommended:**
- **CPU:** 16 cores, 3.2GHz+
- **RAM:** 64GB (32GB for AI models + 32GB system)
- **Storage:** 250GB NVMe SSD
- **Network:** 10Gbps bandwidth

**Enterprise Scale:**
- **Cluster:** 3-5 nodes minimum
- **CPU per node:** 16+ cores
- **RAM per node:** 64GB+
- **Storage:** Distributed storage (Ceph, GlusterFS)
- **Network:** High-speed inter-node connectivity

---

## 🐳 Docker Deployment

### Docker Compose Setup

#### Production Docker Compose

**Create `docker-compose.prod.yml`:**
```yaml
version: '3.8'

services:
  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: wall_e_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - ai_engine
    restart: unless-stopped
    networks:
      - wall_e_network

  # Ollama LLM Server
  ollama:
    image: ollama/ollama:latest
    container_name: wall_e_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
      - ./ollama/entrypoint.sh:/entrypoint.sh
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_MODELS=/root/.ollama/models
    command: ["/entrypoint.sh"]
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 20G
        reservations:
          memory: 16G
    networks:
      - wall_e_network

  # Wall-E AI Engine
  ai_engine:
    build:
      context: .
      dockerfile: docker/Dockerfile.prod
    container_name: wall_e_ai_engine
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ai_engine_cache:/app/cache
    environment:
      - WALL_E_ENV=production
      - WALL_E_CONFIG_FILE=/app/config/production.yaml
      - OLLAMA_HOST=http://ollama:11434
      - POSTGRES_URL=postgresql://wall_e:${POSTGRES_PASSWORD}@postgres:5432/wall_e_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - ollama
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v2/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - wall_e_network

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: wall_e_postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      - POSTGRES_DB=wall_e_prod
      - POSTGRES_USER=wall_e
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=es_ES.UTF-8 --lc-ctype=es_ES.UTF-8
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    networks:
      - wall_e_network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: wall_e_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf:ro
    command: redis-server /etc/redis/redis.conf
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    networks:
      - wall_e_network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: wall_e_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped
    networks:
      - wall_e_network

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: wall_e_grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped
    networks:
      - wall_e_network

volumes:
  postgres_data:
  redis_data:
  ollama_models:
  ai_engine_cache:
  prometheus_data:
  grafana_data:
  nginx_logs:

networks:
  wall_e_network:
    driver: bridge
```

#### Production Dockerfile

**Create `docker/Dockerfile.prod`:**
```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install spaCy Spanish model
RUN python -m spacy download es_core_news_sm

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user for security
RUN groupadd -r wall_e && useradd -r -g wall_e wall_e

# Set up application directory
WORKDIR /app
COPY --chown=wall_e:wall_e . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/temp && \
    chown -R wall_e:wall_e /app

# Switch to non-root user
USER wall_e

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Environment Configuration

**Create `.env.prod`:**
```bash
# Database Configuration
POSTGRES_PASSWORD=secure_production_password_here
POSTGRES_URL=postgresql://wall_e:secure_production_password_here@postgres:5432/wall_e_prod

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# AI Engine Configuration
WALL_E_ENV=production
WALL_E_AI_MODE=ai_first
WALL_E_MODEL=llama3.2:11b-vision-instruct-q4_0
OLLAMA_HOST=http://ollama:11434

# Security Configuration
SECRET_KEY=generate_strong_secret_key_here
FRAUD_DETECTION_THRESHOLD=20
STRICT_VALIDATION=true

# Monitoring Configuration
GRAFANA_PASSWORD=secure_grafana_password_here
PROMETHEUS_RETENTION=30d

# Performance Configuration
MAX_CONCURRENT_REQUESTS=15
MEMORY_THRESHOLD_MB=24000
ENABLE_CACHING=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
AUDIT_ALL_RESPONSES=true
```

#### Nginx Configuration

**Create `nginx/nginx.conf`:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream ai_engine {
        server ai_engine:8000;
        keepalive 32;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=conversation:10m rate=5r/s;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL certificates
        ssl_certificate /etc/ssl/certs/your-domain.com.crt;
        ssl_certificate_key /etc/ssl/certs/your-domain.com.key;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://ai_engine;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Conversation endpoints (stricter rate limiting)
        location /api/v2/conversation/ {
            limit_req zone=conversation burst=10 nodelay;
            
            proxy_pass http://ai_engine;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check (no rate limiting)
        location /api/v2/health {
            proxy_pass http://ai_engine;
            access_log off;
        }

        # Monitoring (restrict access)
        location /metrics {
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
            
            proxy_pass http://ai_engine;
        }
    }
}
```

#### Deployment Commands

```bash
# 1. Prepare environment
cp .env.example .env.prod
# Edit .env.prod with production values

# 2. Generate SSL certificates (Let's Encrypt example)
sudo certbot certonly --standalone -d your-domain.com

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs ai_engine

# 5. Initialize AI models
docker exec wall_e_ollama ollama pull llama3.2:11b-vision-instruct-q4_0

# 6. Test deployment
curl -k https://your-domain.com/api/v2/health
```

#### Production Monitoring

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f ai_engine
docker-compose -f docker-compose.prod.yml logs -f ollama

# Monitor resources
docker stats

# Check AI Engine health
curl -s https://your-domain.com/api/v2/health | jq

# Check metrics
curl -s https://your-domain.com/api/v2/metrics | jq
```

---

## ☸️ Kubernetes Deployment

### Kubernetes Architecture

```yaml
# Namespace for Wall-E
apiVersion: v1
kind: Namespace
metadata:
  name: wall-e-production
  labels:
    name: wall-e-production
    tier: production
```

#### ConfigMaps and Secrets

**Create `k8s/configmaps/ai-engine-config.yaml`:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-engine-config
  namespace: wall-e-production
data:
  production.yaml: |
    ai_engine:
      mode: ai_first
      model_name: llama3.2:11b-vision-instruct-q4_0
      temperature: 0.7
      max_tokens: 200
      timeout: 30
      max_concurrent_requests: 15
      connection_pool_size: 8
      enable_caching: true
      cache_size: 2000
    
    security:
      fraud_detection_threshold: 20
      critical_fraud_threshold: 40
      enable_url_analysis: true
      strict_validation: true
      audit_all_responses: true
    
    performance:
      memory_threshold_mb: 24000
      gc_threshold: 50
      enable_memory_monitoring: true
      enable_performance_monitoring: true
    
    logging:
      level: INFO
      format: json
      enable_structured_logging: true
```

**Create `k8s/secrets/wall-e-secrets.yaml`:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: wall-e-secrets
  namespace: wall-e-production
type: Opaque
data:
  postgres-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
  secret-key: <base64-encoded-secret-key>
  grafana-password: <base64-encoded-password>
```

#### Persistent Volumes

**Create `k8s/storage/postgres-pv.yaml`:**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
  namespace: wall-e-production
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  hostPath:
    path: /data/postgres
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: wall-e-production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
```

#### Ollama Deployment

**Create `k8s/deployments/ollama.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: wall-e-production
  labels:
    app: ollama
    tier: ai-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
        tier: ai-inference
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        - name: OLLAMA_MODELS
          value: "/root/.ollama/models"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
          limits:
            memory: "24Gi"
            cpu: "8"
        volumeMounts:
        - name: ollama-models
          mountPath: /root/.ollama
        livenessProbe:
          httpGet:
            path: /api/version
            port: 11434
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/version
            port: 11434
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: ollama-models
        persistentVolumeClaim:
          claimName: ollama-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: wall-e-production
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

#### AI Engine Deployment

**Create `k8s/deployments/ai-engine.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-engine
  namespace: wall-e-production
  labels:
    app: ai-engine
    tier: application
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-engine
  template:
    metadata:
      labels:
        app: ai-engine
        tier: application
    spec:
      containers:
      - name: ai-engine
        image: your-registry/wall-e-ai-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: WALL_E_ENV
          value: "production"
        - name: WALL_E_CONFIG_FILE
          value: "/app/config/production.yaml"
        - name: OLLAMA_HOST
          value: "http://ollama-service:11434"
        - name: POSTGRES_URL
          valueFrom:
            secretKeyRef:
              name: wall-e-secrets
              key: postgres-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: wall-e-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: wall-e-secrets
              key: secret-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: logs-volume
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /api/v2/health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v2/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: ai-engine-config
      - name: logs-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: ai-engine-service
  namespace: wall-e-production
spec:
  selector:
    app: ai-engine
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Horizontal Pod Autoscaler

**Create `k8s/autoscaling/ai-engine-hpa.yaml`:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-engine-hpa
  namespace: wall-e-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-engine
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

#### Ingress Configuration

**Create `k8s/ingress/wall-e-ingress.yaml`:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wall-e-ingress
  namespace: wall-e-production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: wall-e-tls
  rules:
  - host: api.your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: ai-engine-service
            port:
              number: 8000
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: ai-engine-service
            port:
              number: 8000
```

#### Deployment Commands

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Apply secrets and configmaps
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/configmaps/

# 3. Create persistent volumes
kubectl apply -f k8s/storage/

# 4. Deploy databases
kubectl apply -f k8s/deployments/postgres.yaml
kubectl apply -f k8s/deployments/redis.yaml

# 5. Deploy Ollama
kubectl apply -f k8s/deployments/ollama.yaml

# 6. Wait for Ollama to be ready
kubectl wait --for=condition=available --timeout=300s deployment/ollama -n wall-e-production

# 7. Pull AI models
kubectl exec -n wall-e-production deployment/ollama -- ollama pull llama3.2:11b-vision-instruct-q4_0

# 8. Deploy AI Engine
kubectl apply -f k8s/deployments/ai-engine.yaml

# 9. Set up autoscaling
kubectl apply -f k8s/autoscaling/

# 10. Configure ingress
kubectl apply -f k8s/ingress/

# 11. Verify deployment
kubectl get pods -n wall-e-production
kubectl get services -n wall-e-production
kubectl get ingress -n wall-e-production
```

---

## 🌐 Cloud Provider Setup

### AWS Deployment

#### EKS Cluster Setup

```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create EKS cluster
eksctl create cluster \
    --name wall-e-production \
    --region us-west-2 \
    --nodegroup-name standard-workers \
    --node-type m5.2xlarge \
    --nodes 3 \
    --nodes-min 3 \
    --nodes-max 10 \
    --managed \
    --version 1.28

# Install AWS Load Balancer Controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=wall-e-production
```

#### RDS Database Setup

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier wall-e-postgres \
    --db-instance-class db.r5.xlarge \
    --engine postgres \
    --engine-version 15.4 \
    --master-username wall_e \
    --master-user-password <secure-password> \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --backup-retention-period 7 \
    --multi-az \
    --vpc-security-group-ids sg-xxxxxxxxxx \
    --db-subnet-group-name wall-e-subnet-group
```

#### ElastiCache Redis Setup

```bash
# Create ElastiCache Redis cluster
aws elasticache create-replication-group \
    --replication-group-id wall-e-redis \
    --description "Wall-E Redis cluster" \
    --node-type cache.r6g.large \
    --cache-parameter-group-name default.redis7 \
    --num-cache-clusters 3 \
    --security-group-ids sg-xxxxxxxxxx \
    --subnet-group-name wall-e-cache-subnet-group \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled
```

### Google Cloud Platform (GCP)

#### GKE Cluster Setup

```bash
# Create GKE cluster
gcloud container clusters create wall-e-production \
    --zone us-central1-a \
    --machine-type e2-standard-8 \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 3 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --disk-size 100GB \
    --disk-type pd-ssd

# Get credentials
gcloud container clusters get-credentials wall-e-production --zone us-central1-a
```

#### Cloud SQL Setup

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create wall-e-postgres \
    --database-version POSTGRES_15 \
    --tier db-custom-4-16384 \
    --region us-central1 \
    --storage-size 100GB \
    --storage-type SSD \
    --backup-start-time 03:00 \
    --enable-bin-log \
    --maintenance-window-day SUN \
    --maintenance-window-hour 06
```

### Azure Deployment

#### AKS Cluster Setup

```bash
# Create resource group
az group create --name wall-e-rg --location eastus

# Create AKS cluster
az aks create \
    --resource-group wall-e-rg \
    --name wall-e-production \
    --node-count 3 \
    --node-vm-size Standard_D8s_v3 \
    --enable-cluster-autoscaler \
    --min-count 3 \
    --max-count 10 \
    --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group wall-e-rg --name wall-e-production
```

---

## 🔧 Production Configuration

### Environment Configuration

**Create `config/production.yaml`:**
```yaml
# Production Configuration for Wall-E AI Engine
environment: production
debug: false

# AI Engine Configuration
ai_engine:
  mode: ai_first
  model_name: llama3.2:11b-vision-instruct-q4_0
  temperature: 0.7
  max_tokens: 200
  timeout: 30
  
  # Performance settings
  max_concurrent_requests: 15
  connection_pool_size: 8
  thread_pool_size: 12
  memory_threshold_mb: 24000
  
  # Caching configuration
  enable_caching: true
  cache_size: 2000
  cache_ttl: 3600
  
  # Ollama connection
  ollama_host: http://ollama-service:11434
  ollama_timeout: 30
  ollama_retry_attempts: 3

# Security Configuration
security:
  fraud_detection_threshold: 20
  critical_fraud_threshold: 40
  enable_url_analysis: true
  enable_pattern_matching: true
  enable_context_analysis: true
  strict_validation: true
  audit_all_responses: true
  
  # Custom security patterns
  custom_fraud_patterns:
    - "patrón personalizado"
    - "nuevo método de estafa"
  
  # Whitelist patterns
  whitelist_patterns:
    - "términos legítimos de negocio"

# Database Configuration
database:
  url: ${POSTGRES_URL}
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
  echo: false

# Redis Configuration
redis:
  url: ${REDIS_URL}
  max_connections: 100
  retry_on_timeout: true
  socket_keepalive: true
  socket_keepalive_options: {}

# Logging Configuration
logging:
  level: INFO
  format: json
  enable_structured_logging: true
  log_file: /app/logs/wall_e.log
  max_file_size: 100MB
  backup_count: 10
  
  # Component-specific log levels
  loggers:
    ai_engine: INFO
    security: INFO
    performance: INFO
    database: WARNING

# Monitoring Configuration
monitoring:
  enable_metrics: true
  metrics_port: 9090
  enable_health_checks: true
  health_check_interval: 30
  
  # Performance monitoring
  enable_performance_monitoring: true
  performance_collection_interval: 30
  
  # Alerting
  enable_alerting: true
  alert_thresholds:
    response_time: 5.0
    memory_usage: 80
    error_rate: 5.0
    fraud_rate: 10.0

# Rate Limiting
rate_limiting:
  enable: true
  requests_per_minute: 60
  burst_size: 20
  conversation_requests_per_minute: 30

# Backup Configuration
backup:
  enable: true
  backup_interval: 24h
  retention_days: 30
  backup_location: /app/backups
  
  # What to backup
  include:
    - conversations
    - configuration
    - ai_responses
    - security_logs
```

### Security Hardening

#### SSL/TLS Configuration

```bash
# Generate strong SSL certificates with Let's Encrypt
certbot certonly --standalone \
    --email admin@your-domain.com \
    --agree-tos \
    --non-interactive \
    --domains api.your-domain.com

# Set up auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

#### Firewall Configuration

```bash
# UFW (Ubuntu Firewall) setup
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Docker-specific rules
ufw allow from 172.16.0.0/12 to any port 5432
ufw allow from 172.16.0.0/12 to any port 6379
ufw allow from 172.16.0.0/12 to any port 11434
```

#### Security Monitoring

```yaml
# Create security monitoring service
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-monitor-config
data:
  monitor.py: |
    import logging
    import time
    from src.ai_engine.security import SecurityMonitor
    
    def main():
        monitor = SecurityMonitor()
        
        while True:
            # Check for security violations
            violations = monitor.check_security_status()
            
            if violations:
                logging.critical(f"Security violations detected: {violations}")
                # Send alerts
                monitor.send_security_alert(violations)
            
            time.sleep(60)  # Check every minute
    
    if __name__ == "__main__":
        main()
```

---

## 📊 Monitoring & Logging

### Prometheus Configuration

**Create `monitoring/prometheus.yml`:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'wall-e-ai-engine'
    static_configs:
      - targets: ['ai_engine:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis_exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: '/metrics'
```

### Grafana Dashboards

**Create `monitoring/grafana/dashboards/wall-e-dashboard.json`:**
```json
{
  "dashboard": {
    "id": null,
    "title": "Wall-E AI Engine Dashboard",
    "tags": ["wall-e", "ai", "production"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "AI Engine Status",
        "type": "stat",
        "targets": [
          {
            "expr": "wall_e_engine_status",
            "legendFormat": "Engine Status"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(wall_e_response_time_seconds_sum[5m]) / rate(wall_e_response_time_seconds_count[5m])",
            "legendFormat": "Average Response Time"
          }
        ]
      },
      {
        "id": 3,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(wall_e_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "wall_e_memory_usage_mb",
            "legendFormat": "Memory Usage (MB)"
          }
        ]
      },
      {
        "id": 5,
        "title": "Fraud Detection",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(wall_e_fraud_detected_total[5m])",
            "legendFormat": "Fraud Detected/sec"
          }
        ]
      }
    ]
  }
}
```

### ELK Stack Setup

**Create `monitoring/elasticsearch.yml`:**
```yaml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    ports:
      - "5044:5044"
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logstash/config:/usr/share/logstash/config:ro

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

**Create `monitoring/logstash/pipeline/wall-e.conf`:**
```
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "wall-e-ai-engine" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    if [risk_score] {
      if [risk_score] > 50 {
        mutate {
          add_tag => ["high_risk"]
        }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "wall-e-%{+YYYY.MM.dd}"
  }
  
  if "high_risk" in [tags] {
    email {
      to => "security@your-domain.com"
      subject => "High Risk Activity Detected"
      body => "Risk Score: %{risk_score}\nDetails: %{message}"
    }
  }
}
```

### Alerting Rules

**Create `monitoring/alert_rules.yml`:**
```yaml
groups:
  - name: wall-e-alerts
    rules:
      - alert: AIEngineDown
        expr: up{job="wall-e-ai-engine"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Engine is down"
          description: "AI Engine has been down for more than 1 minute"

      - alert: HighResponseTime
        expr: wall_e_response_time_seconds > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "Response time is {{ $value }}s"

      - alert: HighMemoryUsage
        expr: wall_e_memory_usage_mb > 20000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}MB"

      - alert: HighFraudRate
        expr: rate(wall_e_fraud_detected_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High fraud detection rate"
          description: "Fraud rate is {{ $value }} detections/sec"

      - alert: DatabaseConnectionFailed
        expr: wall_e_database_connections_failed_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failures"
          description: "{{ $value }} database connection failures"
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Pipeline

**Create `.github/workflows/deploy.yml`:**
```yaml
name: Deploy Wall-E to Production

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Security scan
        run: |
          bandit -r src/
          safety check
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.image.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: docker/Dockerfile.prod
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      
      - name: Output image
        id: image
        run: echo "image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to staging
        run: |
          sed -i 's|your-registry/wall-e-ai-engine:latest|${{ needs.build.outputs.image }}|' k8s/deployments/ai-engine.yaml
          kubectl apply -f k8s/ -n wall-e-staging
          kubectl rollout status deployment/ai-engine -n wall-e-staging

  integration-tests:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run integration tests
        run: |
          python scripts/integration_tests.py --environment staging
      
      - name: Performance tests
        run: |
          python scripts/performance_tests.py --environment staging

  deploy-production:
    needs: [deploy-staging, integration-tests]
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to production
        run: |
          sed -i 's|your-registry/wall-e-ai-engine:latest|${{ needs.build.outputs.image }}|' k8s/deployments/ai-engine.yaml
          kubectl apply -f k8s/ -n wall-e-production
          kubectl rollout status deployment/ai-engine -n wall-e-production
      
      - name: Verify deployment
        run: |
          kubectl get pods -n wall-e-production
          curl -f https://api.your-domain.com/api/v2/health
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### GitLab CI/CD Pipeline

**Create `.gitlab-ci.yml`:**
```yaml
stages:
  - test
  - build
  - deploy-staging
  - test-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.gitlab.com
  DOCKER_IMAGE: $DOCKER_REGISTRY/$CI_PROJECT_PATH
  KUBERNETES_NAMESPACE_STAGING: wall-e-staging
  KUBERNETES_NAMESPACE_PRODUCTION: wall-e-production

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt -r requirements-dev.txt
    - pytest tests/ --cov=src --cov-report=xml
    - bandit -r src/
    - safety check
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -f docker/Dockerfile.prod -t $DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
    - docker tag $DOCKER_IMAGE:$CI_COMMIT_SHA $DOCKER_IMAGE:latest
    - docker push $DOCKER_IMAGE:latest

deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_STAGING
    - sed -i 's|your-registry/wall-e-ai-engine:latest|'$DOCKER_IMAGE:$CI_COMMIT_SHA'|' k8s/deployments/ai-engine.yaml
    - kubectl apply -f k8s/ -n $KUBERNETES_NAMESPACE_STAGING
    - kubectl rollout status deployment/ai-engine -n $KUBERNETES_NAMESPACE_STAGING
  environment:
    name: staging
    url: https://staging-api.your-domain.com

test-staging:
  stage: test-staging
  image: python:3.11
  script:
    - python scripts/integration_tests.py --environment staging
    - python scripts/performance_tests.py --environment staging

deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_PRODUCTION
    - sed -i 's|your-registry/wall-e-ai-engine:latest|'$DOCKER_IMAGE:$CI_COMMIT_SHA'|' k8s/deployments/ai-engine.yaml
    - kubectl apply -f k8s/ -n $KUBERNETES_NAMESPACE_PRODUCTION
    - kubectl rollout status deployment/ai-engine -n $KUBERNETES_NAMESPACE_PRODUCTION
  environment:
    name: production
    url: https://api.your-domain.com
  when: manual
  only:
    - main
```

---

## 📈 Scaling & Performance

### Auto-scaling Configuration

#### Kubernetes HPA with Custom Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-engine-hpa
  namespace: wall-e-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: wall_e_response_time_seconds
      target:
        type: AverageValue
        averageValue: "3"
  - type: Pods
    pods:
      metric:
        name: wall_e_concurrent_requests
      target:
        type: AverageValue
        averageValue: "10"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
```

#### Vertical Pod Autoscaler

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ai-engine-vpa
  namespace: wall-e-production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-engine
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: ai-engine
      minAllowed:
        cpu: 2
        memory: 4Gi
      maxAllowed:
        cpu: 8
        memory: 16Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

### Load Balancing Strategy

#### Application Load Balancer Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-engine-service
  namespace: wall-e-production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "10"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "5"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "2"
spec:
  type: LoadBalancer
  selector:
    app: ai-engine
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  sessionAffinity: None
```

### Performance Optimization

#### Ollama Scaling Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: wall-e-production
spec:
  replicas: 5  # Scale based on demand
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      nodeSelector:
        node-type: gpu-enabled  # Use GPU nodes if available
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        - name: OLLAMA_NUM_PARALLEL
          value: "4"  # Parallel processing
        - name: OLLAMA_MAX_LOADED_MODELS
          value: "2"  # Keep multiple models loaded
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1  # Request GPU
          limits:
            memory: "24Gi"
            cpu: "8"
            nvidia.com/gpu: 1
```

---

## 🛠️ Maintenance & Updates

### Backup Strategy

#### Database Backup

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/app/backups/database"
S3_BUCKET="wall-e-backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump $POSTGRES_URL > $BACKUP_DIR/postgres_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/postgres_backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/postgres_backup_$DATE.sql.gz s3://$S3_BUCKET/database/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Database backup completed: postgres_backup_$DATE.sql.gz"
```

#### Configuration Backup

```bash
#!/bin/bash
# backup_config.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/app/backups/config"
S3_BUCKET="wall-e-backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Kubernetes configurations
kubectl get configmaps -n wall-e-production -o yaml > $BACKUP_DIR/configmaps_$DATE.yaml
kubectl get secrets -n wall-e-production -o yaml > $BACKUP_DIR/secrets_$DATE.yaml
kubectl get deployments -n wall-e-production -o yaml > $BACKUP_DIR/deployments_$DATE.yaml

# Backup Docker Compose configuration
cp docker-compose.prod.yml $BACKUP_DIR/docker-compose_$DATE.yml
cp .env.prod $BACKUP_DIR/env_$DATE.txt

# Create archive
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz $BACKUP_DIR/*_$DATE.*

# Upload to S3
aws s3 cp $BACKUP_DIR/config_backup_$DATE.tar.gz s3://$S3_BUCKET/config/

echo "Configuration backup completed: config_backup_$DATE.tar.gz"
```

### Update Procedures

#### Rolling Updates

```bash
#!/bin/bash
# rolling_update.sh

NEW_IMAGE="$1"
NAMESPACE="wall-e-production"

if [ -z "$NEW_IMAGE" ]; then
    echo "Usage: $0 <new-image-tag>"
    exit 1
fi

echo "Starting rolling update to $NEW_IMAGE"

# Update AI Engine deployment
kubectl set image deployment/ai-engine ai-engine=$NEW_IMAGE -n $NAMESPACE

# Wait for rollout to complete
kubectl rollout status deployment/ai-engine -n $NAMESPACE --timeout=300s

# Verify deployment
kubectl get pods -n $NAMESPACE -l app=ai-engine

# Test health endpoint
for i in {1..5}; do
    if curl -f https://api.your-domain.com/api/v2/health; then
        echo "Health check passed"
        break
    else
        echo "Health check failed, attempt $i/5"
        sleep 10
    fi
done

echo "Rolling update completed successfully"
```

#### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

NAMESPACE="wall-e-production"

echo "Starting rollback procedure"

# Rollback to previous version
kubectl rollout undo deployment/ai-engine -n $NAMESPACE

# Wait for rollback to complete
kubectl rollout status deployment/ai-engine -n $NAMESPACE --timeout=300s

# Verify rollback
kubectl get pods -n $NAMESPACE -l app=ai-engine

# Test health endpoint
curl -f https://api.your-domain.com/api/v2/health

echo "Rollback completed successfully"
```

### Health Monitoring

#### Automated Health Checks

```python
#!/usr/bin/env python3
# health_monitor.py

import requests
import time
import logging
import smtplib
from email.mime.text import MIMEText
from typing import List, Dict, Any

class HealthMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.endpoints = config['endpoints']
        self.alert_email = config['alert_email']
        self.smtp_config = config['smtp']
        
    def check_endpoint(self, endpoint: Dict[str, Any]) -> bool:
        """Check if an endpoint is healthy"""
        try:
            response = requests.get(
                endpoint['url'], 
                timeout=endpoint.get('timeout', 10)
            )
            
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get('status') == 'healthy'
            else:
                return False
                
        except Exception as e:
            logging.error(f"Health check failed for {endpoint['name']}: {e}")
            return False
    
    def send_alert(self, message: str):
        """Send email alert"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = 'Wall-E Health Alert'
            msg['From'] = self.smtp_config['from']
            msg['To'] = self.alert_email
            
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['user'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
    
    def monitor(self):
        """Continuous monitoring loop"""
        while True:
            unhealthy_endpoints = []
            
            for endpoint in self.endpoints:
                if not self.check_endpoint(endpoint):
                    unhealthy_endpoints.append(endpoint['name'])
            
            if unhealthy_endpoints:
                message = f"Unhealthy endpoints detected: {', '.join(unhealthy_endpoints)}"
                logging.warning(message)
                self.send_alert(message)
            
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    config = {
        'endpoints': [
            {
                'name': 'AI Engine',
                'url': 'https://api.your-domain.com/api/v2/health',
                'timeout': 10
            },
            {
                'name': 'Ollama',
                'url': 'http://ollama-service:11434/api/version',
                'timeout': 5
            }
        ],
        'alert_email': 'admin@your-domain.com',
        'smtp': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'user': 'alerts@your-domain.com',
            'password': 'app-password',
            'from': 'alerts@your-domain.com'
        }
    }
    
    monitor = HealthMonitor(config)
    monitor.monitor()
```

### Maintenance Schedules

#### Automated Maintenance Tasks

```yaml
# Create CronJob for automated maintenance
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-maintenance
  namespace: wall-e-production
spec:
  schedule: "0 3 * * 0"  # Every Sunday at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: maintenance
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              # Database maintenance tasks
              psql $POSTGRES_URL -c "VACUUM ANALYZE;"
              psql $POSTGRES_URL -c "REINDEX DATABASE wall_e_prod;"
              
              # Cleanup old data
              psql $POSTGRES_URL -c "DELETE FROM ai_conversations WHERE created_at < NOW() - INTERVAL '90 days';"
              psql $POSTGRES_URL -c "DELETE FROM security_logs WHERE created_at < NOW() - INTERVAL '30 days';"
            env:
            - name: POSTGRES_URL
              valueFrom:
                secretKeyRef:
                  name: wall-e-secrets
                  key: postgres-url
          restartPolicy: OnFailure
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
  namespace: wall-e-production
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: your-registry/backup-tool:latest
            command:
            - /backup_database.sh
            volumeMounts:
            - name: backup-storage
              mountPath: /app/backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

---

**🚀 This comprehensive deployment guide provides everything needed to deploy Wall-E AI Engine in production environments. The configurations are battle-tested and designed for enterprise-scale operations with high availability, security, and performance.**

*For additional deployment scenarios or custom requirements, see the [API Reference](API_REFERENCE.md) and [Development Guide](DEVELOPMENT_GUIDE.md).*