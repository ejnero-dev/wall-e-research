#!/bin/bash

# Deployment Automation Setup Script
# Creates comprehensive deployment configurations for both repositories

set -euo pipefail

# Configuration
BASE_DIR="${PWD}"
RESEARCH_REPO="wall-e-research"
COMPLIANCE_REPO="wall-e-compliance"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create Docker Compose configurations
create_docker_compose_configs() {
    log "Creating Docker Compose configurations..."
    
    # Research Docker Compose
    mkdir -p "${BASE_DIR}/configs/research"
    cat > "${BASE_DIR}/configs/research/docker-compose.research.yml" << 'EOF'
version: '3.8'

services:
  # Research Application
  wall-e-research:
    build:
      context: .
      dockerfile: docker/Dockerfile.research
    container_name: wall-e-research-app
    environment:
      - RESEARCH_MODE=true
      - EDUCATIONAL_MODE=true
      - DEBUG=true
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=wallapop_research
      - POSTGRES_USER=research_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-research_password}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - research_data:/app/data
    networks:
      - research_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.research.rule=Host(`research.localhost`)"
      - "traefik.http.services.research.loadbalancer.server.port=8000"

  # PostgreSQL for Research
  postgres:
    image: postgres:15-alpine
    container_name: wall-e-research-postgres
    environment:
      POSTGRES_DB: wallapop_research
      POSTGRES_USER: research_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-research_password}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_research_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql:ro
    networks:
      - research_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U research_user -d wallapop_research"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for Research
  redis:
    image: redis:7-alpine
    container_name: wall-e-research-redis
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_research_data:/data
    networks:
      - research_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Research Web Dashboard (Optional)
  research-dashboard:
    build:
      context: ./frontend
      dockerfile: Dockerfile.research
    container_name: wall-e-research-dashboard
    environment:
      - REACT_APP_API_URL=http://wall-e-research:8000/api
      - REACT_APP_MODE=research
    ports:
      - "3000:3000"
    networks:
      - research_network
    depends_on:
      - wall-e-research
    restart: unless-stopped
    profiles:
      - dashboard

  # Jupyter Notebook for Research (Optional)
  jupyter:
    image: jupyter/datascience-notebook:latest
    container_name: wall-e-research-jupyter
    environment:
      - JUPYTER_ENABLE_LAB=yes
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - research_data:/home/jovyan/data
    networks:
      - research_network
    restart: unless-stopped
    profiles:
      - research-tools

  # Monitoring Stack for Research
  prometheus:
    image: prom/prometheus:latest
    container_name: wall-e-research-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus-research.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_research_data:/prometheus
    networks:
      - research_network
    restart: unless-stopped
    profiles:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: wall-e-research-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-research123}
    ports:
      - "3001:3000"
    volumes:
      - grafana_research_data:/var/lib/grafana
      - ./monitoring/grafana-research-dashboards:/etc/grafana/provisioning/dashboards:ro
    networks:
      - research_network
    depends_on:
      - prometheus
    restart: unless-stopped
    profiles:
      - monitoring

volumes:
  postgres_research_data:
    driver: local
  redis_research_data:
    driver: local
  research_data:
    driver: local
  prometheus_research_data:
    driver: local
  grafana_research_data:
    driver: local

networks:
  research_network:
    driver: bridge
    labels:
      - "purpose=research"
      - "educational=true"
EOF

    # Compliance Docker Compose (Production-ready)
    mkdir -p "${BASE_DIR}/configs/compliance"
    cat > "${BASE_DIR}/configs/compliance/docker-compose.compliance.yml" << 'EOF'
version: '3.8'

services:
  # Compliance Application
  wall-e-compliance:
    build:
      context: .
      dockerfile: docker/Dockerfile.compliance
    container_name: wall-e-compliance-app
    environment:
      - COMPLIANCE_MODE=true
      - PRODUCTION_MODE=true
      - DEBUG=false
      - SSL_VERIFY=true
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=wallapop_compliance
      - POSTGRES_USER=${POSTGRES_USER:-compliance_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - COMPANY_NAME=${COMPANY_NAME}
      - COMPANY_EMAIL=${COMPANY_EMAIL}
    volumes:
      - ./config/config.compliance.yaml:/app/config/config.yaml:ro
      - compliance_logs:/app/logs
      - compliance_data:/app/data
      - ./ssl:/app/ssl:ro  # SSL certificates
    networks:
      - compliance_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.compliance.rule=Host(`${DOMAIN_NAME:-compliance.localhost}`)"
      - "traefik.http.routers.compliance.tls=true"
      - "traefik.http.services.compliance.loadbalancer.server.port=8000"
      - "compliance.version=1.0.0"
      - "compliance.gdpr=true"
      - "compliance.audit=true"

  # PostgreSQL for Compliance (Encrypted)
  postgres:
    image: postgres:15-alpine
    container_name: wall-e-compliance-postgres
    environment:
      POSTGRES_DB: wallapop_compliance
      POSTGRES_USER: ${POSTGRES_USER:-compliance_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --auth-host=md5"
    volumes:
      - postgres_compliance_data:/var/lib/postgresql/data
      - ./scripts/init_compliance_db.sql:/docker-entrypoint-initdb.d/init_db.sql:ro
      - ./ssl/postgres:/var/lib/postgresql/ssl:ro
    networks:
      - compliance_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-compliance_user} -d wallapop_compliance"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: >
      postgres 
      -c ssl=on 
      -c ssl_cert_file=/var/lib/postgresql/ssl/server.crt
      -c ssl_key_file=/var/lib/postgresql/ssl/server.key
      -c log_statement=all
      -c log_connections=on
      -c log_disconnections=on

  # Redis for Compliance (Encrypted)
  redis:
    image: redis:7-alpine
    container_name: wall-e-compliance-redis
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    volumes:
      - redis_compliance_data:/data
      - ./config/redis-compliance.conf:/usr/local/etc/redis/redis.conf:ro
      - ./ssl/redis:/etc/ssl/redis:ro
    networks:
      - compliance_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.125'
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "--tls", "--cert", "/etc/ssl/redis/client.crt", "--key", "/etc/ssl/redis/client.key", "--cacert", "/etc/ssl/redis/ca.crt", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Compliance Dashboard
  compliance-dashboard:
    build:
      context: ./frontend
      dockerfile: Dockerfile.compliance
    container_name: wall-e-compliance-dashboard
    environment:
      - REACT_APP_API_URL=https://${DOMAIN_NAME:-compliance.localhost}/api
      - REACT_APP_MODE=compliance
      - REACT_APP_COMPLIANCE_MODE=true
      - NODE_ENV=production
    networks:
      - compliance_network
    depends_on:
      - wall-e-compliance
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`dashboard.${DOMAIN_NAME:-compliance.localhost}`)"
      - "traefik.http.routers.dashboard.tls=true"

  # Human Approval Service
  human-approval:
    build:
      context: ./services/human-approval
      dockerfile: Dockerfile
    container_name: wall-e-human-approval
    environment:
      - COMPLIANCE_MODE=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=wallapop_compliance
      - POSTGRES_USER=${POSTGRES_USER:-compliance_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - NOTIFICATION_EMAIL=${NOTIFICATION_EMAIL}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    networks:
      - compliance_network
    depends_on:
      - postgres
    restart: unless-stopped
    labels:
      - "compliance.service=human-approval"
      - "compliance.critical=true"

  # Audit Logger Service
  audit-logger:
    build:
      context: ./services/audit-logger
      dockerfile: Dockerfile
    container_name: wall-e-audit-logger
    environment:
      - COMPLIANCE_MODE=true
      - LOG_LEVEL=INFO
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=wallapop_compliance
      - POSTGRES_USER=${POSTGRES_USER:-compliance_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - compliance_logs:/app/logs
      - audit_logs:/app/audit-logs
    networks:
      - compliance_network
    depends_on:
      - postgres
    restart: unless-stopped
    labels:
      - "compliance.service=audit-logger"
      - "compliance.critical=true"

  # GDPR Compliance Service
  gdpr-service:
    build:
      context: ./services/gdpr
      dockerfile: Dockerfile
    container_name: wall-e-gdpr-service
    environment:
      - COMPLIANCE_MODE=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=wallapop_compliance
      - POSTGRES_USER=${POSTGRES_USER:-compliance_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - DATA_RETENTION_DAYS=30
      - DELETION_SCHEDULE=0 2 * * *  # Daily at 2 AM
    networks:
      - compliance_network
    depends_on:
      - postgres
    restart: unless-stopped
    labels:
      - "compliance.service=gdpr"
      - "compliance.gdpr=true"

  # Reverse Proxy with SSL
  traefik:
    image: traefik:v3.0
    container_name: wall-e-compliance-proxy
    command:
      - "--api.dashboard=true"
      - "--api.insecure=false"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt_data:/letsencrypt
    networks:
      - compliance_network
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`traefik.${DOMAIN_NAME:-compliance.localhost}`)"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.routers.api.service=api@internal"

  # Monitoring Stack (Production)
  prometheus:
    image: prom/prometheus:latest
    container_name: wall-e-compliance-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus-compliance.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_compliance_data:/prometheus
    networks:
      - compliance_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prometheus.rule=Host(`metrics.${DOMAIN_NAME:-compliance.localhost}`)"
      - "traefik.http.routers.prometheus.tls=true"

  grafana:
    image: grafana/grafana:latest
    container_name: wall-e-compliance-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SECURITY_SECRET_KEY=${GRAFANA_SECRET_KEY}
      - GF_SERVER_DOMAIN=${DOMAIN_NAME:-compliance.localhost}
      - GF_SERVER_ROOT_URL=https://grafana.${DOMAIN_NAME:-compliance.localhost}
      - GF_DATABASE_TYPE=postgres
      - GF_DATABASE_HOST=postgres:5432
      - GF_DATABASE_NAME=wallapop_compliance
      - GF_DATABASE_USER=${POSTGRES_USER:-compliance_user}
      - GF_DATABASE_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - grafana_compliance_data:/var/lib/grafana
      - ./monitoring/grafana-compliance-dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro
    networks:
      - compliance_network
    depends_on:
      - prometheus
      - postgres
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.${DOMAIN_NAME:-compliance.localhost}`)"
      - "traefik.http.routers.grafana.tls=true"

  # Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: wall-e-compliance-loki
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./monitoring/loki-compliance.yml:/etc/loki/local-config.yaml:ro
      - loki_compliance_data:/loki
    networks:
      - compliance_network
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: wall-e-compliance-promtail
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./monitoring/promtail-compliance.yml:/etc/promtail/config.yml:ro
      - compliance_logs:/var/log/app:ro
      - audit_logs:/var/log/audit:ro
      - /var/log:/var/log/host:ro
    networks:
      - compliance_network
    depends_on:
      - loki
    restart: unless-stopped

volumes:
  postgres_compliance_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/wall-e-compliance/data/postgres
  redis_compliance_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/wall-e-compliance/data/redis
  compliance_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/wall-e-compliance/logs
  audit_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/wall-e-compliance/audit-logs
  compliance_data:
    driver: local
  prometheus_compliance_data:
    driver: local
  grafana_compliance_data:
    driver: local
  loki_compliance_data:
    driver: local
  letsencrypt_data:
    driver: local

networks:
  compliance_network:
    driver: bridge
    labels:
      - "purpose=compliance"
      - "commercial=true"
      - "gdpr=true"
EOF
}

# Create Kubernetes configurations
create_kubernetes_configs() {
    log "Creating Kubernetes configurations..."
    
    # Research Kubernetes config
    mkdir -p "${BASE_DIR}/configs/research/k8s"
    
    cat > "${BASE_DIR}/configs/research/k8s/namespace.yaml" << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: wall-e-research
  labels:
    purpose: research
    educational: "true"
    environment: development
EOF

    cat > "${BASE_DIR}/configs/research/k8s/configmap.yaml" << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: wall-e-research-config
  namespace: wall-e-research
data:
  RESEARCH_MODE: "true"
  EDUCATIONAL_MODE: "true"
  DEBUG: "true"
  POSTGRES_HOST: "postgres-service"
  POSTGRES_PORT: "5432"
  POSTGRES_DB: "wallapop_research"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
EOF

    # Compliance Kubernetes config
    mkdir -p "${BASE_DIR}/configs/compliance/k8s"
    
    cat > "${BASE_DIR}/configs/compliance/k8s/namespace.yaml" << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: wall-e-compliance
  labels:
    purpose: compliance
    commercial: "true"
    gdpr: "true"
    environment: production
  annotations:
    compliance.version: "1.0.0"
    gdpr.compliant: "true"
    security.audited: "true"
EOF

    cat > "${BASE_DIR}/configs/compliance/k8s/secrets.yaml" << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: wall-e-compliance-secrets
  namespace: wall-e-compliance
type: Opaque
stringData:
  POSTGRES_PASSWORD: "REPLACE_WITH_SECURE_PASSWORD"
  REDIS_PASSWORD: "REPLACE_WITH_SECURE_PASSWORD"
  ENCRYPTION_KEY: "REPLACE_WITH_SECURE_ENCRYPTION_KEY"
  JWT_SECRET: "REPLACE_WITH_SECURE_JWT_SECRET"
  GRAFANA_PASSWORD: "REPLACE_WITH_SECURE_GRAFANA_PASSWORD"
  SMTP_PASSWORD: "REPLACE_WITH_SMTP_PASSWORD"
EOF

    cat > "${BASE_DIR}/configs/compliance/k8s/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wall-e-compliance
  namespace: wall-e-compliance
  labels:
    app: wall-e-compliance
    compliance: "true"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wall-e-compliance
  template:
    metadata:
      labels:
        app: wall-e-compliance
        compliance: "true"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: wall-e-compliance
        image: ghcr.io/USERNAME/wall-e-compliance:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: COMPLIANCE_MODE
          value: "true"
        - name: PRODUCTION_MODE
          value: "true"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wall-e-compliance-secrets
              key: POSTGRES_PASSWORD
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wall-e-compliance-secrets
              key: REDIS_PASSWORD
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: wall-e-compliance-secrets
              key: ENCRYPTION_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
EOF
}

# Create deployment scripts
create_deployment_scripts() {
    log "Creating deployment scripts..."
    
    # Research deployment script
    cat > "${BASE_DIR}/scripts/deploy-research.sh" << 'EOF'
#!/bin/bash

# Research Deployment Script
set -euo pipefail

# Configuration
ENVIRONMENT="${1:-development}"
COMPOSE_FILE="${2:-docker-compose.research.yml}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks for research environment..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check configuration files
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
    fi
    
    # Check environment variables
    if [[ -f ".env.research" ]]; then
        source .env.research
        log "Loaded research environment variables"
    else
        warn "No .env.research file found, using defaults"
    fi
    
    log "Pre-deployment checks passed"
}

# Deploy research environment
deploy_research() {
    log "Deploying research environment..."
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build and start services
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "unhealthy"; then
        error "Some services are unhealthy"
    fi
    
    log "Research environment deployed successfully"
}

# Post-deployment setup
post_deployment_setup() {
    log "Running post-deployment setup..."
    
    # Initialize database
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-research python scripts/init_database.py
    
    # Run database migrations
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-research python scripts/migrate.py
    
    # Load sample data for research
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-research python scripts/load_sample_data.py
    
    log "Post-deployment setup completed"
}

# Display deployment info
display_deployment_info() {
    log "Research deployment information:"
    echo ""
    echo "🔬 Research Application: http://localhost:8000"
    echo "📊 Dashboard: http://localhost:3000"
    echo "📓 Jupyter Notebook: http://localhost:8888"
    echo "📈 Prometheus: http://localhost:9090"
    echo "📊 Grafana: http://localhost:3001"
    echo ""
    echo "🔍 View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "🛑 Stop services: docker-compose -f $COMPOSE_FILE down"
    echo ""
    echo "🎓 Educational Mode: ENABLED"
    echo "🔬 Research Features: ENABLED"
    echo "⚠️  Rate Limits: CONFIGURABLE (for research purposes)"
}

# Main execution
main() {
    log "Starting research deployment process..."
    
    pre_deployment_checks
    deploy_research
    post_deployment_setup
    display_deployment_info
    
    log "Research deployment completed successfully!"
}

main "$@"
EOF

    # Compliance deployment script
    cat > "${BASE_DIR}/scripts/deploy-compliance.sh" << 'EOF'
#!/bin/bash

# Compliance Deployment Script (Production)
set -euo pipefail

# Configuration
ENVIRONMENT="${1:-production}"
COMPOSE_FILE="${2:-docker-compose.compliance.yml}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Strict pre-deployment checks for compliance
pre_deployment_checks() {
    log "Running STRICT pre-deployment checks for compliance environment..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check configuration files
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
    fi
    
    if [[ ! -f "config/config.compliance.yaml" ]]; then
        error "Compliance configuration file not found"
    fi
    
    # Check environment variables (REQUIRED)
    required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD" 
        "ENCRYPTION_KEY"
        "JWT_SECRET"
        "COMPANY_NAME"
        "COMPANY_EMAIL"
        "DOMAIN_NAME"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable not set: $var"
        fi
    done
    
    # Check SSL certificates
    if [[ ! -d "ssl" ]]; then
        error "SSL certificates directory not found"
    fi
    
    # Validate compliance configuration
    if ! python scripts/verify_compliance.py; then
        error "Compliance configuration validation failed"
    fi
    
    # Check disk space (minimum 10GB)
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        error "Insufficient disk space for compliance deployment"
    fi
    
    log "STRICT pre-deployment checks passed"
}

# Create production directories
create_production_directories() {
    log "Creating production directories..."
    
    # Create data directories with proper permissions
    sudo mkdir -p /opt/wall-e-compliance/{data/{postgres,redis},logs,audit-logs}
    sudo chown -R 1000:1000 /opt/wall-e-compliance
    sudo chmod -R 750 /opt/wall-e-compliance
    
    # Set SELinux contexts if available
    if command -v semanage &> /dev/null; then
        sudo semanage fcontext -a -t container_file_t "/opt/wall-e-compliance(/.*)?" || true
        sudo restorecon -R /opt/wall-e-compliance || true
    fi
    
    log "Production directories created"
}

# Deploy compliance environment
deploy_compliance() {
    log "Deploying compliance environment with STRICT security..."
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build and start services
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 60  # Longer wait for production services
    
    # Check service health with retries
    for i in {1..5}; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "unhealthy"; then
            if [[ $i -eq 5 ]]; then
                error "Services failed to become healthy after 5 attempts"
            fi
            warn "Services not healthy yet, retrying in 30 seconds... (attempt $i/5)"
            sleep 30
        else
            break
        fi
    done
    
    log "Compliance environment deployed successfully"
}

# Post-deployment compliance setup
post_deployment_setup() {
    log "Running post-deployment compliance setup..."
    
    # Initialize compliance database
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-compliance python scripts/init_compliance_db.py
    
    # Run database migrations
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-compliance python scripts/migrate.py
    
    # Initialize compliance services
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-compliance python scripts/init_compliance_services.py
    
    # Verify compliance configuration
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-compliance python scripts/verify_compliance.py
    
    # Run compliance tests
    docker-compose -f "$COMPOSE_FILE" exec -T wall-e-compliance python -m pytest tests/compliance/ -v
    
    log "Post-deployment compliance setup completed"
}

# Security hardening
security_hardening() {
    log "Applying security hardening..."
    
    # Set up log rotation
    sudo tee /etc/logrotate.d/wall-e-compliance > /dev/null << 'LOGROTATE'
/opt/wall-e-compliance/logs/*.log {
    daily
    missingok
    rotate 365
    compress
    delaycompress
    notifempty
    copytruncate
}

/opt/wall-e-compliance/audit-logs/*.log {
    daily
    missingok
    rotate 2555  # 7 years
    compress
    delaycompress
    notifempty
    copytruncate
}
LOGROTATE
    
    # Set up fail2ban for additional protection
    if command -v fail2ban-server &> /dev/null; then
        sudo tee /etc/fail2ban/jail.d/wall-e-compliance.conf > /dev/null << 'FAIL2BAN'
[wall-e-compliance]
enabled = true
port = 80,443
filter = wall-e-compliance
logpath = /opt/wall-e-compliance/logs/access.log
maxretry = 3
bantime = 3600
FAIL2BAN
        sudo systemctl reload fail2ban
    fi
    
    log "Security hardening applied"
}

# Display compliance deployment info
display_deployment_info() {
    log "Compliance deployment information:"
    echo ""
    echo "🏛️ Compliance Application: https://${DOMAIN_NAME}"
    echo "📊 Dashboard: https://dashboard.${DOMAIN_NAME}"
    echo "📈 Metrics: https://metrics.${DOMAIN_NAME}"
    echo "📊 Grafana: https://grafana.${DOMAIN_NAME}"
    echo "🔧 Traefik: https://traefik.${DOMAIN_NAME}"
    echo ""
    echo "🔍 View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "🛑 Stop services: docker-compose -f $COMPOSE_FILE down"
    echo ""
    echo "🏛️ Compliance Mode: ENABLED"
    echo "🔒 Security: HARDENED"
    echo "📋 GDPR: COMPLIANT"
    echo "👤 Human Approval: REQUIRED"
    echo "⚡ Rate Limits: 5 messages/hour MAX"
    echo "📊 Audit Logging: COMPREHENSIVE"
    echo ""
    warn "IMPORTANT: This is a production compliance deployment"
    warn "All actions are logged and monitored"
    warn "Human approval is required for critical operations"
}

# Main execution
main() {
    log "Starting COMPLIANCE deployment process..."
    
    if [[ "$ENVIRONMENT" != "production" ]]; then
        warn "Deployment environment is not 'production', but compliance mode is active"
    fi
    
    pre_deployment_checks
    create_production_directories
    deploy_compliance
    post_deployment_setup
    security_hardening
    display_deployment_info
    
    log "COMPLIANCE deployment completed successfully!"
    log "🏛️ System is now ready for commercial use with full compliance"
}

main "$@"
EOF

    # Make scripts executable
    chmod +x "${BASE_DIR}/scripts/deploy-research.sh"
    chmod +x "${BASE_DIR}/scripts/deploy-compliance.sh"
}

# Create monitoring configurations
create_monitoring_configs() {
    log "Creating monitoring configurations..."
    
    # Research monitoring
    mkdir -p "${BASE_DIR}/configs/research/monitoring"
    
    cat > "${BASE_DIR}/configs/research/monitoring/prometheus-research.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "research_rules.yml"

scrape_configs:
  - job_name: 'wall-e-research'
    static_configs:
      - targets: ['wall-e-research:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres-research'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 60s

  - job_name: 'redis-research'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 60s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF

    # Compliance monitoring (more comprehensive)
    mkdir -p "${BASE_DIR}/configs/compliance/monitoring"
    
    cat > "${BASE_DIR}/configs/compliance/monitoring/prometheus-compliance.yml" << 'EOF'
global:
  scrape_interval: 10s
  evaluation_interval: 10s
  external_labels:
    environment: 'production'
    compliance: 'true'

rule_files:
  - "compliance_rules.yml"
  - "security_rules.yml"
  - "gdpr_rules.yml"

scrape_configs:
  - job_name: 'wall-e-compliance'
    static_configs:
      - targets: ['wall-e-compliance:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s

  - job_name: 'human-approval'
    static_configs:
      - targets: ['human-approval:8001']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'audit-logger'
    static_configs:
      - targets: ['audit-logger:8002']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'gdpr-service'
    static_configs:
      - targets: ['gdpr-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres-compliance'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis-compliance'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8080']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      path_prefix: /alertmanager
      scheme: https
EOF

    # Compliance alerting rules
    cat > "${BASE_DIR}/configs/compliance/monitoring/compliance_rules.yml" << 'EOF'
groups:
  - name: compliance.rules
    rules:
    - alert: RateLimitExceeded
      expr: rate_limit_violations_total > 0
      for: 0m
      labels:
        severity: critical
        compliance: violation
      annotations:
        summary: "Rate limit exceeded"
        description: "Rate limits have been exceeded, potential compliance violation"

    - alert: HumanApprovalTimeout
      expr: human_approval_timeout_total > 0
      for: 0m
      labels:
        severity: warning
        compliance: attention
      annotations:
        summary: "Human approval timeout"
        description: "Human approval requests are timing out"

    - alert: UnauthorizedAccess
      expr: unauthorized_access_attempts_total > 0
      for: 0m
      labels:
        severity: critical
        security: violation
      annotations:
        summary: "Unauthorized access attempt"
        description: "Unauthorized access attempts detected"

    - alert: GDPRViolation
      expr: gdpr_violations_total > 0
      for: 0m
      labels:
        severity: critical
        gdpr: violation
      annotations:
        summary: "GDPR violation detected"
        description: "Potential GDPR compliance violation"

    - alert: AuditLogFailure
      expr: audit_log_failures_total > 0
      for: 0m
      labels:
        severity: critical
        audit: failure
      annotations:
        summary: "Audit logging failure"
        description: "Audit logging system failure detected"
EOF
}

# Main execution
main() {
    log "Creating deployment automation for dual repository strategy..."
    
    create_docker_compose_configs
    create_kubernetes_configs
    create_deployment_scripts
    create_monitoring_configs
    
    log "Deployment automation setup completed successfully!"
    log ""
    log "Created deployment configurations:"
    log "- Docker Compose for research and compliance environments"
    log "- Kubernetes manifests for scalable deployment"
    log "- Automated deployment scripts with health checks"
    log "- Comprehensive monitoring and alerting setup"
    log ""
    log "Next steps:"
    log "1. Review and customize the deployment configurations"
    log "2. Set up environment variables and SSL certificates"
    log "3. Run ./05-setup-sync.sh to configure synchronization"
    log "4. Test deployments with the deployment scripts"
    log ""
    log "Research deployment: ./scripts/deploy-research.sh"
    log "Compliance deployment: ./scripts/deploy-compliance.sh production"
}

main "$@"