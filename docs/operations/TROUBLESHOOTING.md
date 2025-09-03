# 🩺 Wall-E Troubleshooting Guide

Comprehensive troubleshooting guide for the Wall-E Wallapop automation system with AI Engine integration.

---

## 📋 Table of Contents

- [🚀 Quick Diagnostics](#-quick-diagnostics)
- [🤖 AI Engine Issues](#-ai-engine-issues)
- [🔧 Installation Problems](#-installation-problems)
- [⚡ Performance Issues](#-performance-issues)
- [🛡️ Security & Fraud Detection](#️-security--fraud-detection)
- [💽 Database Issues](#-database-issues)
- [🌐 Network & Connectivity](#-network--connectivity)
- [🐳 Docker & Deployment](#-docker--deployment)
- [📊 Monitoring & Logs](#-monitoring--logs)
- [🆘 Emergency Procedures](#-emergency-procedures)

---

## 🚀 Quick Diagnostics

### System Health Check

**Run comprehensive system validation:**
```bash
# Complete system health check
python scripts/validate_setup.py --full --verbose

# Quick AI Engine check
python scripts/test_ai_engine_basic.py

# Performance validation
python scripts/validate_performance_setup.py

# Network connectivity check
curl -I https://api.your-domain.com/api/v2/health
```

### Common Status Commands

```bash
# Check service status (Docker)
docker-compose ps
docker-compose logs ai_engine --tail=50

# Check service status (Kubernetes)
kubectl get pods -n wall-e-production
kubectl logs deployment/ai-engine -n wall-e-production --tail=50

# Check system resources
htop
free -h
df -h
iostat -x 1 5

# Check AI Engine metrics
curl -s http://localhost:8000/api/v2/metrics | jq
```

### Emergency Health Check Script

**Create `scripts/emergency_health_check.py`:**
```python
#!/usr/bin/env python3
"""Emergency health check for Wall-E system"""

import requests
import psutil
import subprocess
import json
from datetime import datetime

def check_system_resources():
    """Check system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_usage": cpu_percent,
        "memory_usage": memory.percent,
        "memory_available_gb": memory.available / (1024**3),
        "disk_usage": disk.percent,
        "disk_free_gb": disk.free / (1024**3)
    }

def check_ai_engine():
    """Check AI Engine health"""
    try:
        response = requests.get("http://localhost:8000/api/v2/health", timeout=10)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time": response.elapsed.total_seconds(),
            "data": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def check_ollama():
    """Check Ollama service"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "version": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def check_database():
    """Check database connectivity"""
    try:
        import psycopg2
        # Use connection string from environment
        conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy"}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    print("🩺 Wall-E Emergency Health Check")
    print("=" * 50)
    
    # System resources
    print("\n📊 System Resources:")
    resources = check_system_resources()
    for key, value in resources.items():
        status = "⚠️" if "usage" in key and value > 80 else "✅"
        print(f"  {status} {key}: {value}")
    
    # AI Engine
    print("\n🤖 AI Engine:")
    ai_status = check_ai_engine()
    status_icon = "✅" if ai_status["status"] == "healthy" else "❌"
    print(f"  {status_icon} Status: {ai_status['status']}")
    if "response_time" in ai_status:
        print(f"  ⏱️ Response Time: {ai_status['response_time']:.3f}s")
    
    # Ollama
    print("\n🧠 Ollama:")
    ollama_status = check_ollama()
    status_icon = "✅" if ollama_status["status"] == "healthy" else "❌"
    print(f"  {status_icon} Status: {ollama_status['status']}")
    
    # Database
    print("\n💾 Database:")
    db_status = check_database()
    status_icon = "✅" if db_status["status"] == "healthy" else "❌"
    print(f"  {status_icon} Status: {db_status['status']}")
    
    # Overall assessment
    all_healthy = all([
        ai_status["status"] == "healthy",
        ollama_status["status"] == "healthy",
        db_status["status"] == "healthy",
        resources["cpu_usage"] < 90,
        resources["memory_usage"] < 90
    ])
    
    print(f"\n🎯 Overall Status: {'✅ HEALTHY' if all_healthy else '⚠️ NEEDS ATTENTION'}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_resources": resources,
        "ai_engine": ai_status,
        "ollama": ollama_status,
        "database": db_status,
        "overall_healthy": all_healthy
    }
    
    with open("health_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: health_report.json")

if __name__ == "__main__":
    main()
```

---

## 🤖 AI Engine Issues

### Model Not Found Errors

**Issue:** `ModelNotAvailableError: Model 'llama3.2:11b-vision-instruct-q4_0' not found`

**Diagnosis:**
```bash
# Check available models
ollama list

# Check if Ollama is running
ps aux | grep ollama
curl http://localhost:11434/api/version
```

**Solutions:**

1. **Pull the required model:**
```bash
ollama pull llama3.2:11b-vision-instruct-q4_0

# If download fails, try smaller model
ollama pull phi3.5:3.8b-mini-instruct-q4_0
```

2. **Check disk space:**
```bash
df -h
# Models require 4-20GB each
```

3. **Restart Ollama service:**
```bash
# Kill existing process
pkill ollama

# Start Ollama
ollama serve
```

4. **Use alternative model:**
```python
# Update configuration
config = AIEngineConfig(
    model_name="phi3.5:3.8b-mini-instruct-q4_0"  # Smaller model
)
```

### Ollama Connection Issues

**Issue:** `OllamaConnectionError: Failed to connect to Ollama server`

**Diagnosis:**
```bash
# Check if Ollama is running
sudo netstat -tlnp | grep 11434
curl http://localhost:11434/api/version

# Check logs
journalctl -u ollama -f
```

**Solutions:**

1. **Start Ollama service:**
```bash
# Manual start
ollama serve

# Background start
nohup ollama serve > ollama.log 2>&1 &

# Systemd service
sudo systemctl start ollama
sudo systemctl enable ollama
```

2. **Check firewall:**
```bash
sudo ufw status
sudo ufw allow 11434
```

3. **Fix permission issues:**
```bash
# Check Ollama installation
which ollama
ls -la /usr/local/bin/ollama

# Reinstall if needed
curl -fsSL https://ollama.ai/install.sh | sh
```

4. **Configuration fix:**
```python
# Use correct host in configuration
config = AIEngineConfig(
    ollama_host="http://localhost:11434",  # Ensure correct URL
    ollama_timeout=30,
    ollama_retry_attempts=3
)
```

### Generation Timeout Issues

**Issue:** `GenerationTimeoutError: AI generation timeout after 30 seconds`

**Diagnosis:**
```bash
# Check system load
top
iostat -x 1 5

# Check memory usage
free -h

# Test manual generation
ollama run llama3.2:11b-vision-instruct-q4_0 "Test message"
```

**Solutions:**

1. **Increase timeout:**
```python
config = AIEngineConfig(
    timeout=60,  # Increase timeout
    ollama_timeout=50
)
```

2. **Use faster model:**
```python
config = AIEngineConfig(
    model_name="phi3.5:3.8b-mini-instruct-q4_0",  # Faster model
    max_tokens=150  # Shorter responses
)
```

3. **Optimize system resources:**
```bash
# Close unnecessary processes
sudo systemctl stop unnecessary-service

# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

4. **Enable template fallback:**
```python
config = AIEngineConfig(
    mode=AIEngineMode.AI_FIRST,  # Use fallback
    enable_fallback=True
)
```

### Memory Issues

**Issue:** `MemoryExhaustedError: Memory usage exceeded threshold`

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check AI Engine memory
python -c "
from src.ai_engine.performance_monitor import get_performance_monitor
monitor = get_performance_monitor()
print(monitor.get_memory_status())
"
```

**Solutions:**

1. **Increase memory threshold:**
```python
config = AIEngineConfig(
    memory_threshold_mb=16000,  # Increase threshold
    gc_threshold=25  # More frequent garbage collection
)
```

2. **Use memory-efficient model:**
```python
config = AIEngineConfig(
    model_name="phi3.5:3.8b-mini-instruct-q4_0",  # Uses less memory
    max_concurrent_requests=3  # Reduce concurrency
)
```

3. **Clear cache:**
```python
from src.ai_engine.performance_monitor import get_performance_monitor
monitor = get_performance_monitor()
monitor.clear_cache()
```

4. **Manual memory cleanup:**
```python
import gc
gc.collect()

# Force cleanup in AI Engine
engine.trigger_cleanup()
```

### Poor Response Quality

**Issue:** Low confidence scores or inappropriate responses

**Diagnosis:**
```python
# Test with debug mode
config = AIEngineConfig(
    debug_mode=True,
    save_prompts=True,
    save_responses=True
)

response = engine.generate_response(request)
print(f"Confidence: {response.confidence}")
print(f"Source: {response.source}")
print(f"Metadata: {response.metadata}")
```

**Solutions:**

1. **Adjust temperature:**
```python
config = AIEngineConfig(
    temperature=0.8,  # More creative
    # OR
    temperature=0.5   # More focused
)
```

2. **Optimize prompts:**
```python
# Use specific personality
request = ConversationRequest(
    buyer_message="...",
    personality="profesional_cordial",  # More appropriate
    force_personality=True
)
```

3. **Check model compatibility:**
```python
# Test different models
models_to_test = [
    "llama3.2:11b-vision-instruct-q4_0",
    "qwen2.5:14b-instruct-q4_0",
    "phi3.5:3.8b-mini-instruct-q4_0"
]

for model in models_to_test:
    config.model_name = model
    response = engine.generate_response(request)
    print(f"{model}: {response.confidence:.2f}")
```

---

## 🔧 Installation Problems

### Python Version Issues

**Issue:** `Python version 3.11+ required`

**Solutions:**

1. **Install Python 3.11:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# CentOS/RHEL
sudo dnf install python3.11
```

2. **Use pyenv for version management:**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.7
pyenv global 3.11.7
```

3. **Virtual environment with specific Python:**
```bash
python3.11 -m venv wall_e_env
source wall_e_env/bin/activate
```

### Dependency Installation Failures

**Issue:** `pip install` failures or missing packages

**Diagnosis:**
```bash
# Check pip version
pip --version

# Check for conflicts
pip check

# Verbose installation
pip install -r requirements.txt -v
```

**Solutions:**

1. **Upgrade pip and tools:**
```bash
pip install --upgrade pip setuptools wheel
```

2. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev libpq-dev

# CentOS/RHEL
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel postgresql-devel
```

3. **Clean installation:**
```bash
pip cache purge
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

4. **Use conda environment:**
```bash
conda create -n wall_e python=3.11
conda activate wall_e
pip install -r requirements.txt
```

### spaCy Model Issues

**Issue:** `OSError: Can't find model 'es_core_news_sm'`

**Solutions:**

1. **Install spaCy model:**
```bash
python -m spacy download es_core_news_sm

# If download fails, use direct URL
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0.tar.gz
```

2. **Verify installation:**
```python
import spacy
nlp = spacy.load("es_core_news_sm")
print("✅ spaCy Spanish model loaded successfully")
```

3. **Alternative model:**
```bash
# Use larger model if available
python -m spacy download es_core_news_md
```

### Playwright Installation Issues

**Issue:** Browser installation failures

**Solutions:**

1. **Install with dependencies:**
```bash
playwright install --with-deps chromium
```

2. **Manual dependency installation:**
```bash
# Ubuntu/Debian
sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Install browsers
playwright install chromium
```

3. **Use system browser:**
```python
# Configure to use system Chrome
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/google-chrome-stable"
    )
```

### Docker Installation Issues

**Issue:** Docker or Docker Compose not working

**Solutions:**

1. **Install Docker:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Fix permissions:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
newgrp docker
```

---

## ⚡ Performance Issues

### Slow Response Times

**Issue:** Response times > 5 seconds

**Diagnosis:**
```bash
# Run performance benchmark
python scripts/run_performance_benchmark.py --quick

# Check system resources
htop
iotop -a

# Profile specific request
python scripts/profile_request.py
```

**Solutions:**

1. **Optimize configuration:**
```python
config = AIEngineConfig(
    model_name="phi3.5:3.8b-mini-instruct-q4_0",  # Faster model
    max_tokens=150,                               # Shorter responses
    temperature=0.6,                              # Less creative
    timeout=20,                                   # Shorter timeout
    connection_pool_size=8                        # More connections
)
```

2. **Enable aggressive caching:**
```python
config = AIEngineConfig(
    enable_caching=True,
    cache_size=2000,
    cache_ttl=7200
)
```

3. **Reduce concurrent load:**
```python
config = AIEngineConfig(
    max_concurrent_requests=5  # Lower if system struggles
)
```

4. **System optimization:**
```bash
# Increase file descriptor limits
echo "fs.file-max = 65536" | sudo tee -a /etc/sysctl.conf
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize TCP settings
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### High Memory Usage

**Issue:** Memory usage > 80%

**Diagnosis:**
```bash
# Monitor memory usage over time
python scripts/monitor_memory.py

# Check for memory leaks
valgrind --tool=memcheck --leak-check=full python scripts/test_memory.py
```

**Solutions:**

1. **Adjust memory limits:**
```python
config = AIEngineConfig(
    memory_threshold_mb=6000,  # Lower threshold
    gc_threshold=25,           # More frequent GC
    enable_memory_monitoring=True
)
```

2. **Use memory-efficient model:**
```python
config = AIEngineConfig(
    model_name="phi3.5:3.8b-mini-instruct-q4_0"  # Uses ~4GB vs 12GB
)
```

3. **Optimize caching:**
```python
config = AIEngineConfig(
    cache_size=500,  # Smaller cache
    enable_cache_compression=True
)
```

4. **System-level fixes:**
```bash
# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### CPU Bottlenecks

**Issue:** High CPU usage causing slowdowns

**Diagnosis:**
```bash
# Check CPU usage by process
top -o %CPU
ps aux --sort=-%cpu | head -10

# Check CPU frequency scaling
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

**Solutions:**

1. **Optimize concurrency:**
```python
config = AIEngineConfig(
    max_concurrent_requests=min(cpu_count(), 8),
    thread_pool_size=cpu_count() * 2
)
```

2. **CPU governor optimization:**
```bash
# Set performance governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Or use cpufrequtils
sudo apt install cpufrequtils
sudo cpufreq-set -g performance
```

3. **Process priority:**
```bash
# Increase AI Engine priority
sudo renice -10 $(pgrep -f "ai_engine")

# Or start with high priority
sudo nice -n -10 python src/api/main.py
```

---

## 🛡️ Security & Fraud Detection

### False Positives in Fraud Detection

**Issue:** Legitimate messages being blocked as fraud

**Diagnosis:**
```python
# Test specific message
from src.ai_engine.validator import AIResponseValidator

validator = AIResponseValidator(config)
result = validator.validate_buyer_message("Your problematic message")

print(f"Risk Score: {result.risk_score}")
print(f"Risk Factors: {result.risk_factors}")
print(f"Critical Violations: {result.critical_violations}")
```

**Solutions:**

1. **Adjust thresholds:**
```python
config = AIEngineConfig(
    fraud_detection_threshold=35,  # Higher threshold (less strict)
    critical_fraud_threshold=60
)
```

2. **Add whitelist patterns:**
```python
config = AIEngineConfig(
    whitelist_patterns=[
        "legitimate business phrase",
        "commonly used term",
        "industry-specific terminology"
    ]
)
```

3. **Disable specific checks:**
```python
config = AIEngineConfig(
    enable_url_analysis=False,     # If URLs causing issues
    enable_context_analysis=False  # If context checks too strict
)
```

### False Negatives in Fraud Detection

**Issue:** Known fraud patterns not being detected

**Diagnosis:**
```bash
# Test fraud detection patterns
pytest tests/ai_engine/test_validator.py::test_fraud_patterns -v

# Check pattern updates
python -c "
from src.ai_engine.validator import AIResponseValidator
validator = AIResponseValidator()
print(f'Loaded patterns: {len(validator.fraud_patterns)}')
"
```

**Solutions:**

1. **Add custom patterns:**
```python
config = AIEngineConfig(
    custom_fraud_patterns=[
        "new scam pattern",
        "recently discovered fraud method",
        r"regex.*pattern"
    ]
)
```

2. **Lower thresholds:**
```python
config = AIEngineConfig(
    fraud_detection_threshold=15,  # More strict
    critical_fraud_threshold=35
)
```

3. **Enable all validation:**
```python
config = AIEngineConfig(
    enable_url_analysis=True,
    enable_pattern_matching=True,
    enable_context_analysis=True,
    strict_validation=True
)
```

### SSL/TLS Certificate Issues

**Issue:** Certificate validation errors

**Solutions:**

1. **Renew Let's Encrypt certificates:**
```bash
sudo certbot renew --dry-run
sudo certbot renew
sudo systemctl reload nginx
```

2. **Check certificate validity:**
```bash
openssl x509 -in /etc/ssl/certs/your-domain.com.crt -text -noout
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

3. **Fix certificate chain:**
```bash
# Combine certificate and chain
cat /etc/letsencrypt/live/your-domain.com/fullchain.pem > /etc/ssl/certs/your-domain.com.crt
```

---

## 💽 Database Issues

### Connection Failures

**Issue:** `psycopg2.OperationalError: could not connect to server`

**Diagnosis:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
ps aux | grep postgres

# Test connection
psql $POSTGRES_URL -c "SELECT 1;"

# Check port availability
sudo netstat -tlnp | grep 5432
```

**Solutions:**

1. **Start PostgreSQL:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. **Fix connection string:**
```bash
# Verify environment variables
echo $POSTGRES_URL

# Update if needed
export POSTGRES_URL="postgresql://wall_e:password@localhost:5432/wall_e"
```

3. **Check firewall:**
```bash
sudo ufw allow 5432
```

4. **Reset password:**
```bash
sudo -u postgres psql
\password wall_e
```

### Database Migration Issues

**Issue:** Alembic migration failures

**Diagnosis:**
```bash
# Check current revision
alembic current

# Check migration history
alembic history

# Show SQL that would be executed
alembic upgrade head --sql
```

**Solutions:**

1. **Manual migration:**
```bash
# Mark current state
alembic stamp head

# Run specific migration
alembic upgrade +1
```

2. **Reset migrations:**
```bash
# Drop and recreate
alembic downgrade base
alembic upgrade head
```

3. **Fix migration conflicts:**
```bash
# Merge branches
alembic merge heads

# Generate new migration
alembic revision --autogenerate -m "fix conflicts"
```

### Performance Issues

**Issue:** Slow database queries

**Diagnosis:**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
WHERE mean_time > 1000 
ORDER BY mean_time DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Solutions:**

1. **Add indexes:**
```sql
-- Common indexes for Wall-E
CREATE INDEX idx_conversations_buyer_id ON conversations(buyer_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_ai_responses_timestamp ON ai_responses(timestamp);
CREATE INDEX idx_security_logs_risk_score ON security_logs(risk_score);
```

2. **Optimize configuration:**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Recommended settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

3. **Regular maintenance:**
```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE wall_e;
```

---

## 🌐 Network & Connectivity

### DNS Resolution Issues

**Issue:** Cannot resolve domain names

**Diagnosis:**
```bash
# Test DNS resolution
nslookup api.your-domain.com
dig api.your-domain.com

# Check DNS configuration
cat /etc/resolv.conf
```

**Solutions:**

1. **Fix DNS configuration:**
```bash
# Set reliable DNS servers
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
```

2. **Flush DNS cache:**
```bash
sudo systemctl restart systemd-resolved
sudo systemctl flush-dns
```

### Load Balancer Issues

**Issue:** Load balancer not distributing traffic

**Diagnosis:**
```bash
# Check backend health
curl -I http://backend1:8000/api/v2/health
curl -I http://backend2:8000/api/v2/health

# Check Nginx configuration
sudo nginx -t
sudo systemctl status nginx
```

**Solutions:**

1. **Fix Nginx configuration:**
```nginx
upstream ai_engine {
    server ai_engine_1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server ai_engine_2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server ai_engine_3:8000 weight=1 max_fails=3 fail_timeout=30s;
    
    # Health check
    keepalive 32;
}
```

2. **Restart load balancer:**
```bash
sudo systemctl reload nginx
```

### Rate Limiting Issues

**Issue:** Requests being rate limited

**Diagnosis:**
```bash
# Check rate limit logs
grep "rate limit" /var/log/nginx/error.log

# Test rate limits
for i in {1..20}; do curl -I https://api.your-domain.com/api/v2/health; done
```

**Solutions:**

1. **Adjust rate limits:**
```nginx
# In nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req zone=api burst=50 nodelay;
```

2. **Whitelist trusted IPs:**
```nginx
geo $limit {
    default 1;
    10.0.0.0/8 0;      # Internal network
    192.168.0.0/16 0;  # Private network
    your.trusted.ip 0;  # Trusted IP
}

map $limit $limit_key {
    0 "";
    1 $binary_remote_addr;
}

limit_req_zone $limit_key zone=api:10m rate=10r/s;
```

---

## 🐳 Docker & Deployment

### Container Issues

**Issue:** Containers failing to start

**Diagnosis:**
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs ai_engine
docker-compose logs ollama

# Check resource usage
docker stats

# Inspect container
docker inspect wall_e_ai_engine
```

**Solutions:**

1. **Fix resource limits:**
```yaml
# In docker-compose.yml
services:
  ai_engine:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
```

2. **Fix environment variables:**
```bash
# Check .env file
cat .env.prod

# Update missing variables
echo "MISSING_VAR=value" >> .env.prod
```

3. **Rebuild containers:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Volume Issues

**Issue:** Data not persisting between container restarts

**Diagnosis:**
```bash
# Check volumes
docker volume ls
docker volume inspect wall_e_postgres_data

# Check mount points
docker inspect wall_e_postgres | grep -A 10 Mounts
```

**Solutions:**

1. **Fix volume definitions:**
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres
```

2. **Set proper permissions:**
```bash
sudo chown -R 999:999 /data/postgres  # PostgreSQL user
sudo chmod 700 /data/postgres
```

### Kubernetes Issues

**Issue:** Pods failing in Kubernetes

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n wall-e-production

# Check events
kubectl get events -n wall-e-production --sort-by=.metadata.creationTimestamp

# Describe problematic pod
kubectl describe pod ai-engine-xxx -n wall-e-production

# Check logs
kubectl logs ai-engine-xxx -n wall-e-production
```

**Solutions:**

1. **Fix resource requests:**
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

2. **Fix ConfigMaps and Secrets:**
```bash
# Check if secrets exist
kubectl get secrets -n wall-e-production

# Recreate secret if needed
kubectl delete secret wall-e-secrets -n wall-e-production
kubectl create secret generic wall-e-secrets \
  --from-literal=postgres-password=newpassword \
  -n wall-e-production
```

3. **Check node resources:**
```bash
kubectl describe nodes
kubectl top nodes
```

---

## 📊 Monitoring & Logs

### Log Analysis

**Issue:** Finding specific errors in logs

**Tools and Commands:**
```bash
# Search for errors in AI Engine logs
grep -i "error\|exception\|failed" logs/ai_engine.log | tail -20

# Search for performance issues
grep -i "timeout\|slow\|memory" logs/ai_engine.log

# Search for security issues
grep -i "fraud\|security\|violation" logs/security.log

# Use structured log analysis
jq '.level == "ERROR"' logs/ai_engine.jsonl

# Real-time monitoring
tail -f logs/ai_engine.log | grep -i error
```

**Analyze specific issues:**
```python
#!/usr/bin/env python3
"""Log analysis script"""

import json
import sys
from collections import Counter
from datetime import datetime, timedelta

def analyze_logs(logfile):
    errors = []
    performance_issues = []
    
    with open(logfile, 'r') as f:
        for line in f:
            try:
                log = json.loads(line)
                
                if log.get('level') == 'ERROR':
                    errors.append(log)
                
                if log.get('response_time', 0) > 5:
                    performance_issues.append(log)
                    
            except json.JSONDecodeError:
                continue
    
    # Count error types
    error_types = Counter(log.get('error_type', 'unknown') for log in errors)
    
    print("🔍 Log Analysis Results")
    print("=" * 30)
    print(f"📊 Total errors: {len(errors)}")
    print(f"⚡ Performance issues: {len(performance_issues)}")
    
    print("\n🚨 Error Types:")
    for error_type, count in error_types.most_common(10):
        print(f"  {error_type}: {count}")
    
    if performance_issues:
        avg_time = sum(log.get('response_time', 0) for log in performance_issues) / len(performance_issues)
        print(f"\n⏱️ Average slow response time: {avg_time:.2f}s")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_logs(sys.argv[1])
    else:
        analyze_logs("logs/ai_engine.log")
```

### Metrics Collection Issues

**Issue:** Prometheus not collecting metrics

**Diagnosis:**
```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# Check Prometheus configuration
cat monitoring/prometheus.yml

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

**Solutions:**

1. **Fix metrics endpoint:**
```python
# Ensure metrics are enabled in AI Engine
config = AIEngineConfig(
    enable_metrics=True,
    metrics_port=8000
)
```

2. **Fix Prometheus configuration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ai-engine'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

3. **Check firewall:**
```bash
sudo ufw allow from 172.17.0.0/16 to any port 8000
```

### Dashboard Issues

**Issue:** Grafana dashboards not showing data

**Solutions:**

1. **Check data source:**
```bash
# Test Prometheus connection
curl http://prometheus:9090/api/v1/query?query=up
```

2. **Fix queries:**
```promql
# Example corrected queries
rate(wall_e_requests_total[5m])
histogram_quantile(0.95, wall_e_response_time_seconds_bucket)
```

3. **Import dashboard:**
```bash
# Re-import dashboard
curl -X POST http://admin:password@grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/wall-e-dashboard.json
```

---

## 🆘 Emergency Procedures

### System Recovery

**Complete System Failure:**

1. **Emergency shutdown:**
```bash
# Stop all services gracefully
docker-compose down
# OR
kubectl delete deployment --all -n wall-e-production
```

2. **Check system resources:**
```bash
# Check disk space
df -h

# Check memory
free -h

# Check processes
ps aux | head -20
```

3. **Restart core services:**
```bash
# Start database first
docker-compose up -d postgres redis

# Wait for database
sleep 30

# Start AI Engine
docker-compose up -d ollama
sleep 60  # Wait for model loading
docker-compose up -d ai_engine
```

### Data Recovery

**Database Recovery:**

1. **From backup:**
```bash
# Stop services
docker-compose stop ai_engine

# Restore from backup
gunzip -c backup_20250116.sql.gz | psql $POSTGRES_URL

# Restart services
docker-compose start ai_engine
```

2. **Point-in-time recovery:**
```bash
# Use WAL files if available
pg_basebackup -h localhost -D backup_location -U wall_e -P -W
```

### Security Incident Response

**Security Breach Detected:**

1. **Immediate isolation:**
```bash
# Block all external traffic
sudo ufw deny in
sudo ufw deny out

# Stop AI Engine
docker-compose stop ai_engine
```

2. **Assess damage:**
```bash
# Check security logs
grep -i "fraud\|attack\|violation" logs/security.log | tail -100

# Check access logs
grep -E "(POST|PUT|DELETE)" logs/access.log | tail -50
```

3. **Recovery steps:**
```bash
# Update security patterns
python scripts/update_security_patterns.py

# Restart with enhanced security
export FRAUD_DETECTION_THRESHOLD=10
docker-compose up -d ai_engine
```

### Performance Emergency

**System Overload:**

1. **Immediate relief:**
```bash
# Reduce concurrent requests
export MAX_CONCURRENT_REQUESTS=3
docker-compose restart ai_engine

# Enable aggressive caching
export ENABLE_CACHING=true
export CACHE_SIZE=5000
```

2. **Scale horizontally:**
```bash
# Kubernetes scaling
kubectl scale deployment ai-engine --replicas=10 -n wall-e-production

# Docker Compose scaling
docker-compose up -d --scale ai_engine=3
```

### Emergency Contacts

**Create `emergency_procedures.md`:**
```markdown
# Emergency Contacts and Procedures

## Contacts
- **System Administrator:** admin@company.com (+1234567890)
- **Security Team:** security@company.com (+1234567891)
- **DevOps Engineer:** devops@company.com (+1234567892)

## Emergency Commands
```bash
# Complete system shutdown
sudo shutdown -h now

# Emergency restart
sudo reboot

# Kill all Wall-E processes
pkill -f wall_e
```

## Backup Locations
- Database backups: s3://wall-e-backups/database/
- Configuration backups: s3://wall-e-backups/config/
- Log archives: s3://wall-e-backups/logs/

## Recovery Time Objectives
- Database recovery: 30 minutes
- Full system recovery: 60 minutes
- Emergency patch deployment: 15 minutes
```

### Health Check Automation

**Create automated recovery script:**
```python
#!/usr/bin/env python3
"""Automated recovery script for Wall-E"""

import subprocess
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_service_health(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def restart_service(service_name):
    try:
        subprocess.run(["docker-compose", "restart", service_name], check=True)
        logger.info(f"Restarted service: {service_name}")
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to restart service: {service_name}")
        return False

def emergency_recovery():
    services = [
        ("AI Engine", "http://localhost:8000/api/v2/health", "ai_engine"),
        ("Ollama", "http://localhost:11434/api/version", "ollama"),
    ]
    
    for name, url, service in services:
        if not check_service_health(url):
            logger.warning(f"{name} is unhealthy, attempting restart...")
            
            if restart_service(service):
                # Wait for service to come up
                time.sleep(30)
                
                if check_service_health(url):
                    logger.info(f"{name} recovered successfully")
                else:
                    logger.error(f"{name} failed to recover")
                    # Send alert
                    send_emergency_alert(f"{name} failed to recover")
            else:
                logger.error(f"Failed to restart {name}")

def send_emergency_alert(message):
    # Implement your alerting mechanism here
    logger.critical(f"EMERGENCY ALERT: {message}")

if __name__ == "__main__":
    emergency_recovery()
```

---

**🩺 This comprehensive troubleshooting guide covers the most common issues and their solutions. For additional help or complex issues, consult the [AI Engine Guide](AI_ENGINE_GUIDE.md), [Deployment Guide](DEPLOYMENT_GUIDE.md), or [API Reference](API_REFERENCE.md).**

*Remember: The Wall-E system is designed with fault tolerance and graceful degradation. Most issues can be resolved with simple configuration adjustments or service restarts.*