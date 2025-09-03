#!/bin/bash

# Repository Creation and Initial Setup Script
# This script creates the two target repositories and sets up the initial structure

set -euo pipefail

# Configuration
ORIGINAL_REPO="project-wall-e"
RESEARCH_REPO="wall-e-research"
COMPLIANCE_REPO="wall-e-compliance"
GITHUB_USERNAME="${GITHUB_USERNAME:-your-username}"
BASE_DIR="${PWD}"

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v git &> /dev/null; then
        error "Git is not installed"
    fi
    
    if ! command -v gh &> /dev/null; then
        warn "GitHub CLI (gh) not found. You'll need to create repositories manually"
        USE_GH_CLI=false
    else
        USE_GH_CLI=true
    fi
    
    if [[ -z "${GITHUB_TOKEN:-}" ]] && [[ "$USE_GH_CLI" == "true" ]]; then
        warn "GITHUB_TOKEN not set. Make sure you're authenticated with 'gh auth login'"
    fi
}

# Create directory structure
create_directory_structure() {
    log "Creating directory structure..."
    
    mkdir -p "${BASE_DIR}/temp-repos"
    cd "${BASE_DIR}/temp-repos"
}

# Create research repository
create_research_repo() {
    log "Creating ${RESEARCH_REPO} repository..."
    
    # Clone original repository
    if [[ ! -d "$RESEARCH_REPO" ]]; then
        git clone "${BASE_DIR}/../" "$RESEARCH_REPO"
        cd "$RESEARCH_REPO"
        
        # Remove existing origin and add new one
        git remote remove origin
        
        if [[ "$USE_GH_CLI" == "true" ]]; then
            # Create repository on GitHub
            gh repo create "$RESEARCH_REPO" \
                --description "Educational Wallapop automation framework for research and learning purposes" \
                --public \
                --clone=false
            
            git remote add origin "https://github.com/${GITHUB_USERNAME}/${RESEARCH_REPO}.git"
        else
            log "Please create repository ${RESEARCH_REPO} manually on GitHub and update the remote:"
            log "git remote add origin https://github.com/${GITHUB_USERNAME}/${RESEARCH_REPO}.git"
        fi
        
        # Create research-specific branch structure
        git checkout -b main
        git checkout -b develop
        git checkout -b feature/research-enhancements
        git checkout main
        
        # Update README for research version
        cp "${BASE_DIR}/../repo-separation/templates/README-research.md" README.md
        
        # Add research-specific configuration
        mkdir -p .github/workflows
        cp "${BASE_DIR}/../repo-separation/configs/research/"*.yml .github/workflows/ 2>/dev/null || true
        
        # Commit initial changes
        git add .
        git commit -m "🔬 Initialize wall-e-research repository

- Educational/research version of Wallapop automation
- Full technical implementation for learning purposes
- Educational disclaimers and ethical guidelines included
- Configurable rate limits for research scenarios

Generated with repository separation strategy"
        
        # Push if remote is configured
        if git remote get-url origin &>/dev/null; then
            git push -u origin main
            git push origin develop
            git push origin feature/research-enhancements
        fi
        
        cd ..
    else
        log "${RESEARCH_REPO} already exists, skipping..."
    fi
}

# Create compliance repository
create_compliance_repo() {
    log "Creating ${COMPLIANCE_REPO} repository..."
    
    if [[ ! -d "$COMPLIANCE_REPO" ]]; then
        # Clone research repository as base
        git clone "$RESEARCH_REPO" "$COMPLIANCE_REPO"
        cd "$COMPLIANCE_REPO"
        
        # Remove existing origin and add new one
        git remote remove origin
        
        if [[ "$USE_GH_CLI" == "true" ]]; then
            # Create repository on GitHub
            gh repo create "$COMPLIANCE_REPO" \
                --description "Commercial-ready ethical Wallapop automation with compliance controls" \
                --private \
                --clone=false
            
            git remote add origin "https://github.com/${GITHUB_USERNAME}/${COMPLIANCE_REPO}.git"
        else
            log "Please create repository ${COMPLIANCE_REPO} manually on GitHub and update the remote:"
            log "git remote add origin https://github.com/${GITHUB_USERNAME}/${COMPLIANCE_REPO}.git"
        fi
        
        # Create compliance-specific branch structure
        git checkout -b main
        git checkout -b develop
        git checkout -b feature/compliance-controls
        git checkout main
        
        # Update README for compliance version
        cp "${BASE_DIR}/../repo-separation/templates/README-compliance.md" README.md
        
        # Add compliance-specific configuration
        mkdir -p .github/workflows
        cp "${BASE_DIR}/../repo-separation/configs/compliance/"*.yml .github/workflows/ 2>/dev/null || true
        
        # Add compliance layer
        mkdir -p src/compliance
        cat > src/compliance/__init__.py << 'EOF'
"""
Compliance layer for wall-e-compliance repository.
Enforces ethical constraints and regulatory compliance.
"""

from .rate_limiter import ComplianceRateLimiter
from .human_approval import HumanApprovalSystem
from .gdpr_compliance import GDPRComplianceManager
from .audit_logger import ComplianceAuditLogger

__all__ = [
    'ComplianceRateLimiter',
    'HumanApprovalSystem', 
    'GDPRComplianceManager',
    'ComplianceAuditLogger'
]
EOF

        # Create compliance configuration
        cp "${BASE_DIR}/../repo-separation/configs/compliance/config.compliance.yaml" config/
        
        # Commit initial changes
        git add .
        git commit -m "🏛️ Initialize wall-e-compliance repository

- Commercial-ready ethical version with compliance controls
- Rate-limited (max 5 actions/hour, 3 concurrent conversations)
- Human approval required for all critical actions
- GDPR compliance features implemented
- Comprehensive audit logging and monitoring

Generated with repository separation strategy"
        
        # Push if remote is configured
        if git remote get-url origin &>/dev/null; then
            git push -u origin main
            git push origin develop
            git push origin feature/compliance-controls
        fi
        
        cd ..
    else
        log "${COMPLIANCE_REPO} already exists, skipping..."
    fi
}

# Set up repository configuration
setup_repo_config() {
    log "Setting up repository configurations..."
    
    # Research repository
    if [[ -d "$RESEARCH_REPO" ]]; then
        cd "$RESEARCH_REPO"
        
        # Set up branch protection (requires GitHub API or manual setup)
        if [[ "$USE_GH_CLI" == "true" ]]; then
            gh api repos/${GITHUB_USERNAME}/${RESEARCH_REPO}/branches/main/protection \
                --method PUT \
                --field required_status_checks='{"strict":true,"contexts":["ci/tests","ci/security-scan"]}' \
                --field enforce_admins=true \
                --field required_pull_request_reviews='{"required_approving_review_count":1}' \
                --field restrictions=null 2>/dev/null || warn "Could not set branch protection for ${RESEARCH_REPO}"
        fi
        
        cd ..
    fi
    
    # Compliance repository
    if [[ -d "$COMPLIANCE_REPO" ]]; then
        cd "$COMPLIANCE_REPO"
        
        # Set up stricter branch protection
        if [[ "$USE_GH_CLI" == "true" ]]; then
            gh api repos/${GITHUB_USERNAME}/${COMPLIANCE_REPO}/branches/main/protection \
                --method PUT \
                --field required_status_checks='{"strict":true,"contexts":["ci/tests","ci/security-scan","ci/compliance-check"]}' \
                --field enforce_admins=true \
                --field required_pull_request_reviews='{"required_approving_review_count":2,"require_code_owner_reviews":true}' \
                --field restrictions=null 2>/dev/null || warn "Could not set branch protection for ${COMPLIANCE_REPO}"
        fi
        
        cd ..
    fi
}

# Create sync configuration
create_sync_config() {
    log "Creating synchronization configuration..."
    
    cat > "${BASE_DIR}/sync-config.json" << EOF
{
  "repositories": {
    "source": {
      "name": "project-wall-e",
      "path": "${BASE_DIR}/../",
      "branch": "main"
    },
    "targets": [
      {
        "name": "wall-e-research",
        "path": "${BASE_DIR}/temp-repos/wall-e-research",
        "branch": "main",
        "sync_strategy": "merge",
        "excluded_paths": [
          "repo-separation/",
          "temp-repos/"
        ]
      },
      {
        "name": "wall-e-compliance",
        "path": "${BASE_DIR}/temp-repos/wall-e-compliance", 
        "branch": "main",
        "sync_strategy": "selective",
        "excluded_paths": [
          "repo-separation/",
          "temp-repos/",
          "config/config.example.yaml"
        ],
        "compliance_transforms": [
          {
            "file": "config/config.yaml",
            "template": "config.compliance.yaml"
          }
        ]
      }
    ]
  },
  "sync_schedule": "0 2 * * *",
  "notification_webhook": null
}
EOF

    log "Sync configuration created at ${BASE_DIR}/sync-config.json"
}

# Main execution
main() {
    log "Starting repository creation process..."
    
    check_prerequisites
    create_directory_structure
    
    create_research_repo
    create_compliance_repo
    
    setup_repo_config
    create_sync_config
    
    log "Repository creation completed successfully!"
    log ""
    log "Next steps:"
    log "1. Run ./02-setup-git-workflow.sh to configure Git workflows"
    log "2. Review and customize the repository configurations"
    log "3. Set up CI/CD pipelines with ./03-setup-cicd.sh"
    log ""
    log "Created repositories:"
    log "- Research: ${BASE_DIR}/temp-repos/${RESEARCH_REPO}"
    log "- Compliance: ${BASE_DIR}/temp-repos/${COMPLIANCE_REPO}"
}

# Execute main function
main "$@"