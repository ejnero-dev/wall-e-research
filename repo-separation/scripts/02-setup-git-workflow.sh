#!/bin/bash

# Git Workflow and Branching Strategy Setup Script
# This script configures Git workflows for both repositories

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

# Setup Git workflows for research repository
setup_research_workflow() {
    log "Setting up Git workflow for ${RESEARCH_REPO}..."
    
    cd "${BASE_DIR}/temp-repos/${RESEARCH_REPO}"
    
    # Create .gitignore for research version
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Database
*.db
*.sqlite3
pgdata/
redis-data/

# Logs
logs/
*.log

# Configuration files with secrets
config/config.yaml
.env.local
.env.production
secrets/

# Temporary files
tmp/
temp/
*.tmp

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Research-specific
experiments/
research-data/
analysis-results/
test-outputs/

# Docker
.docker/

# Coverage reports
htmlcov/
.coverage
.pytest_cache/

# MyPy
.mypy_cache/

# Node modules (if any frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Repository separation temp files
repo-separation/temp-repos/
sync-*.log
EOF

    # Create Git hooks for research repository
    mkdir -p .git/hooks
    
    # Pre-commit hook for research
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for wall-e-research

echo "🔬 Running pre-commit checks for research repository..."

# Check for secrets in staged files
if git diff --cached --name-only | xargs grep -l "password\|secret\|token\|key" 2>/dev/null; then
    echo "❌ Potential secrets detected in staged files!"
    echo "Please review and use environment variables or config files."
    exit 1
fi

# Run basic Python syntax check
python -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$") 2>/dev/null || {
    echo "❌ Python syntax errors detected!"
    exit 1
}

# Check for educational disclaimers in main files
if ! grep -q "Educational\|Research\|Learning" README.md; then
    echo "❌ Educational disclaimer missing from README.md"
    exit 1
fi

echo "✅ Pre-commit checks passed for research repository"
EOF

    chmod +x .git/hooks/pre-commit
    
    # Create pull request template for research
    mkdir -p .github/pull_request_template.md
    cat > .github/pull_request_template.md << 'EOF'
## 🔬 Research Repository Pull Request

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Research enhancement
- [ ] Educational improvement

### Description
Brief description of the changes and their purpose for educational/research use.

### Educational Value
How does this change benefit learning or research?

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Educational examples updated

### Compliance Considerations
- [ ] Changes are appropriate for educational use
- [ ] No production-ready exploits introduced
- [ ] Ethical guidelines maintained
- [ ] Rate limiting considerations documented

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Educational disclaimers maintained
EOF

    cd "${BASE_DIR}"
}

# Setup Git workflows for compliance repository
setup_compliance_workflow() {
    log "Setting up Git workflow for ${COMPLIANCE_REPO}..."
    
    cd "${BASE_DIR}/temp-repos/${COMPLIANCE_REPO}"
    
    # Create .gitignore for compliance version (stricter)
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Database
*.db
*.sqlite3
pgdata/
redis-data/

# Logs (STRICT - all log files)
logs/
*.log
audit-logs/
compliance-logs/

# Configuration files with secrets (STRICT)
config/config.yaml
config/*.yaml
.env*
secrets/
credentials/
keys/
certificates/

# Temporary files
tmp/
temp/
*.tmp

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Compliance-specific (STRICT)
user-data/
conversations/
personal-data/
gdpr-data/
audit-trails/
compliance-reports/
sensitive-data/

# Docker
.docker/

# Coverage reports
htmlcov/
.coverage
.pytest_cache/

# MyPy
.mypy_cache/

# Node modules (if any frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Repository separation temp files
repo-separation/temp-repos/
sync-*.log

# Backup files
*.bak
backup/
backups/

# Any files containing user data
*-userdata.*
*-conversations.*
*-personal.*
EOF

    # Create stricter Git hooks for compliance repository
    mkdir -p .git/hooks
    
    # Pre-commit hook for compliance
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for wall-e-compliance (STRICT)

echo "🏛️ Running STRICT pre-commit checks for compliance repository..."

# Check for any secrets or sensitive data
if git diff --cached --name-only | xargs grep -i -l "password\|secret\|token\|key\|api_key\|private\|credential" 2>/dev/null; then
    echo "❌ CRITICAL: Secrets or credentials detected in staged files!"
    echo "This is STRICTLY PROHIBITED in the compliance repository."
    exit 1
fi

# Check for personal data patterns
if git diff --cached --name-only | xargs grep -i -l "email\|phone\|address\|name.*=" 2>/dev/null; then
    echo "⚠️  WARNING: Potential personal data detected in staged files!"
    echo "Please ensure GDPR compliance and data anonymization."
    read -p "Continue? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        exit 1
    fi
fi

# Check for aggressive rate limiting settings
if git diff --cached --name-only | xargs grep -l "max_messages_per_hour.*[5-9][0-9]\|max_messages_per_hour.*[1-9][0-9][0-9]" 2>/dev/null; then
    echo "❌ CRITICAL: Rate limits exceed compliance thresholds!"
    echo "Compliance version must maintain max_messages_per_hour <= 5"
    exit 1
fi

# Ensure compliance rate limits are in place
if git diff --cached --name-only | grep -q "config.*\.yaml"; then
    if ! git diff --cached | grep -q "require_human_approval.*true"; then
        echo "❌ CRITICAL: Human approval requirement missing in config changes!"
        exit 1
    fi
fi

# Run Python syntax check
python -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$") 2>/dev/null || {
    echo "❌ Python syntax errors detected!"
    exit 1
}

# Check for compliance disclaimers
if ! grep -q "Compliance\|GDPR\|Commercial" README.md; then
    echo "❌ Compliance disclaimers missing from README.md"
    exit 1
fi

echo "✅ STRICT pre-commit checks passed for compliance repository"
EOF

    chmod +x .git/hooks/pre-commit
    
    # Create pull request template for compliance
    mkdir -p .github/pull_request_template.md
    cat > .github/pull_request_template.md << 'EOF'
## 🏛️ Compliance Repository Pull Request

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Compliance enhancement
- [ ] Security improvement
- [ ] GDPR compliance feature
- [ ] Rate limiting adjustment
- [ ] Documentation update

### Description
Brief description of the changes and their compliance implications.

### Compliance Impact Assessment
- [ ] No personal data exposure risk
- [ ] Rate limits maintained within compliance thresholds
- [ ] Human approval workflows preserved
- [ ] GDPR compliance maintained
- [ ] Legal review completed (if required)

### Security Review
- [ ] No credential exposure
- [ ] No sensitive data in code
- [ ] Security scanning completed
- [ ] Vulnerability assessment passed

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Compliance tests pass
- [ ] Rate limiting tests pass
- [ ] GDPR compliance tests pass

### Legal Compliance
- [ ] Terms of Service compliance verified
- [ ] Privacy policy compliance verified
- [ ] Data protection laws compliance verified
- [ ] Commercial use authorization confirmed

### Required Approvals
- [ ] Technical review completed
- [ ] Compliance officer approval (if applicable)
- [ ] Legal review (for major changes)
- [ ] Security team approval

### Risk Assessment
**Low Risk** / **Medium Risk** / **High Risk**

Explain the risk level and mitigation measures.

### Rollback Plan
Describe the rollback procedure if issues arise post-deployment.
EOF

    cd "${BASE_DIR}"
}

# Create workflow documentation
create_workflow_docs() {
    log "Creating workflow documentation..."
    
    mkdir -p "${BASE_DIR}/docs"
    
    cat > "${BASE_DIR}/docs/git-workflow.md" << 'EOF'
# Git Workflow Strategy for Dual Repository Setup

## Overview
This document outlines the Git workflow strategy for maintaining two synchronized repositories:
- `wall-e-research`: Educational/research version
- `wall-e-compliance`: Commercial-ready ethical version

## Branching Strategy

### Research Repository (wall-e-research)
```
main
├── develop
├── feature/*
├── research/*
├── experiment/*
└── educational/*
```

**Branch Purposes:**
- `main`: Stable educational version
- `develop`: Integration branch for educational features
- `feature/*`: New functionality development
- `research/*`: Experimental research branches
- `experiment/*`: Temporary experimental branches
- `educational/*`: Educational content improvements

### Compliance Repository (wall-e-compliance)
```
main
├── develop
├── feature/*
├── compliance/*
├── security/*
└── hotfix/*
```

**Branch Purposes:**
- `main`: Production-ready compliant version
- `develop`: Integration branch for compliance features
- `feature/*`: New compliant functionality
- `compliance/*`: Compliance-specific enhancements
- `security/*`: Security improvements
- `hotfix/*`: Critical production fixes

## Workflow Rules

### Research Repository
1. **Feature Development:**
   - Create feature branch from `develop`
   - Educational disclaimers required
   - Merge to `develop` via PR
   - Regular merge to `main`

2. **Pull Request Requirements:**
   - 1 reviewer minimum
   - Educational value assessment
   - Ethical guidelines compliance
   - Basic security checks

3. **Commit Message Format:**
   ```
   🔬 [type]: brief description
   
   Detailed explanation of educational/research value
   ```

### Compliance Repository
1. **Feature Development:**
   - Create feature branch from `develop`
   - Compliance impact assessment required
   - Legal review for major changes
   - Merge to `develop` via PR with 2+ reviews
   - Staged deployment to `main`

2. **Pull Request Requirements:**
   - 2 reviewers minimum (1 technical, 1 compliance)
   - Compliance officer approval for sensitive changes
   - Security team review
   - Legal review (for major features)
   - Full test suite execution

3. **Commit Message Format:**
   ```
   🏛️ [type]: brief description
   
   Compliance impact:
   - Legal implications
   - Privacy considerations
   - Security measures
   ```

## Synchronization Strategy

### Source → Research (Permissive)
- All changes from source can be merged
- Educational disclaimers added automatically
- Rate limits remain configurable

### Source → Compliance (Selective)
- Changes filtered through compliance layer
- Rate limits enforced at maximum safe levels
- Human approval requirements maintained
- Personal data handling enhanced

### Research → Compliance (Restricted)
- Manual review required
- Compliance transformation applied
- Security audit mandatory

## Emergency Procedures

### Research Repository
1. Revert problematic commits
2. Notify educational users
3. Update documentation

### Compliance Repository
1. Immediate rollback for compliance violations
2. Incident report generation
3. Stakeholder notification
4. Legal team involvement (if needed)
5. Audit trail preservation

## Quality Gates

### Research Repository
- [ ] Python syntax validation
- [ ] Educational disclaimer presence
- [ ] Basic security scan
- [ ] Unit tests pass

### Compliance Repository
- [ ] Python syntax validation
- [ ] Compliance disclaimer presence
- [ ] Comprehensive security scan
- [ ] Rate limit validation
- [ ] GDPR compliance check
- [ ] Unit + integration tests pass
- [ ] Compliance tests pass

## Automation

### Automated Synchronization
- Daily sync from source to research (automatic)
- Weekly sync from source to compliance (manual approval)
- Compliance transformation applied automatically

### Automated Testing
- Pre-commit hooks for both repositories
- CI/CD pipeline validation
- Security scanning
- Compliance checking

## Monitoring and Metrics

### Key Metrics
- Sync success rate
- Compliance violations
- Security incidents
- Pull request approval time
- Test coverage

### Alerting
- Failed synchronization
- Compliance violations
- Security vulnerabilities
- Unauthorized changes

## Tools and Integration

### Required Tools
- Git (version control)
- GitHub CLI (repository management)
- Pre-commit hooks
- Security scanners
- Compliance validators

### Optional Tools
- GitKraken (visual Git interface)
- GitHub Desktop
- VS Code Git integration
EOF

    log "Workflow documentation created at ${BASE_DIR}/docs/git-workflow.md"
}

# Create synchronization script template
create_sync_script() {
    log "Creating synchronization script template..."
    
    cat > "${BASE_DIR}/scripts/sync-repositories.sh" << 'EOF'
#!/bin/bash

# Repository Synchronization Script
# Synchronizes changes between source and target repositories

set -euo pipefail

# Configuration
SOURCE_REPO_PATH="${1:-../}"
RESEARCH_REPO_PATH="${2:-temp-repos/wall-e-research}"
COMPLIANCE_REPO_PATH="${3:-temp-repos/wall-e-compliance}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[SYNC]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Sync to research repository (permissive)
sync_to_research() {
    log "Syncing to research repository..."
    
    cd "$RESEARCH_REPO_PATH"
    
    # Fetch latest changes from source
    git remote add source "$SOURCE_REPO_PATH" 2>/dev/null || true
    git fetch source
    
    # Merge changes (with conflict resolution strategy)
    git merge source/main --no-edit --strategy=recursive --strategy-option=theirs || {
        warn "Merge conflicts detected in research sync"
        git status
        return 1
    }
    
    # Ensure educational disclaimers are maintained
    if ! grep -q "Educational\|Research" README.md; then
        warn "Educational disclaimers missing, restoring..."
        # Restore educational README template
    fi
    
    log "Research repository sync completed"
}

# Sync to compliance repository (selective)
sync_to_compliance() {
    log "Syncing to compliance repository (selective)..."
    
    cd "$COMPLIANCE_REPO_PATH"
    
    # Fetch latest changes from source
    git remote add source "$SOURCE_REPO_PATH" 2>/dev/null || true
    git fetch source
    
    # Create temporary branch for selective merge
    git checkout -b sync-temp-$(date +%s)
    
    # Cherry-pick safe commits (exclude aggressive features)
    # This requires manual review for each sync
    warn "Compliance sync requires manual review"
    warn "Review source changes and cherry-pick appropriate commits"
    
    log "Compliance repository sync prepared (manual review required)"
}

# Main execution
main() {
    log "Starting repository synchronization..."
    
    if [[ ! -d "$SOURCE_REPO_PATH" ]]; then
        error "Source repository not found: $SOURCE_REPO_PATH"
    fi
    
    if [[ -d "$RESEARCH_REPO_PATH" ]]; then
        sync_to_research
    else
        warn "Research repository not found: $RESEARCH_REPO_PATH"
    fi
    
    if [[ -d "$COMPLIANCE_REPO_PATH" ]]; then
        sync_to_compliance
    else
        warn "Compliance repository not found: $COMPLIANCE_REPO_PATH"
    fi
    
    log "Synchronization process completed"
}

main "$@"
EOF

    chmod +x "${BASE_DIR}/scripts/sync-repositories.sh"
    log "Synchronization script created at ${BASE_DIR}/scripts/sync-repositories.sh"
}

# Main execution
main() {
    log "Setting up Git workflows for dual repository strategy..."
    
    if [[ ! -d "${BASE_DIR}/temp-repos" ]]; then
        error "Repository directories not found. Run 01-create-repositories.sh first."
    fi
    
    setup_research_workflow
    setup_compliance_workflow
    create_workflow_docs
    create_sync_script
    
    log "Git workflow setup completed successfully!"
    log ""
    log "Next steps:"
    log "1. Review the workflow documentation in docs/git-workflow.md"
    log "2. Customize the Git hooks as needed"
    log "3. Run ./03-setup-cicd.sh to configure CI/CD pipelines"
    log "4. Test the synchronization script"
}

main "$@"