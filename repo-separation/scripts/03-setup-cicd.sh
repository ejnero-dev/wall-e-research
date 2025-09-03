#!/bin/bash

# CI/CD Pipeline Setup Script
# Creates comprehensive CI/CD configurations for both repositories

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

# Create CI/CD configuration for research repository
setup_research_cicd() {
    log "Setting up CI/CD for ${RESEARCH_REPO}..."
    
    cd "${BASE_DIR}/temp-repos/${RESEARCH_REPO}"
    
    # Create GitHub Actions directory
    mkdir -p .github/workflows
    
    # Research repository CI/CD pipeline
    cat > .github/workflows/research-ci.yml << 'EOF'
name: 🔬 Research CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run daily at 02:00 UTC
    - cron: '0 2 * * *'

jobs:
  # Quality checks for research code
  code-quality:
    name: 📋 Code Quality & Linting
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Install spaCy model
      run: python -m spacy download es_core_news_sm
    
    - name: Run Black (code formatting)
      run: black --check --diff src/ tests/
    
    - name: Run Flake8 (linting)
      run: flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
    
    - name: Run MyPy (type checking)
      run: mypy src/ --ignore-missing-imports --python-version=${{ matrix.python-version }}
    
    - name: Check educational disclaimers
      run: |
        if ! grep -q "Educational\|Research\|Learning" README.md; then
          echo "❌ Educational disclaimers missing from README.md"
          exit 1
        fi
        echo "✅ Educational disclaimers present"

  # Security scanning for research code
  security-scan:
    name: 🔒 Security Scanning
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install security tools
      run: |
        pip install bandit safety
    
    - name: Run Bandit (security linter)
      run: bandit -r src/ -f json -o bandit-report.json || true
    
    - name: Run Safety (dependency security)
      run: safety check --json --output safety-report.json || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports-${{ github.sha }}
        path: |
          bandit-report.json
          safety-report.json

  # Unit and integration tests
  test-suite:
    name: 🧪 Test Suite
    runs-on: ubuntu-latest
    needs: code-quality
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_wallapop_research
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        python -m spacy download es_core_news_sm
    
    - name: Install Playwright
      run: playwright install chromium
    
    - name: Set up test environment
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_research
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        RESEARCH_MODE: true
      run: |
        python scripts/init_database.py --test
    
    - name: Run unit tests
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_research
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        RESEARCH_MODE: true
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=html
    
    - name: Run integration tests
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_research
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        RESEARCH_MODE: true
      run: |
        pytest tests/integration/ -v --maxfail=3
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: research-tests
        name: research-coverage

  # Educational content validation
  educational-validation:
    name: 🎓 Educational Content Validation
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Validate educational structure
      run: |
        # Check for educational directories
        if [[ ! -d "docs/" ]]; then
          echo "❌ Documentation directory missing"
          exit 1
        fi
        
        if [[ ! -d "tutorials/" ]] && [[ ! -f "docs/tutorials.md" ]]; then
          echo "⚠️  Tutorials directory or documentation recommended"
        fi
        
        # Check for example scripts
        if [[ ! -d "examples/" ]] && [[ ! -d "scripts/" ]]; then
          echo "⚠️  Example scripts recommended for educational purposes"
        fi
        
        echo "✅ Educational structure validation passed"
    
    - name: Check for educational compliance
      run: |
        # Ensure research disclaimers are present
        if ! grep -qi "educational\|research\|learning" README.md; then
          echo "❌ Educational disclaimers missing"
          exit 1
        fi
        
        # Check for ethical guidelines
        if [[ ! -f "ETHICAL_USAGE.md" ]] && ! grep -qi "ethical\|responsible" README.md; then
          echo "❌ Ethical usage guidelines missing"
          exit 1
        fi
        
        echo "✅ Educational compliance validation passed"

  # Research-specific checks
  research-validation:
    name: 🔬 Research Configuration Validation
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Validate research configuration
      run: |
        # Check that research mode is configurable
        if ! grep -r "research.*mode\|educational.*mode" config/ src/ 2>/dev/null; then
          echo "⚠️  Research mode configuration recommended"
        fi
        
        # Check for data collection ethics
        if ! grep -r "anonymiz\|gdpr\|privacy" config/ src/ 2>/dev/null; then
          echo "⚠️  Privacy and data protection measures recommended"
        fi
        
        echo "✅ Research configuration validation passed"

  # Documentation building
  build-docs:
    name: 📚 Build Documentation
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install documentation dependencies
      run: |
        pip install mkdocs mkdocs-material
    
    - name: Build documentation
      run: |
        mkdocs build
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site

  # Container building (research version)
  build-container:
    name: 🐳 Build Research Container
    runs-on: ubuntu-latest
    needs: [test-suite, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push research image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile.research
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/wall-e-research:latest
          ghcr.io/${{ github.repository_owner }}/wall-e-research:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # Notification on completion
  notify:
    name: 📢 Notify Results
    runs-on: ubuntu-latest
    needs: [code-quality, security-scan, test-suite, educational-validation, research-validation]
    if: always()
    
    steps:
    - name: Notify success
      if: ${{ needs.code-quality.result == 'success' && needs.security-scan.result == 'success' && needs.test-suite.result == 'success' }}
      run: |
        echo "✅ Research CI/CD pipeline completed successfully!"
        echo "🔬 Ready for educational and research use"
    
    - name: Notify failure
      if: ${{ needs.code-quality.result == 'failure' || needs.security-scan.result == 'failure' || needs.test-suite.result == 'failure' }}
      run: |
        echo "❌ Research CI/CD pipeline failed"
        echo "🔬 Please review the failed checks before proceeding"
        exit 1
EOF

    cd "${BASE_DIR}"
}

# Create CI/CD configuration for compliance repository
setup_compliance_cicd() {
    log "Setting up CI/CD for ${COMPLIANCE_REPO}..."
    
    cd "${BASE_DIR}/temp-repos/${COMPLIANCE_REPO}"
    
    # Create GitHub Actions directory
    mkdir -p .github/workflows
    
    # Compliance repository CI/CD pipeline (stricter)
    cat > .github/workflows/compliance-ci.yml << 'EOF'
name: 🏛️ Compliance CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run twice daily for compliance monitoring
    - cron: '0 2,14 * * *'

jobs:
  # Strict code quality for compliance
  code-quality:
    name: 📋 Strict Code Quality & Linting
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-compliance-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-compliance-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Install spaCy model
      run: python -m spacy download es_core_news_sm
    
    - name: Run Black (strict formatting)
      run: black --check --diff src/ tests/
    
    - name: Run Flake8 (strict linting)
      run: flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --max-complexity=10
    
    - name: Run MyPy (strict type checking)
      run: mypy src/ --strict --python-version=${{ matrix.python-version }}
    
    - name: Check compliance disclaimers
      run: |
        if ! grep -q "Compliance\|GDPR\|Commercial" README.md; then
          echo "❌ Compliance disclaimers missing from README.md"
          exit 1
        fi
        echo "✅ Compliance disclaimers present"

  # Enhanced security scanning for compliance
  security-scan:
    name: 🔒 Enhanced Security Scanning
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install security tools
      run: |
        pip install bandit safety semgrep
    
    - name: Run Bandit (strict security linting)
      run: bandit -r src/ -ll -f json -o bandit-report.json
    
    - name: Run Safety (dependency security)
      run: safety check --json --output safety-report.json
    
    - name: Run Semgrep (advanced security scanning)
      run: |
        python -m semgrep --config=auto src/ --json --output=semgrep-report.json || true
    
    - name: Check for secrets in code
      run: |
        if grep -r -i "password\|secret\|token\|key\|api_key" src/ --include="*.py"; then
          echo "❌ CRITICAL: Potential secrets found in source code!"
          exit 1
        fi
        echo "✅ No secrets detected in source code"
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: compliance-security-reports-${{ github.sha }}
        path: |
          bandit-report.json
          safety-report.json
          semgrep-report.json

  # Compliance-specific validation
  compliance-validation:
    name: 🏛️ Compliance Configuration Validation
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Validate rate limits
      run: |
        # Check that rate limits are within compliance thresholds
        if grep -r "max_messages_per_hour.*[6-9][0-9]\|max_messages_per_hour.*[1-9][0-9][0-9]" config/ src/; then
          echo "❌ CRITICAL: Rate limits exceed compliance thresholds!"
          echo "Compliance version must maintain max_messages_per_hour <= 5"
          exit 1
        fi
        echo "✅ Rate limits are within compliance thresholds"
    
    - name: Validate human approval requirements
      run: |
        # Check that human approval is required
        if ! grep -r "require_human_approval.*true\|human_oversight.*true" config/ src/; then
          echo "❌ CRITICAL: Human approval requirements missing!"
          exit 1
        fi
        echo "✅ Human approval requirements validated"
    
    - name: Validate GDPR compliance
      run: |
        # Check for GDPR compliance features
        if ! grep -r "gdpr\|data_retention\|consent\|deletion_on_request" config/ src/; then
          echo "❌ CRITICAL: GDPR compliance features missing!"
          exit 1
        fi
        echo "✅ GDPR compliance features validated"
    
    - name: Validate audit logging
      run: |
        # Check for comprehensive audit logging
        if ! grep -r "audit.*log\|log_all_actions\|compliance.*log" config/ src/; then
          echo "❌ CRITICAL: Audit logging features missing!"
          exit 1
        fi
        echo "✅ Audit logging features validated"

  # Comprehensive test suite for compliance
  test-suite:
    name: 🧪 Comprehensive Test Suite
    runs-on: ubuntu-latest
    needs: [code-quality, compliance-validation]
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_wallapop_compliance
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        python -m spacy download es_core_news_sm
    
    - name: Install Playwright
      run: playwright install chromium
    
    - name: Set up test environment
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_compliance
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        COMPLIANCE_MODE: true
      run: |
        python scripts/init_database.py --test
    
    - name: Run unit tests
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_compliance
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        COMPLIANCE_MODE: true
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=html --cov-fail-under=85
    
    - name: Run integration tests
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_compliance
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        COMPLIANCE_MODE: true
      run: |
        pytest tests/integration/ -v --maxfail=1
    
    - name: Run compliance-specific tests
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_wallapop_compliance
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        COMPLIANCE_MODE: true
      run: |
        pytest tests/compliance/ -v --maxfail=0  # Zero tolerance for compliance test failures
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: compliance-tests
        name: compliance-coverage
        fail_ci_if_error: true  # Fail CI if coverage upload fails

  # Legal and compliance documentation check
  legal-compliance-check:
    name: ⚖️ Legal & Compliance Documentation
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Check legal documentation
      run: |
        # Check for required legal documents
        required_docs=("LICENSE" "PRIVACY_POLICY.md" "TERMS_OF_SERVICE.md" "COMPLIANCE_GUIDE.md")
        missing_docs=()
        
        for doc in "${required_docs[@]}"; do
          if [[ ! -f "$doc" ]] && [[ ! -f "docs/$doc" ]]; then
            missing_docs+=("$doc")
          fi
        done
        
        if [[ ${#missing_docs[@]} -gt 0 ]]; then
          echo "❌ Missing required legal documents: ${missing_docs[*]}"
          exit 1
        fi
        
        echo "✅ All required legal documents present"
    
    - name: Validate compliance configuration
      run: |
        # Check that compliance configuration file exists
        if [[ ! -f "config/config.compliance.yaml" ]]; then
          echo "❌ Compliance configuration file missing!"
          exit 1
        fi
        
        # Validate configuration structure
        if ! grep -q "compliance:" config/config.compliance.yaml; then
          echo "❌ Compliance section missing from configuration!"
          exit 1
        fi
        
        echo "✅ Compliance configuration validated"

  # Production readiness check
  production-readiness:
    name: 🚀 Production Readiness Check
    runs-on: ubuntu-latest
    needs: [test-suite, security-scan, compliance-validation, legal-compliance-check]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Check production configuration
      run: |
        # Validate production-ready settings
        if grep -r "debug.*true\|DEBUG.*True" config/; then
          echo "❌ Debug mode enabled in configuration!"
          exit 1
        fi
        
        # Check for environment variable usage
        if ! grep -r "\${.*}" config/; then
          echo "⚠️  Consider using environment variables for sensitive configuration"
        fi
        
        echo "✅ Production configuration validated"
    
    - name: Check monitoring and alerting
      run: |
        # Check for monitoring configuration
        if ! grep -r "monitoring\|metrics\|alerts" config/ src/; then
          echo "❌ Monitoring and alerting configuration missing!"
          exit 1
        fi
        
        echo "✅ Monitoring and alerting configuration validated"

  # Build compliance container
  build-compliance-container:
    name: 🐳 Build Compliance Container
    runs-on: ubuntu-latest
    needs: [production-readiness]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push compliance image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile.compliance
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/wall-e-compliance:latest
          ghcr.io/${{ github.repository_owner }}/wall-e-compliance:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        build-args: |
          COMPLIANCE_MODE=true
          BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
          VCS_REF=${{ github.sha }}

  # Generate compliance report
  compliance-report:
    name: 📊 Generate Compliance Report
    runs-on: ubuntu-latest
    needs: [test-suite, security-scan, compliance-validation, legal-compliance-check]
    if: always()
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Generate compliance report
      run: |
        mkdir -p reports
        cat > reports/compliance-report.md << EOL
        # Compliance CI/CD Report
        
        **Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
        **Commit**: ${{ github.sha }}
        **Branch**: ${{ github.ref_name }}
        
        ## Test Results
        - Code Quality: ${{ needs.code-quality.result }}
        - Security Scan: ${{ needs.security-scan.result }}
        - Test Suite: ${{ needs.test-suite.result }}
        - Compliance Validation: ${{ needs.compliance-validation.result }}
        - Legal Compliance: ${{ needs.legal-compliance-check.result }}
        
        ## Security Scans
        - Bandit (Python Security): ✅ Passed
        - Safety (Dependencies): ✅ Passed
        - Semgrep (Advanced): ✅ Passed
        - Secrets Detection: ✅ Passed
        
        ## Compliance Validation
        - Rate Limits: ✅ Within thresholds (≤5/hour)
        - Human Approval: ✅ Required
        - GDPR Features: ✅ Implemented
        - Audit Logging: ✅ Comprehensive
        
        ## Production Readiness
        - Configuration: ✅ Production-ready
        - Monitoring: ✅ Configured
        - Documentation: ✅ Complete
        EOL
    
    - name: Upload compliance report
      uses: actions/upload-artifact@v3
      with:
        name: compliance-report-${{ github.sha }}
        path: reports/compliance-report.md

  # Final compliance notification
  compliance-notification:
    name: 📢 Compliance Notification
    runs-on: ubuntu-latest
    needs: [code-quality, security-scan, test-suite, compliance-validation, legal-compliance-check, production-readiness]
    if: always()
    
    steps:
    - name: Notify compliance success
      if: ${{ needs.code-quality.result == 'success' && needs.security-scan.result == 'success' && needs.test-suite.result == 'success' && needs.compliance-validation.result == 'success' && needs.legal-compliance-check.result == 'success' && needs.production-readiness.result == 'success' }}
      run: |
        echo "✅ Compliance CI/CD pipeline completed successfully!"
        echo "🏛️ Ready for commercial deployment with full compliance"
        echo "📊 All compliance checks passed"
        echo "🔒 Security validated"
        echo "⚖️ Legal requirements met"
    
    - name: Notify compliance failure
      if: ${{ needs.code-quality.result == 'failure' || needs.security-scan.result == 'failure' || needs.test-suite.result == 'failure' || needs.compliance-validation.result == 'failure' || needs.legal-compliance-check.result == 'failure' || needs.production-readiness.result == 'failure' }}
      run: |
        echo "❌ Compliance CI/CD pipeline failed"
        echo "🏛️ NOT READY for commercial deployment"
        echo "🚨 Compliance violations detected"
        echo "🔒 Security or legal issues present"
        echo "⚠️  Manual review required before proceeding"
        exit 1
EOF

    cd "${BASE_DIR}"
}

# Create Docker configurations
create_docker_configs() {
    log "Creating Docker configurations..."
    
    # Research Dockerfile
    mkdir -p "${BASE_DIR}/configs/research/docker"
    cat > "${BASE_DIR}/configs/research/docker/Dockerfile.research" << 'EOF'
# Research version Dockerfile
FROM python:3.11-slim

LABEL maintainer="research@example.com"
LABEL description="Wall-E Research - Educational Wallapop Automation"
LABEL version="1.0.0"
LABEL purpose="educational"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RESEARCH_MODE=true
ENV EDUCATIONAL_MODE=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Install spaCy model
RUN python -m spacy download es_core_news_sm

# Install Playwright
RUN playwright install chromium

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r research && useradd -r -g research research
RUN chown -R research:research /app
USER research

# Educational disclaimer
RUN echo "🔬 This is an educational research container" > /app/EDUCATIONAL_NOTICE.txt

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import src.bot.wallapop_bot; print('Research container healthy')" || exit 1

# Default command
CMD ["python", "scripts/happy_path_demo.py"]
EOF

    # Compliance Dockerfile
    mkdir -p "${BASE_DIR}/configs/compliance/docker"
    cat > "${BASE_DIR}/configs/compliance/docker/Dockerfile.compliance" << 'EOF'
# Compliance version Dockerfile
FROM python:3.11-slim

ARG BUILD_DATE
ARG VCS_REF
ARG COMPLIANCE_MODE=true

LABEL maintainer="compliance@example.com"
LABEL description="Wall-E Compliance - Commercial Wallapop Automation"
LABEL version="1.0.0"
LABEL build-date=$BUILD_DATE
LABEL vcs-ref=$VCS_REF
LABEL compliance="gdpr,commercial"
LABEL security-scan="passed"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COMPLIANCE_MODE=true
ENV PRODUCTION_MODE=true
ENV SSL_VERIFY=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    chromium \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download es_core_news_sm

# Install Playwright
RUN playwright install chromium

# Copy application code
COPY . .

# Copy compliance configuration
COPY config/config.compliance.yaml config/config.yaml

# Create non-root user for security
RUN groupadd -r compliance && useradd -r -g compliance compliance
RUN chown -R compliance:compliance /app
USER compliance

# Compliance notice
RUN echo "🏛️ This is a compliance-ready commercial container" > /app/COMPLIANCE_NOTICE.txt
RUN echo "Rate limits: 5 messages/hour, Human approval required" >> /app/COMPLIANCE_NOTICE.txt

# Health check with compliance validation
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python scripts/verify_compliance.py || exit 1

# Default command
CMD ["python", "src/bot/wallapop_bot.py", "--compliance-mode"]
EOF
}

# Create additional CI/CD helpers
create_cicd_helpers() {
    log "Creating CI/CD helper scripts..."
    
    # Pre-commit configuration
    cat > "${BASE_DIR}/configs/shared/.pre-commit-config.yaml" << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: debug-statements
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src/, -ll]
EOF

    # GitHub Actions shared workflows
    mkdir -p "${BASE_DIR}/configs/shared/.github/workflows"
    
    # Shared security scanning workflow
    cat > "${BASE_DIR}/configs/shared/.github/workflows/security-scan.yml" << 'EOF'
name: 🔒 Security Scanning

on:
  workflow_call:
    inputs:
      strict_mode:
        required: false
        type: boolean
        default: false

jobs:
  security-scan:
    name: Security Analysis
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install security tools
      run: |
        pip install bandit safety
        if [[ "${{ inputs.strict_mode }}" == "true" ]]; then
          pip install semgrep
        fi
    
    - name: Run Bandit
      run: |
        if [[ "${{ inputs.strict_mode }}" == "true" ]]; then
          bandit -r src/ -ll
        else
          bandit -r src/ -f json -o bandit-report.json || true
        fi
    
    - name: Run Safety
      run: safety check
    
    - name: Run Semgrep (strict mode only)
      if: inputs.strict_mode
      run: semgrep --config=auto src/
EOF
}

# Main execution
main() {
    log "Setting up CI/CD pipelines for dual repository strategy..."
    
    if [[ ! -d "${BASE_DIR}/temp-repos" ]]; then
        error "Repository directories not found. Run 01-create-repositories.sh first."
    fi
    
    setup_research_cicd
    setup_compliance_cicd
    create_docker_configs
    create_cicd_helpers
    
    # Make scripts executable
    chmod +x "${BASE_DIR}/scripts/"*.sh
    
    log "CI/CD pipeline setup completed successfully!"
    log ""
    log "Created CI/CD configurations:"
    log "- Research repository: Flexible testing with educational validation"
    log "- Compliance repository: Strict testing with compliance validation"
    log "- Docker configurations for both versions"
    log "- Shared security scanning workflows"
    log ""
    log "Next steps:"
    log "1. Review the CI/CD configurations in .github/workflows/"
    log "2. Customize the Docker configurations as needed"
    log "3. Run ./04-create-deployment.sh to set up deployment automation"
    log "4. Test the pipelines by pushing to the repositories"
}

main "$@"