# 📦 Wall-E Installation Guide

Complete installation and setup guide for the Wall-E Wallapop automation system with AI Engine integration.

---

## 📋 Table of Contents

- [🎯 Prerequisites](#-prerequisites)
- [⚡ Quick Installation](#-quick-installation)
- [🔧 Manual Installation](#-manual-installation)
- [🤖 AI Engine Setup](#-ai-engine-setup)
- [🐳 Docker Installation](#-docker-installation)
- [✅ Verification & Testing](#-verification--testing)
- [🔧 Configuration](#-configuration)
- [🩺 Troubleshooting](#-troubleshooting)

---

## 🎯 Prerequisites

### Hardware Requirements

**Minimum Requirements:**
- **RAM:** 8GB (for lightweight AI models)
- **CPU:** 4 cores, 2.4GHz+
- **Storage:** 20GB free space (SSD recommended)
- **Network:** Stable internet connection for downloads

**Recommended Configuration:**
- **RAM:** 16GB+ (optimal for Llama 3.2 11B model)
- **CPU:** 8+ cores, 3.0GHz+
- **Storage:** 50GB+ NVMe SSD
- **Network:** High-speed internet for model downloads

**Enterprise Configuration:**
- **RAM:** 32GB+ (for premium AI models)
- **CPU:** 16+ cores, high-frequency
- **Storage:** 100GB+ enterprise SSD
- **GPU:** Optional but recommended for faster inference

### Software Requirements

**Operating System:**
- **Linux:** Ubuntu 20.04+, Debian 11+, CentOS 8+ (Recommended)
- **macOS:** 12.0+ (Monterey)
- **Windows:** 10/11 with WSL2 (Limited support)

**Core Dependencies:**
- **Python:** 3.11+ (3.12 recommended)
- **Git:** Latest version
- **curl/wget:** For downloading components
- **Docker:** 20.10+ (optional, for containerized deployment)

### System Preparation

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget build-essential

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python@3.11 git curl wget

# Install Docker (optional)
brew install --cask docker
```

**Windows (WSL2):**
```powershell
# Install WSL2 and Ubuntu
wsl --install -d Ubuntu-20.04

# Inside WSL2, follow Ubuntu instructions above
```

---

## ⚡ Quick Installation

### One-Command Setup (Recommended)

For fastest setup, use the automated installation script:

```bash
# Clone repository
git clone <repository-url>
cd wall-e-research

# Run automated setup (includes AI Engine)
python scripts/quick_setup.py --full
```

**What this does:**
1. ✅ Creates Python virtual environment
2. ✅ Installs all Python dependencies
3. ✅ Downloads and installs Ollama
4. ✅ Pulls AI model (Llama 3.2 11B)
5. ✅ Installs spaCy Spanish language model
6. ✅ Sets up Playwright browsers
7. ✅ Initializes database schema
8. ✅ Creates default configuration files
9. ✅ Runs validation tests

**Expected output:**
```
🚀 Wall-E Quick Setup
✅ Virtual environment created
✅ Dependencies installed
✅ Ollama installed and started
✅ AI model downloaded (llama3.2:11b-vision-instruct-q4_0)
✅ spaCy Spanish model installed
✅ Playwright browsers installed
✅ Database initialized
✅ Configuration files created
✅ System validation passed

🎉 Installation complete! Run: python examples/ai_engine_example.py
```

### Quick Verification

```bash
# Test AI Engine
python scripts/test_ai_engine_basic.py

# Run interactive demo
python examples/ai_engine_example.py --interactive
```

---

## 🔧 Manual Installation

### Step 1: Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd wall-e-research

# Create virtual environment
python3.11 -m venv wall_e_env
source wall_e_env/bin/activate  # Linux/macOS
# wall_e_env\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 2: Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Verify installation
pip list | grep -E "(fastapi|playwright|spacy|ollama)"
```

### Step 3: Language Models

```bash
# Install spaCy Spanish model
python -m spacy download es_core_news_sm

# Verify spaCy installation
python -c "import spacy; nlp = spacy.load('es_core_news_sm'); print('✅ spaCy Spanish model loaded')"
```

### Step 4: Web Automation

```bash
# Install Playwright browsers
playwright install chromium

# Verify Playwright installation
playwright --version
```

### Step 5: Database Setup

```bash
# Initialize database schema
python scripts/init_database_advanced.py

# Verify database connection
python scripts/validate_config.py --database
```

---

## 🤖 AI Engine Setup

### Ollama Installation

**Automatic Installation (Recommended):**
```bash
python scripts/setup_ollama.py
```

**Manual Installation:**

**Linux/macOS:**
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Windows:**
```powershell
# Download from https://ollama.ai/download/windows
# Run the installer and follow instructions
```

### AI Model Setup

**Recommended Model (16GB+ RAM):**
```bash
# Pull Llama 3.2 11B Vision Instruct (4-bit quantized)
ollama pull llama3.2:11b-vision-instruct-q4_0

# Verify model
ollama list
```

**Lightweight Model (8-16GB RAM):**
```bash
# Pull Phi 3.5 Mini (more efficient)
ollama pull phi3.5:3.8b-mini-instruct-q4_0
```

**Premium Model (32GB+ RAM):**
```bash
# Pull Qwen 2.5 14B (highest quality)
ollama pull qwen2.5:14b-instruct-q4_0
```

### Hardware-Specific Configuration

**For 8GB RAM Systems:**
```bash
python scripts/setup_ollama.py --model phi3.5:3.8b-mini-instruct-q4_0 --memory-profile lightweight
```

**For 16GB RAM Systems:**
```bash
python scripts/setup_ollama.py --model llama3.2:11b-vision-instruct-q4_0 --memory-profile balanced
```

**For 32GB+ RAM Systems:**
```bash
python scripts/setup_ollama.py --model qwen2.5:14b-instruct-q4_0 --memory-profile premium
```

### AI Engine Validation

```bash
# Test AI Engine initialization
python scripts/test_ai_engine_basic.py

# Run performance benchmark
python scripts/run_performance_benchmark.py --quick

# Interactive testing
python examples/ai_engine_example.py --interactive
```

---

## 🐳 Docker Installation

### Prerequisites

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Development Environment

```bash
# Clone repository
git clone <repository-url>
cd wall-e-research

# Build and start development environment
docker-compose -f docker-compose.dev.yml up --build

# Verify services
docker-compose ps
```

### Production Environment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check service health
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs ai_engine
```

### Docker Services

**Core Services:**
- **ai_engine** - Main AI Engine service
- **postgres** - Primary database
- **redis** - Caching and session storage
- **ollama** - LLM inference server
- **nginx** - Load balancer and proxy

**Optional Services:**
- **grafana** - Monitoring dashboard
- **prometheus** - Metrics collection
- **elasticsearch** - Log aggregation

### Docker Configuration

**Environment Variables (.env):**
```bash
# Core Configuration
POSTGRES_DB=wall_e
POSTGRES_USER=wall_e_user
POSTGRES_PASSWORD=secure_password
REDIS_URL=redis://redis:6379/0

# AI Engine Configuration
OLLAMA_HOST=http://ollama:11434
AI_MODEL=llama3.2:11b-vision-instruct-q4_0
AI_MODE=ai_first

# Security Configuration
SECRET_KEY=your_secret_key_here
FRAUD_DETECTION_THRESHOLD=25
```

---

## ✅ Verification & Testing

### System Health Check

```bash
# Complete system validation
python scripts/validate_setup.py --full

# Check specific components
python scripts/validate_setup.py --ai-engine
python scripts/validate_setup.py --database
python scripts/validate_setup.py --dependencies
```

### AI Engine Testing

```bash
# Basic functionality test
python scripts/test_ai_engine_basic.py

# Integration testing
python scripts/test_ai_engine_integration.py

# Performance benchmark
python scripts/run_performance_benchmark.py --full
```

### Interactive Demo

```bash
# Start interactive demo
python examples/ai_engine_example.py --interactive

# Expected interaction:
# 🤖 Wall-E AI Engine Demo
# Enter buyer message: ¡Hola! ¿Está disponible el iPhone?
# 🤖 Response: ¡Hola! 😊 Sí, está disponible. Son 400€ como aparece en el anuncio. ¿Te interesa?
# 📊 Confidence: 0.92 | Risk Score: 0/100 | Source: ai_engine
```

### Test Suite Execution

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/ai_engine/ -v
pytest tests/integration/ -v
pytest tests/security/ -v
```

### Performance Validation

```bash
# Memory usage test
python scripts/test_memory_management.py

# Concurrent processing test
python scripts/test_concurrent_processing.py --requests 10

# Response time benchmark
python scripts/benchmark_response_times.py
```

---

## 🔧 Configuration

### Basic Configuration

**Create config file:**
```bash
cp config/config.example.yaml config/config.yaml
```

**Edit configuration:**
```yaml
# config/config.yaml
ai_engine:
  mode: ai_first  # ai_first, template_only, hybrid, ai_only
  model_name: llama3.2:11b-vision-instruct-q4_0
  temperature: 0.7
  max_tokens: 150
  timeout: 30

security:
  fraud_detection_threshold: 25
  critical_fraud_threshold: 50
  enable_url_analysis: true
  enable_pattern_matching: true

performance:
  max_concurrent_requests: 10
  connection_pool_size: 5
  cache_size: 1000
  enable_caching: true
```

### Environment-Specific Configurations

**Development (config/dev_config.yaml):**
```yaml
ai_engine:
  mode: hybrid
  debug_mode: true
  log_level: DEBUG
  enable_profiling: true

database:
  echo_sql: true
  pool_pre_ping: true
```

**Production (config/prod_config.yaml):**
```yaml
ai_engine:
  mode: ai_first
  debug_mode: false
  log_level: INFO
  enable_profiling: false

security:
  fraud_detection_threshold: 20  # Stricter in production
  audit_all_responses: true
```

### Hardware-Aware Configuration

```bash
# Auto-detect and configure for your hardware
python scripts/configure_for_hardware.py

# Manual configuration for specific hardware
python scripts/configure_for_hardware.py --ram 16 --cpu 8
```

### Advanced Configuration

**AI Engine Tuning:**
```python
# Custom configuration in code
from src.ai_engine.config import AIEngineConfig

config = AIEngineConfig(
    mode=AIEngineMode.AI_FIRST,
    model_name="llama3.2:11b-vision-instruct-q4_0",
    temperature=0.7,
    max_tokens=150,
    max_concurrent_requests=15,
    connection_pool_size=8,
    memory_threshold_mb=12000,
    cache_size=2000,
    enable_performance_monitoring=True
)
```

**Security Configuration:**
```python
# Enhanced fraud detection
config.fraud_detection_threshold = 20
config.critical_fraud_threshold = 40
config.enable_url_analysis = True
config.enable_context_analysis = True
config.strict_validation = True
```

---

## 🩺 Troubleshooting

### Common Installation Issues

**Issue: Python version conflicts**
```bash
# Solution: Use specific Python version
python3.11 -m venv wall_e_env
source wall_e_env/bin/activate
pip install --upgrade pip
```

**Issue: Ollama installation fails**
```bash
# Solution: Manual installation
curl -fsSL https://ollama.ai/install.sh | sh

# If permission issues on Linux:
sudo curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

**Issue: AI model download fails**
```bash
# Solution: Check internet connection and retry
ollama pull llama3.2:11b-vision-instruct-q4_0

# If model too large for system:
ollama pull phi3.5:3.8b-mini-instruct-q4_0  # Smaller model
```

**Issue: spaCy model download fails**
```bash
# Solution: Direct download
python -m spacy download es_core_news_sm --user

# Alternative method
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0.tar.gz
```

**Issue: Playwright installation fails**
```bash
# Solution: Install with dependencies
playwright install --with-deps chromium

# If permission issues:
sudo playwright install-deps
playwright install chromium
```

### AI Engine Issues

**Issue: Ollama connection failed**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama service
ollama serve

# Test connection
curl http://localhost:11434/api/version
```

**Issue: Model not found**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3.2:11b-vision-instruct-q4_0

# Verify model works
ollama run llama3.2:11b-vision-instruct-q4_0 "Test message"
```

**Issue: Out of memory errors**
```bash
# Solution: Use smaller model
python scripts/setup_ollama.py --model phi3.5:3.8b-mini-instruct-q4_0

# Or adjust configuration
python scripts/configure_for_hardware.py --memory-profile lightweight
```

### Database Issues

**Issue: Database connection fails**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
python scripts/validate_config.py --database
```

**Issue: Permission denied**
```bash
# Fix PostgreSQL permissions
sudo -u postgres createuser wall_e_user
sudo -u postgres createdb wall_e
sudo -u postgres psql -c "ALTER USER wall_e_user CREATEDB;"
```

### Performance Issues

**Issue: Slow response times**
```bash
# Check system resources
htop
free -h
df -h

# Run performance benchmark
python scripts/run_performance_benchmark.py --full

# Check AI Engine metrics
python scripts/monitor_performance.py
```

**Issue: High memory usage**
```bash
# Monitor memory usage
python scripts/test_memory_management.py

# Adjust configuration
# Edit config/config.yaml:
# memory_threshold_mb: 8000  # Lower threshold
# max_concurrent_requests: 5  # Reduce concurrency
```

### Getting Help

**System Diagnostics:**
```bash
# Generate diagnostic report
python scripts/generate_diagnostic_report.py

# Check logs
tail -f logs/ai_engine.log
tail -f logs/installation.log
```

**Validation Scripts:**
```bash
# Complete system check
python scripts/validate_setup.py --full --verbose

# Component-specific checks
python scripts/validate_setup.py --ai-engine --verbose
python scripts/validate_setup.py --dependencies --verbose
```

**Debug Mode:**
```bash
# Run with debug logging
export WALL_E_DEBUG=true
python examples/ai_engine_example.py --debug
```

### Support Resources

- **📚 Full Documentation:** [README.md](../README.md)
- **🤖 AI Engine Guide:** [AI_ENGINE_GUIDE.md](AI_ENGINE_GUIDE.md)
- **🔧 API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
- **🩺 Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **👩‍💻 Development Guide:** [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

---

## 🎉 Installation Complete!

After successful installation, you should have:

✅ **Fully functional AI Engine** with natural Spanish conversations  
✅ **Multi-layer fraud detection** system active  
✅ **Performance monitoring** and optimization  
✅ **Comprehensive testing** suite available  
✅ **Production-ready** configuration  

### Next Steps

1. **🚀 Try the interactive demo:**
   ```bash
   python examples/ai_engine_example.py --interactive
   ```

2. **📊 Monitor performance:**
   ```bash
   python scripts/monitor_performance.py
   ```

3. **🧪 Run test suite:**
   ```bash
   pytest tests/ -v
   ```

4. **📚 Read the documentation:**
   - [AI Engine Guide](AI_ENGINE_GUIDE.md)
   - [API Reference](API_REFERENCE.md)
   - [Development Guide](DEVELOPMENT_GUIDE.md)

5. **🤖 Start building:**
   ```python
   from src.ai_engine import AIEngine, AIEngineConfig
   
   # Your AI-powered Wallapop automation starts here!
   ```

**🚀 Welcome to the future of marketplace automation with Wall-E AI Engine!**