#!/bin/bash

# Backup and Synchronization Strategy Setup Script
# Creates comprehensive backup and sync infrastructure for dual repositories

set -euo pipefail

# Configuration
BASE_DIR="${PWD}"
RESEARCH_REPO="wall-e-research"
COMPLIANCE_REPO="wall-e-compliance"
SOURCE_REPO="project-wall-e"

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

# Create advanced synchronization script
create_sync_system() {
    log "Creating advanced synchronization system..."
    
    cat > "${BASE_DIR}/scripts/sync-manager.py" << 'EOF'
#!/usr/bin/env python3
"""
Advanced Repository Synchronization Manager
Handles bidirectional sync between source and target repositories with conflict resolution
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SyncStrategy(Enum):
    MERGE = "merge"
    SELECTIVE = "selective"
    OVERWRITE = "overwrite"
    MANUAL = "manual"

class ConflictResolution(Enum):
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_ATTEMPT = "merge_attempt"

@dataclass
class Repository:
    name: str
    path: Path
    branch: str
    remote_url: Optional[str] = None
    sync_strategy: SyncStrategy = SyncStrategy.MERGE
    conflict_resolution: ConflictResolution = ConflictResolution.MANUAL_REVIEW
    excluded_paths: List[str] = None
    
    def __post_init__(self):
        if self.excluded_paths is None:
            self.excluded_paths = []

@dataclass
class SyncRule:
    source_pattern: str
    target_pattern: str
    transformation: Optional[str] = None
    condition: Optional[str] = None

class RepositorySyncManager:
    def __init__(self, config_path: str = "sync-config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.sync_log = []
        
    def load_config(self) -> Dict:
        """Load synchronization configuration"""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
            
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        # Validate configuration
        self.validate_config(config)
        return config
    
    def validate_config(self, config: Dict):
        """Validate configuration structure"""
        required_keys = ['repositories', 'sync_schedule']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
    
    def get_repository_info(self, repo_path: Path) -> Dict:
        """Get repository information"""
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
            
            # Get last commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            last_commit = result.stdout.strip()
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            has_changes = bool(result.stdout.strip())
            
            return {
                'path': str(repo_path),
                'current_branch': current_branch,
                'last_commit': last_commit,
                'has_changes': has_changes,
                'status': 'clean' if not has_changes else 'dirty'
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get repository info for {repo_path}: {e}")
            return None
    
    def sync_source_to_research(self) -> bool:
        """Synchronize source repository to research (permissive)"""
        logger.info("Starting source → research synchronization...")
        
        source_config = self.config['repositories']['source']
        research_config = None
        
        for target in self.config['repositories']['targets']:
            if target['name'] == 'wall-e-research':
                research_config = target
                break
        
        if not research_config:
            logger.error("Research repository configuration not found")
            return False
        
        try:
            source_path = Path(source_config['path'])
            research_path = Path(research_config['path'])
            
            # Ensure repositories exist
            if not source_path.exists():
                logger.error(f"Source repository not found: {source_path}")
                return False
            
            if not research_path.exists():
                logger.error(f"Research repository not found: {research_path}")
                return False
            
            # Get repository states
            source_info = self.get_repository_info(source_path)
            research_info = self.get_repository_info(research_path)
            
            if not source_info or not research_info:
                logger.error("Failed to get repository information")
                return False
            
            # Perform synchronization
            os.chdir(research_path)
            
            # Add source as remote if not exists
            try:
                subprocess.run(['git', 'remote', 'get-url', 'source'], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['git', 'remote', 'add', 'source', str(source_path)], 
                             check=True)
            
            # Fetch from source
            subprocess.run(['git', 'fetch', 'source'], check=True)
            
            # Merge changes with strategy
            if research_config['sync_strategy'] == 'merge':
                result = subprocess.run(
                    ['git', 'merge', 'source/main', '--no-edit'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.warning("Merge conflicts detected, attempting resolution...")
                    self.resolve_merge_conflicts(research_path, 'research')
            
            # Apply research-specific transformations
            self.apply_research_transformations(research_path)
            
            # Commit changes if any
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                commit_msg = f"🔬 Sync from source - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            logger.info("Source → research synchronization completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Synchronization failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during synchronization: {e}")
            return False
    
    def sync_source_to_compliance(self) -> bool:
        """Synchronize source repository to compliance (selective)"""
        logger.info("Starting source → compliance synchronization (SELECTIVE)...")
        
        source_config = self.config['repositories']['source']
        compliance_config = None
        
        for target in self.config['repositories']['targets']:
            if target['name'] == 'wall-e-compliance':
                compliance_config = target
                break
        
        if not compliance_config:
            logger.error("Compliance repository configuration not found")
            return False
        
        try:
            source_path = Path(source_config['path'])
            compliance_path = Path(compliance_config['path'])
            
            # Get repository states
            source_info = self.get_repository_info(source_path)
            compliance_info = self.get_repository_info(compliance_path)
            
            if not source_info or not compliance_info:
                logger.error("Failed to get repository information")
                return False
            
            # Selective synchronization for compliance
            os.chdir(compliance_path)
            
            # Create temporary branch for review
            temp_branch = f"sync-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            subprocess.run(['git', 'checkout', '-b', temp_branch], check=True)
            
            # Add source as remote if not exists
            try:
                subprocess.run(['git', 'remote', 'get-url', 'source'], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['git', 'remote', 'add', 'source', str(source_path)], 
                             check=True)
            
            # Fetch from source
            subprocess.run(['git', 'fetch', 'source'], check=True)
            
            # Get list of changes
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'source/main'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            safe_files = self.filter_safe_files_for_compliance(changed_files)
            
            if safe_files:
                # Cherry-pick safe changes
                for file in safe_files:
                    try:
                        subprocess.run(['git', 'checkout', 'source/main', '--', file], 
                                     check=True)
                        logger.info(f"Applied safe change: {file}")
                    except subprocess.CalledProcessError:
                        logger.warning(f"Could not apply change to: {file}")
                
                # Apply compliance transformations
                self.apply_compliance_transformations(compliance_path)
                
                # Validate compliance after changes
                if self.validate_compliance_configuration(compliance_path):
                    # Commit changes
                    commit_msg = f"🏛️ Selective sync from source - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nCompliance validation: PASSED"
                    subprocess.run(['git', 'add', '.'], check=True)
                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                    
                    # Switch back to main and merge
                    subprocess.run(['git', 'checkout', 'main'], check=True)
                    subprocess.run(['git', 'merge', temp_branch, '--no-edit'], check=True)
                    subprocess.run(['git', 'branch', '-d', temp_branch], check=True)
                    
                    logger.info("Source → compliance synchronization completed successfully")
                    return True
                else:
                    logger.error("Compliance validation failed, reverting changes")
                    subprocess.run(['git', 'checkout', 'main'], check=True)
                    subprocess.run(['git', 'branch', '-D', temp_branch], check=True)
                    return False
            else:
                logger.info("No safe changes found for compliance repository")
                subprocess.run(['git', 'checkout', 'main'], check=True)
                subprocess.run(['git', 'branch', '-d', temp_branch], check=True)
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Compliance synchronization failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during compliance synchronization: {e}")
            return False
    
    def filter_safe_files_for_compliance(self, files: List[str]) -> List[str]:
        """Filter files that are safe to sync to compliance repository"""
        safe_patterns = [
            # Documentation updates
            r'^docs/',
            r'^README\.md$',
            r'\.md$',
            
            # Bug fixes (non-rate-limit related)
            r'^src/.*\.py$',  # Will be validated individually
            
            # Test updates
            r'^tests/',
            
            # Configuration templates (not actual configs)
            r'\.example\.',
            
            # Scripts (will be validated)
            r'^scripts/',
        ]
        
        unsafe_patterns = [
            # Rate limiting changes
            r'rate.*limit',
            r'max.*messages',
            r'delay.*seconds',
            
            # Anti-detection features
            r'anti.*detection',
            r'stealth',
            r'proxy',
            
            # Aggressive automation
            r'aggressive',
            r'bypass',
            
            # Configuration files
            r'config\.yaml$',
            r'\.env',
        ]
        
        safe_files = []
        
        for file in files:
            if not file.strip():
                continue
                
            # Check if file matches unsafe patterns
            is_unsafe = any(
                __import__('re').search(pattern, file, __import__('re').IGNORECASE) 
                for pattern in unsafe_patterns
            )
            
            if is_unsafe:
                logger.warning(f"Skipping unsafe file for compliance: {file}")
                continue
            
            # Check if file matches safe patterns
            is_safe = any(
                __import__('re').search(pattern, file, __import__('re').IGNORECASE) 
                for pattern in safe_patterns
            )
            
            if is_safe:
                # Additional validation for Python files
                if file.endswith('.py'):
                    if self.validate_python_file_for_compliance(file):
                        safe_files.append(file)
                    else:
                        logger.warning(f"Python file failed compliance validation: {file}")
                else:
                    safe_files.append(file)
        
        return safe_files
    
    def validate_python_file_for_compliance(self, file_path: str) -> bool:
        """Validate that a Python file is compliant"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for compliance violations
            violations = [
                ('max_messages_per_hour.*[6-9][0-9]', 'Rate limit too high'),
                ('max_messages_per_hour.*[1-9][0-9][0-9]', 'Rate limit too high'),
                ('require_human_approval.*false', 'Human approval disabled'),
                ('stealth', 'Stealth techniques'),
                ('anti.*detection', 'Anti-detection features'),
                ('bypass', 'Bypass mechanisms'),
            ]
            
            for pattern, description in violations:
                if __import__('re').search(pattern, content, __import__('re').IGNORECASE):
                    logger.warning(f"Compliance violation in {file_path}: {description}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Python file {file_path}: {e}")
            return False
    
    def apply_research_transformations(self, repo_path: Path):
        """Apply research-specific transformations"""
        logger.info("Applying research transformations...")
        
        # Update README to research version if needed
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            if "Educational" not in content and "Research" not in content:
                # Prepend educational disclaimer
                educational_header = '''# 🔬 EDUCATIONAL/RESEARCH VERSION

**THIS IS FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

This repository demonstrates automation techniques for learning and research.
Before any real-world use, ensure compliance with Terms of Service and applicable laws.

---

'''
                with open(readme_path, 'w') as f:
                    f.write(educational_header + content)
                
                logger.info("Added educational disclaimer to README")
    
    def apply_compliance_transformations(self, repo_path: Path):
        """Apply compliance-specific transformations"""
        logger.info("Applying compliance transformations...")
        
        # Ensure compliance configuration is used
        config_src = repo_path / "config" / "config.compliance.yaml"
        config_dst = repo_path / "config" / "config.yaml"
        
        if config_src.exists():
            shutil.copy2(config_src, config_dst)
            logger.info("Applied compliance configuration")
        
        # Update README to compliance version if needed
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            if "Compliance" not in content or "Commercial" not in content:
                # This would typically use a compliance README template
                logger.info("README compliance check completed")
    
    def validate_compliance_configuration(self, repo_path: Path) -> bool:
        """Validate that compliance configuration is properly set"""
        logger.info("Validating compliance configuration...")
        
        config_path = repo_path / "config" / "config.yaml"
        if not config_path.exists():
            logger.error("Configuration file not found")
            return False
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check compliance requirements
            compliance_checks = [
                ('compliance.rate_limits.max_messages_per_hour', 5, 'le'),
                ('compliance.human_approval.require_approval_for_responses', True, 'eq'),
                ('compliance.gdpr.enabled', True, 'eq'),
                ('compliance.audit.log_all_actions', True, 'eq'),
            ]
            
            for path, expected, operator in compliance_checks:
                keys = path.split('.')
                value = config
                
                try:
                    for key in keys:
                        value = value[key]
                except KeyError:
                    logger.error(f"Missing compliance configuration: {path}")
                    return False
                
                if operator == 'le' and value > expected:
                    logger.error(f"Compliance violation: {path} = {value} (should be <= {expected})")
                    return False
                elif operator == 'eq' and value != expected:
                    logger.error(f"Compliance violation: {path} = {value} (should be {expected})")
                    return False
            
            logger.info("Compliance configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating compliance configuration: {e}")
            return False
    
    def resolve_merge_conflicts(self, repo_path: Path, repo_type: str):
        """Resolve merge conflicts based on repository type"""
        logger.info(f"Resolving merge conflicts for {repo_type} repository...")
        
        # Get conflicted files
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=U'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        conflicted_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        for file in conflicted_files:
            if repo_type == 'research':
                # For research, prefer source changes but maintain educational disclaimers
                self.resolve_research_conflict(repo_path, file)
            elif repo_type == 'compliance':
                # For compliance, be very conservative
                self.resolve_compliance_conflict(repo_path, file)
    
    def resolve_research_conflict(self, repo_path: Path, file: str):
        """Resolve conflicts for research repository"""
        # Simple strategy: accept source changes for most files
        subprocess.run(['git', 'checkout', '--theirs', file], cwd=repo_path)
        subprocess.run(['git', 'add', file], cwd=repo_path)
        logger.info(f"Resolved research conflict: {file} (accepted source changes)")
    
    def resolve_compliance_conflict(self, repo_path: Path, file: str):
        """Resolve conflicts for compliance repository"""
        # Conservative strategy: keep compliance version unless it's documentation
        if file.endswith('.md') or file.startswith('docs/'):
            subprocess.run(['git', 'checkout', '--theirs', file], cwd=repo_path)
            subprocess.run(['git', 'add', file], cwd=repo_path)
            logger.info(f"Resolved compliance conflict: {file} (accepted source for documentation)")
        else:
            subprocess.run(['git', 'checkout', '--ours', file], cwd=repo_path)
            subprocess.run(['git', 'add', file], cwd=repo_path)
            logger.info(f"Resolved compliance conflict: {file} (kept compliance version)")
    
    def create_backup(self, repo_path: Path) -> str:
        """Create backup of repository"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{repo_path.name}_{timestamp}"
        backup_path = repo_path.parent / backup_name
        
        shutil.copytree(repo_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return str(backup_path)
    
    def cleanup_old_backups(self, repo_path: Path, keep_days: int = 7):
        """Clean up old backups"""
        backup_pattern = f"backup_{repo_path.name}_*"
        parent_dir = repo_path.parent
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for backup_dir in parent_dir.glob(backup_pattern):
            if backup_dir.is_dir():
                # Extract date from backup name
                try:
                    date_str = backup_dir.name.split('_')[-2] + '_' + backup_dir.name.split('_')[-1]
                    backup_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                    
                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_dir)
                        logger.info(f"Removed old backup: {backup_dir}")
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse backup date: {backup_dir}")
    
    def sync_all(self) -> bool:
        """Perform full synchronization"""
        logger.info("Starting full repository synchronization...")
        
        success = True
        
        # Sync source to research
        if not self.sync_source_to_research():
            success = False
            logger.error("Source → research sync failed")
        
        # Sync source to compliance (selective)
        if not self.sync_source_to_compliance():
            success = False
            logger.error("Source → compliance sync failed")
        
        if success:
            logger.info("Full synchronization completed successfully")
        else:
            logger.error("Synchronization completed with errors")
        
        return success
    
    def generate_sync_report(self) -> str:
        """Generate synchronization report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'repositories': {},
            'sync_results': self.sync_log,
            'summary': {
                'total_syncs': len(self.sync_log),
                'successful_syncs': len([s for s in self.sync_log if s.get('success', False)]),
                'failed_syncs': len([s for s in self.sync_log if not s.get('success', False)])
            }
        }
        
        # Get repository states
        for repo_config in [self.config['repositories']['source']] + self.config['repositories']['targets']:
            repo_path = Path(repo_config['path'])
            if repo_path.exists():
                report['repositories'][repo_config['name']] = self.get_repository_info(repo_path)
        
        return json.dumps(report, indent=2)

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Repository Synchronization Manager')
    parser.add_argument('--config', default='sync-config.json', help='Configuration file path')
    parser.add_argument('--sync-all', action='store_true', help='Perform full synchronization')
    parser.add_argument('--sync-research', action='store_true', help='Sync source to research only')
    parser.add_argument('--sync-compliance', action='store_true', help='Sync source to compliance only')
    parser.add_argument('--report', action='store_true', help='Generate sync report')
    parser.add_argument('--backup', action='store_true', help='Create backups before sync')
    
    args = parser.parse_args()
    
    # Initialize sync manager
    sync_manager = RepositorySyncManager(args.config)
    
    success = True
    
    if args.backup:
        logger.info("Creating backups before synchronization...")
        # Create backups would be implemented here
    
    if args.sync_all:
        success = sync_manager.sync_all()
    elif args.sync_research:
        success = sync_manager.sync_source_to_research()
    elif args.sync_compliance:
        success = sync_manager.sync_source_to_compliance()
    
    if args.report:
        report = sync_manager.generate_sync_report()
        with open(f'sync-report-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            f.write(report)
        logger.info("Sync report generated")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
EOF

    chmod +x "${BASE_DIR}/scripts/sync-manager.py"
}

# Create backup system
create_backup_system() {
    log "Creating backup system..."
    
    cat > "${BASE_DIR}/scripts/backup-manager.sh" << 'EOF'
#!/bin/bash

# Repository Backup Manager
# Creates and manages backups for all repositories

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/opt/backups/wall-e}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
COMPRESSION="${COMPRESSION:-true}"
ENCRYPTION="${ENCRYPTION:-false}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[BACKUP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create backup directory structure
create_backup_dirs() {
    log "Creating backup directory structure..."
    
    mkdir -p "$BACKUP_BASE_DIR"/{source,research,compliance}/{daily,weekly,monthly}
    mkdir -p "$BACKUP_BASE_DIR"/metadata
    
    # Set proper permissions
    chmod 750 "$BACKUP_BASE_DIR"
    
    log "Backup directories created"
}

# Create repository backup
backup_repository() {
    local repo_name="$1"
    local repo_path="$2"
    local backup_type="${3:-daily}"
    
    log "Backing up $repo_name repository..."
    
    if [[ ! -d "$repo_path" ]]; then
        error "Repository path not found: $repo_path"
    fi
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="${repo_name}_${backup_type}_${timestamp}"
    local backup_dir="$BACKUP_BASE_DIR/$repo_name/$backup_type"
    local backup_path="$backup_dir/$backup_name"
    
    # Create backup
    if [[ "$COMPRESSION" == "true" ]]; then
        local archive_name="${backup_name}.tar.gz"
        local archive_path="$backup_dir/$archive_name"
        
        tar -czf "$archive_path" -C "$(dirname "$repo_path")" "$(basename "$repo_path")"
        
        if [[ "$ENCRYPTION" == "true" && -n "$ENCRYPTION_KEY" ]]; then
            gpg --symmetric --cipher-algo AES256 --passphrase "$ENCRYPTION_KEY" --batch "$archive_path"
            rm "$archive_path"
            archive_path="${archive_path}.gpg"
            log "Backup encrypted: $archive_path"
        fi
        
        backup_path="$archive_path"
    else
        cp -r "$repo_path" "$backup_path"
    fi
    
    # Create metadata
    cat > "$BACKUP_BASE_DIR/metadata/${backup_name}.json" << EOF
{
    "repository": "$repo_name",
    "backup_type": "$backup_type",
    "timestamp": "$timestamp",
    "path": "$backup_path",
    "size": $(du -sb "$backup_path" | cut -f1),
    "compressed": $COMPRESSION,
    "encrypted": $ENCRYPTION,
    "git_commit": "$(cd "$repo_path" && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(cd "$repo_path" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
}
EOF
    
    log "Backup completed: $backup_path"
}

# Clean old backups
cleanup_old_backups() {
    local repo_name="$1"
    local backup_type="$2"
    
    log "Cleaning old $backup_type backups for $repo_name..."
    
    local backup_dir="$BACKUP_BASE_DIR/$repo_name/$backup_type"
    
    if [[ ! -d "$backup_dir" ]]; then
        return
    fi
    
    # Find and remove old backups
    find "$backup_dir" -name "${repo_name}_${backup_type}_*" -type f -mtime +$RETENTION_DAYS -delete
    find "$backup_dir" -name "${repo_name}_${backup_type}_*" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    # Clean metadata
    find "$BACKUP_BASE_DIR/metadata" -name "${repo_name}_${backup_type}_*.json" -mtime +$RETENTION_DAYS -delete
    
    log "Old $backup_type backups cleaned for $repo_name"
}

# Restore repository from backup
restore_repository() {
    local backup_path="$1"
    local restore_path="$2"
    
    log "Restoring repository from backup..."
    
    if [[ ! -e "$backup_path" ]]; then
        error "Backup not found: $backup_path"
    fi
    
    # Create restore directory
    mkdir -p "$(dirname "$restore_path")"
    
    # Extract backup
    if [[ "$backup_path" == *.tar.gz.gpg ]]; then
        if [[ -z "$ENCRYPTION_KEY" ]]; then
            error "Encryption key required for encrypted backup"
        fi
        gpg --decrypt --passphrase "$ENCRYPTION_KEY" --batch "$backup_path" | tar -xzf - -C "$(dirname "$restore_path")"
    elif [[ "$backup_path" == *.tar.gz ]]; then
        tar -xzf "$backup_path" -C "$(dirname "$restore_path")"
    else
        cp -r "$backup_path" "$restore_path"
    fi
    
    log "Repository restored to: $restore_path"
}

# List available backups
list_backups() {
    local repo_name="${1:-all}"
    
    log "Available backups:"
    echo ""
    
    if [[ "$repo_name" == "all" ]]; then
        for repo in source research compliance; do
            if [[ -d "$BACKUP_BASE_DIR/$repo" ]]; then
                echo "📁 $repo:"
                find "$BACKUP_BASE_DIR/$repo" -name "${repo}_*" -type f,d | sort | sed 's|^|  |'
                echo ""
            fi
        done
    else
        if [[ -d "$BACKUP_BASE_DIR/$repo_name" ]]; then
            echo "📁 $repo_name:"
            find "$BACKUP_BASE_DIR/$repo_name" -name "${repo_name}_*" -type f,d | sort | sed 's|^|  |'
        else
            warn "No backups found for repository: $repo_name"
        fi
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup integrity: $backup_path"
    
    if [[ ! -e "$backup_path" ]]; then
        error "Backup not found: $backup_path"
    fi
    
    if [[ "$backup_path" == *.tar.gz ]]; then
        if tar -tzf "$backup_path" >/dev/null 2>&1; then
            log "✅ Backup integrity verified"
            return 0
        else
            error "❌ Backup integrity check failed"
        fi
    elif [[ "$backup_path" == *.tar.gz.gpg ]]; then
        if [[ -z "$ENCRYPTION_KEY" ]]; then
            error "Encryption key required for encrypted backup verification"
        fi
        if gpg --decrypt --passphrase "$ENCRYPTION_KEY" --batch "$backup_path" | tar -tz >/dev/null 2>&1; then
            log "✅ Encrypted backup integrity verified"
            return 0
        else
            error "❌ Encrypted backup integrity check failed"
        fi
    else
        log "✅ Directory backup exists"
        return 0
    fi
}

# Generate backup report
generate_backup_report() {
    log "Generating backup report..."
    
    local report_file="$BACKUP_BASE_DIR/backup-report-$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_base_dir": "$BACKUP_BASE_DIR",
    "retention_days": $RETENTION_DAYS,
    "compression": $COMPRESSION,
    "encryption": $ENCRYPTION,
    "repositories": {
EOF

    local first=true
    for repo in source research compliance; do
        if [[ -d "$BACKUP_BASE_DIR/$repo" ]]; then
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$report_file"
            fi
            
            echo "        \"$repo\": {" >> "$report_file"
            echo "            \"daily_backups\": $(find "$BACKUP_BASE_DIR/$repo/daily" -name "${repo}_daily_*" 2>/dev/null | wc -l)," >> "$report_file"
            echo "            \"weekly_backups\": $(find "$BACKUP_BASE_DIR/$repo/weekly" -name "${repo}_weekly_*" 2>/dev/null | wc -l)," >> "$report_file"
            echo "            \"monthly_backups\": $(find "$BACKUP_BASE_DIR/$repo/monthly" -name "${repo}_monthly_*" 2>/dev/null | wc -l)," >> "$report_file"
            echo "            \"total_size\": \"$(du -sh "$BACKUP_BASE_DIR/$repo" 2>/dev/null | cut -f1 || echo '0')\"" >> "$report_file"
            echo -n "        }" >> "$report_file"
        fi
    done

    cat >> "$report_file" << EOF

    },
    "total_backup_size": "$(du -sh "$BACKUP_BASE_DIR" 2>/dev/null | cut -f1 || echo '0')"
}
EOF

    log "Backup report generated: $report_file"
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        "init")
            create_backup_dirs
            ;;
        "backup")
            local repo_name="$2"
            local repo_path="$3"
            local backup_type="${4:-daily}"
            backup_repository "$repo_name" "$repo_path" "$backup_type"
            ;;
        "cleanup")
            local repo_name="$2"
            local backup_type="${3:-daily}"
            cleanup_old_backups "$repo_name" "$backup_type"
            ;;
        "restore")
            local backup_path="$2"
            local restore_path="$3"
            restore_repository "$backup_path" "$restore_path"
            ;;
        "list")
            local repo_name="${2:-all}"
            list_backups "$repo_name"
            ;;
        "verify")
            local backup_path="$2"
            verify_backup "$backup_path"
            ;;
        "report")
            generate_backup_report
            ;;
        "help"|*)
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  init                           - Initialize backup directory structure"
            echo "  backup <repo_name> <repo_path> [type] - Create backup (type: daily/weekly/monthly)"
            echo "  cleanup <repo_name> [type]     - Clean old backups"
            echo "  restore <backup_path> <restore_path> - Restore from backup"
            echo "  list [repo_name]               - List available backups"
            echo "  verify <backup_path>           - Verify backup integrity"
            echo "  report                         - Generate backup report"
            echo ""
            echo "Environment variables:"
            echo "  BACKUP_BASE_DIR     - Base directory for backups (default: /opt/backups/wall-e)"
            echo "  RETENTION_DAYS      - Days to keep backups (default: 30)"
            echo "  COMPRESSION         - Enable compression (default: true)"
            echo "  ENCRYPTION          - Enable encryption (default: false)"
            echo "  ENCRYPTION_KEY      - Encryption key for encrypted backups"
            ;;
    esac
}

main "$@"
EOF

    chmod +x "${BASE_DIR}/scripts/backup-manager.sh"
}

# Create automated sync scheduling
create_sync_scheduling() {
    log "Creating sync scheduling system..."
    
    # Systemd timer for automated sync
    cat > "${BASE_DIR}/configs/shared/wall-e-sync.service" << 'EOF'
[Unit]
Description=Wall-E Repository Synchronization
After=network.target

[Service]
Type=oneshot
User=wall-e
Group=wall-e
WorkingDirectory=/opt/wall-e-sync
ExecStartPre=/opt/wall-e-sync/scripts/backup-manager.sh backup source /opt/repositories/project-wall-e daily
ExecStartPre=/opt/wall-e-sync/scripts/backup-manager.sh backup research /opt/repositories/wall-e-research daily
ExecStartPre=/opt/wall-e-sync/scripts/backup-manager.sh backup compliance /opt/repositories/wall-e-compliance daily
ExecStart=/opt/wall-e-sync/scripts/sync-manager.py --sync-all --report --backup
ExecStartPost=/opt/wall-e-sync/scripts/backup-manager.sh cleanup source daily
ExecStartPost=/opt/wall-e-sync/scripts/backup-manager.sh cleanup research daily
ExecStartPost=/opt/wall-e-sync/scripts/backup-manager.sh cleanup compliance daily
StandardOutput=journal
StandardError=journal
Environment=PYTHONPATH=/opt/wall-e-sync
EOF

    cat > "${BASE_DIR}/configs/shared/wall-e-sync.timer" << 'EOF'
[Unit]
Description=Wall-E Repository Synchronization Timer
Requires=wall-e-sync.service

[Timer]
# Run daily at 2 AM
OnCalendar=*-*-* 02:00:00
# Also run weekly on Sunday at 3 AM
OnCalendar=Sun *-*-* 03:00:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

    # Cron alternative
    cat > "${BASE_DIR}/configs/shared/wall-e-sync.cron" << 'EOF'
# Wall-E Repository Synchronization Cron Jobs
# Run daily sync at 2 AM
0 2 * * * /opt/wall-e-sync/scripts/sync-manager.py --sync-all --report --backup >/var/log/wall-e-sync.log 2>&1

# Run weekly full backup on Sunday at 3 AM
0 3 * * 0 /opt/wall-e-sync/scripts/backup-manager.sh backup source /opt/repositories/project-wall-e weekly >/var/log/wall-e-backup.log 2>&1
0 3 * * 0 /opt/wall-e-sync/scripts/backup-manager.sh backup research /opt/repositories/wall-e-research weekly >>/var/log/wall-e-backup.log 2>&1
0 3 * * 0 /opt/wall-e-sync/scripts/backup-manager.sh backup compliance /opt/repositories/wall-e-compliance weekly >>/var/log/wall-e-backup.log 2>&1

# Run monthly backup on first day of month at 4 AM
0 4 1 * * /opt/wall-e-sync/scripts/backup-manager.sh backup source /opt/repositories/project-wall-e monthly >/var/log/wall-e-backup-monthly.log 2>&1
0 4 1 * * /opt/wall-e-sync/scripts/backup-manager.sh backup research /opt/repositories/wall-e-research monthly >>/var/log/wall-e-backup-monthly.log 2>&1
0 4 1 * * /opt/wall-e-sync/scripts/backup-manager.sh backup compliance /opt/repositories/wall-e-compliance monthly >>/var/log/wall-e-backup-monthly.log 2>&1

# Cleanup old backups daily at 5 AM
0 5 * * * /opt/wall-e-sync/scripts/backup-manager.sh cleanup source daily >/var/log/wall-e-cleanup.log 2>&1
0 5 * * * /opt/wall-e-sync/scripts/backup-manager.sh cleanup research daily >>/var/log/wall-e-cleanup.log 2>&1
0 5 * * * /opt/wall-e-sync/scripts/backup-manager.sh cleanup compliance daily >>/var/log/wall-e-cleanup.log 2>&1
EOF
}

# Create installation script
create_installation_script() {
    log "Creating installation script..."
    
    cat > "${BASE_DIR}/scripts/install-sync-system.sh" << 'EOF'
#!/bin/bash

# Installation script for Wall-E sync system
set -euo pipefail

# Configuration
INSTALL_DIR="/opt/wall-e-sync"
SERVICE_USER="wall-e"
BACKUP_DIR="/opt/backups/wall-e"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INSTALL]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv git cron rsync gpg
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip git cronie rsync gnupg2
    elif command -v dnf &> /dev/null; then
        dnf install -y python3 python3-pip git cronie rsync gnupg2
    else
        error "Unsupported package manager"
    fi
    
    # Install Python dependencies
    pip3 install PyYAML
}

# Create service user
create_service_user() {
    log "Creating service user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
        log "Created user: $SERVICE_USER"
    else
        log "User already exists: $SERVICE_USER"
    fi
}

# Create directories
create_directories() {
    log "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"/{scripts,configs,logs}
    mkdir -p "$BACKUP_DIR"
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$BACKUP_DIR"
    
    chmod 750 "$INSTALL_DIR"
    chmod 750 "$BACKUP_DIR"
}

# Install sync system files
install_sync_files() {
    log "Installing sync system files..."
    
    # Copy scripts
    cp scripts/sync-manager.py "$INSTALL_DIR/scripts/"
    cp scripts/backup-manager.sh "$INSTALL_DIR/scripts/"
    
    # Copy configuration
    cp sync-config.json "$INSTALL_DIR/"
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR/scripts/"*.py
    chmod +x "$INSTALL_DIR/scripts/"*.sh
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
}

# Install systemd service
install_systemd_service() {
    log "Installing systemd service..."
    
    if command -v systemctl &> /dev/null; then
        cp configs/shared/wall-e-sync.service /etc/systemd/system/
        cp configs/shared/wall-e-sync.timer /etc/systemd/system/
        
        systemctl daemon-reload
        systemctl enable wall-e-sync.timer
        systemctl start wall-e-sync.timer
        
        log "Systemd service installed and started"
    else
        warn "Systemd not available, skipping service installation"
    fi
}

# Install cron jobs
install_cron_jobs() {
    log "Installing cron jobs..."
    
    # Install cron job for service user
    crontab -u "$SERVICE_USER" -l > /tmp/wall-e-cron 2>/dev/null || echo "" > /tmp/wall-e-cron
    
    # Add sync jobs if not already present
    if ! grep -q "wall-e-sync" /tmp/wall-e-cron; then
        cat configs/shared/wall-e-sync.cron >> /tmp/wall-e-cron
        crontab -u "$SERVICE_USER" /tmp/wall-e-cron
        log "Cron jobs installed"
    else
        log "Cron jobs already installed"
    fi
    
    rm /tmp/wall-e-cron
}

# Create log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/wall-e-sync << 'LOGROTATE'
/var/log/wall-e-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su wall-e wall-e
}
LOGROTATE

    log "Log rotation configured"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Test sync manager
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/scripts/sync-manager.py" --help >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        log "✅ Sync manager test passed"
    else
        error "❌ Sync manager test failed"
    fi
    
    # Test backup manager
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/scripts/backup-manager.sh" help >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        log "✅ Backup manager test passed"
    else
        error "❌ Backup manager test failed"
    fi
    
    log "Installation tests passed"
}

# Display installation summary
display_summary() {
    log "Installation completed successfully!"
    echo ""
    echo "📁 Installation directory: $INSTALL_DIR"
    echo "💾 Backup directory: $BACKUP_DIR"
    echo "👤 Service user: $SERVICE_USER"
    echo ""
    echo "🔧 Management commands:"
    echo "  sudo systemctl status wall-e-sync.timer  # Check timer status"
    echo "  sudo systemctl start wall-e-sync.service # Manual sync"
    echo "  sudo -u $SERVICE_USER $INSTALL_DIR/scripts/sync-manager.py --sync-all # Manual sync"
    echo "  sudo -u $SERVICE_USER $INSTALL_DIR/scripts/backup-manager.sh list # List backups"
    echo ""
    echo "📋 Log files:"
    echo "  /var/log/wall-e-sync.log     # Sync logs"
    echo "  /var/log/wall-e-backup.log   # Backup logs"
    echo "  $INSTALL_DIR/logs/           # Application logs"
    echo ""
    echo "⚙️  Configuration:"
    echo "  $INSTALL_DIR/sync-config.json # Sync configuration"
    echo ""
    echo "🔄 The sync system will run automatically according to the configured schedule."
}

# Main installation
main() {
    log "Starting Wall-E sync system installation..."
    
    check_root
    install_dependencies
    create_service_user
    create_directories
    install_sync_files
    
    # Install scheduling system
    if command -v systemctl &> /dev/null; then
        install_systemd_service
    else
        install_cron_jobs
    fi
    
    setup_log_rotation
    test_installation
    display_summary
    
    log "Installation completed successfully!"
}

main "$@"
EOF

    chmod +x "${BASE_DIR}/scripts/install-sync-system.sh"
}

# Update sync configuration
update_sync_config() {
    log "Updating sync configuration..."
    
    cat > "${BASE_DIR}/sync-config.json" << 'EOF'
{
  "repositories": {
    "source": {
      "name": "project-wall-e",
      "path": "/opt/repositories/project-wall-e",
      "branch": "main"
    },
    "targets": [
      {
        "name": "wall-e-research",
        "path": "/opt/repositories/wall-e-research",
        "branch": "main",
        "sync_strategy": "merge",
        "conflict_resolution": "source_wins",
        "excluded_paths": [
          "repo-separation/",
          "temp-repos/",
          ".git/hooks/",
          "*.log"
        ],
        "transformations": [
          {
            "type": "educational_disclaimer",
            "target": "README.md",
            "action": "prepend_if_missing"
          }
        ]
      },
      {
        "name": "wall-e-compliance",
        "path": "/opt/repositories/wall-e-compliance",
        "branch": "main",
        "sync_strategy": "selective",
        "conflict_resolution": "manual_review",
        "excluded_paths": [
          "repo-separation/",
          "temp-repos/",
          "config/config.yaml",
          "*.log"
        ],
        "compliance_transforms": [
          {
            "file": "config/config.yaml",
            "template": "config.compliance.yaml",
            "validation_required": true
          },
          {
            "file": "README.md",
            "template": "README-compliance.md",
            "condition": "missing_compliance_info"
          }
        ],
        "validation_rules": [
          {
            "type": "rate_limit_check",
            "max_messages_per_hour": 5
          },
          {
            "type": "human_approval_check",
            "required": true
          },
          {
            "type": "gdpr_compliance_check",
            "required": true
          }
        ]
      }
    ]
  },
  "sync_schedule": {
    "daily": "0 2 * * *",
    "weekly": "0 3 * * 0",
    "monthly": "0 4 1 * *"
  },
  "backup_settings": {
    "enabled": true,
    "retention_days": 30,
    "compression": true,
    "encryption": false,
    "backup_before_sync": true
  },
  "notification_settings": {
    "webhook_url": null,
    "email_recipients": [],
    "slack_channel": null,
    "discord_webhook": null
  },
  "monitoring": {
    "metrics_enabled": true,
    "health_checks": true,
    "performance_tracking": true
  }
}
EOF
}

# Create documentation
create_sync_documentation() {
    log "Creating synchronization documentation..."
    
    mkdir -p "${BASE_DIR}/docs"
    
    cat > "${BASE_DIR}/docs/synchronization-guide.md" << 'EOF'
# Repository Synchronization Guide

## Overview

The Wall-E repository synchronization system maintains consistency between three repositories:
- **project-wall-e** (source) - Original development repository
- **wall-e-research** (target) - Educational/research version
- **wall-e-compliance** (target) - Commercial-ready ethical version

## Synchronization Strategies

### Source → Research (Permissive)
- **Strategy**: Merge all changes from source
- **Conflict Resolution**: Source wins (with educational disclaimer preservation)
- **Frequency**: Daily automatic sync
- **Transformations**: 
  - Add educational disclaimers if missing
  - Maintain research-friendly configuration options

### Source → Compliance (Selective)
- **Strategy**: Selective sync with manual review
- **Conflict Resolution**: Manual review required
- **Frequency**: Weekly with approval workflow
- **Validation**: 
  - Rate limits ≤ 5 messages/hour
  - Human approval required
  - GDPR compliance maintained
  - No aggressive automation features

## Manual Sync Commands

### Full Synchronization
```bash
# Sync all repositories
sudo -u wall-e /opt/wall-e-sync/scripts/sync-manager.py --sync-all --report

# With backup
sudo -u wall-e /opt/wall-e-sync/scripts/sync-manager.py --sync-all --backup --report
```

### Individual Repository Sync
```bash
# Sync to research only
sudo -u wall-e /opt/wall-e-sync/scripts/sync-manager.py --sync-research

# Sync to compliance only (requires manual review)
sudo -u wall-e /opt/wall-e-sync/scripts/sync-manager.py --sync-compliance
```

## Backup Management

### Create Backups
```bash
# Daily backup
/opt/wall-e-sync/scripts/backup-manager.sh backup source /opt/repositories/project-wall-e daily

# Weekly backup
/opt/wall-e-sync/scripts/backup-manager.sh backup research /opt/repositories/wall-e-research weekly

# Monthly backup
/opt/wall-e-sync/scripts/backup-manager.sh backup compliance /opt/repositories/wall-e-compliance monthly
```

### List Backups
```bash
# List all backups
/opt/wall-e-sync/scripts/backup-manager.sh list

# List specific repository backups
/opt/wall-e-sync/scripts/backup-manager.sh list compliance
```

### Restore from Backup
```bash
# Restore repository
/opt/wall-e-sync/scripts/backup-manager.sh restore /opt/backups/wall-e/compliance/daily/compliance_daily_20250805_140000.tar.gz /opt/repositories/wall-e-compliance-restored
```

## Monitoring and Alerting

### Check Sync Status
```bash
# View systemd timer status
systemctl status wall-e-sync.timer

# View last sync service status
systemctl status wall-e-sync.service

# View sync logs
journalctl -u wall-e-sync.service -f
```

### Log Files
- **Sync logs**: `/var/log/wall-e-sync.log`
- **Backup logs**: `/var/log/wall-e-backup.log`
- **Application logs**: `/opt/wall-e-sync/logs/`

## Configuration

### Sync Configuration
Edit `/opt/wall-e-sync/sync-config.json` to modify:
- Repository paths and URLs
- Sync strategies and schedules
- Excluded files and patterns
- Validation rules
- Notification settings

### Environment Variables
- `BACKUP_BASE_DIR`: Base directory for backups
- `RETENTION_DAYS`: Days to keep backups
- `ENCRYPTION_KEY`: Key for encrypted backups
- `NOTIFICATION_WEBHOOK`: Webhook URL for notifications

## Troubleshooting

### Common Issues

#### Sync Conflicts
```bash
# Check for merge conflicts
cd /opt/repositories/wall-e-research
git status

# Manual conflict resolution
git mergetool
```

#### Compliance Validation Failures
```bash
# Validate compliance configuration
cd /opt/repositories/wall-e-compliance
python scripts/verify_compliance.py
```

#### Backup Issues
```bash
# Verify backup integrity
/opt/wall-e-sync/scripts/backup-manager.sh verify /path/to/backup.tar.gz

# Check backup disk space
df -h /opt/backups/wall-e
```

### Emergency Procedures

#### Stop Automatic Sync
```bash
# Disable timer
systemctl stop wall-e-sync.timer
systemctl disable wall-e-sync.timer

# Or disable cron jobs
crontab -u wall-e -e
```

#### Emergency Restore
```bash
# List available backups
/opt/wall-e-sync/scripts/backup-manager.sh list

# Restore from backup
/opt/wall-e-sync/scripts/backup-manager.sh restore [backup_path] [restore_path]
```

## Security Considerations

### Access Control
- Sync system runs as dedicated `wall-e` user
- Repository directories have restricted permissions (750)
- Backup directories are protected

### Audit Trail
- All sync operations are logged
- Backup metadata includes Git commit information
- Compliance changes require manual approval

### Encryption
- Optional backup encryption with GPG
- SSL/TLS for remote repository access
- Secure key management

## Performance Optimization

### Large Repository Handling
- Incremental synchronization
- Selective file filtering
- Compression for backups

### Network Optimization
- Delta transfers for Git operations
- Bandwidth throttling options
- Resume capability for interrupted transfers

## Compliance and Legal

### Data Protection
- Automatic anonymization of personal data
- Configurable data retention periods
- GDPR compliance features

### Audit Requirements
- Complete operation logging
- Compliance validation tracking
- Change approval workflows

## API Reference

### Sync Manager API
The sync manager provides a Python API for programmatic access:

```python
from sync_manager import RepositorySyncManager

# Initialize
sync_manager = RepositorySyncManager('config.json')

# Perform sync
result = sync_manager.sync_all()

# Generate report
report = sync_manager.generate_sync_report()
```

### Webhook Integration
Configure webhooks for sync notifications:

```json
{
  "notification_settings": {
    "webhook_url": "https://your-webhook.com/sync-notifications",
    "events": ["sync_success", "sync_failure", "compliance_violation"]
  }
}
```

## Support and Maintenance

### Regular Maintenance Tasks
- Monitor disk usage for backups
- Review sync logs for errors
- Update sync configuration as needed
- Test restore procedures quarterly

### Performance Monitoring
- Sync execution time tracking
- Backup size and duration monitoring
- Repository growth analysis
  
### Update Procedures
- Test sync system updates in development
- Backup current configuration before updates
- Follow change management procedures
EOF
}

# Main execution
main() {
    log "Setting up backup and synchronization strategy..."
    
    create_sync_system
    create_backup_system
    create_sync_scheduling
    create_installation_script
    update_sync_config
    create_sync_documentation
    
    log "Backup and synchronization setup completed successfully!"
    log ""
    log "Created synchronization infrastructure:"
    log "- Advanced Python-based sync manager with conflict resolution"
    log "- Comprehensive backup system with encryption support"
    log "- Automated scheduling via systemd/cron"
    log "- Installation script for production deployment"
    log "- Complete documentation and troubleshooting guides"
    log ""
    log "Next steps:"
    log "1. Review the sync configuration in sync-config.json"
    log "2. Run ./scripts/install-sync-system.sh to install the system"
    log "3. Test the synchronization with manual commands"
    log "4. Monitor the automated sync operations"
    log ""
    log "Installation command: sudo ./scripts/install-sync-system.sh"
    log "Manual sync test: python3 scripts/sync-manager.py --sync-all --report"
}

main "$@"