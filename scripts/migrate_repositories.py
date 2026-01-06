#!/usr/bin/env python3
"""
Repository Migration Script for Wall-E Project
Helps separate the project into research and compliance repositories
"""

import os
import shutil
import yaml
import argparse
from pathlib import Path
from typing import Dict, List
import logging

# Import configuration system for path management
try:
    from src.enhanced_config_loader import ConfigPaths

    CONFIG_PATHS_AVAILABLE = True
except ImportError:
    CONFIG_PATHS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepositoryMigrator:
    """Handles migration of Wall-E project to separate repositories"""

    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)

        # Initialize configuration paths (no more hardcoding)
        if CONFIG_PATHS_AVAILABLE:
            self.config_paths = ConfigPaths()
            self.migration_paths = self.config_paths.migration_paths
        else:
            # Fallback to hardcoded values if config system unavailable
            logger.warning("Configuration system unavailable, using fallback paths")
            self.migration_paths = {
                "base_config_rel": "config/base_config.yaml",
                "config_loader_rel": "src/config_loader.py",
                "requirements_rel": "requirements.txt",
                "src_dir": "src",
                "scripts_dir": "scripts",
                "config_dir": "config",
                "environments_dir": "config/environments",
                "data_dir": "data",
                "logs_dir": "logs",
                "backups_dir": "backups",
            }

        self.validate_source_directory()

    def validate_source_directory(self):
        """Validate that source directory contains Wall-E project"""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")

        required_files = [
            self.migration_paths["base_config_rel"],
            self.migration_paths["config_loader_rel"],
            self.migration_paths["requirements_rel"],
        ]

        for file_path in required_files:
            full_path = self.source_dir / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"Required file not found: {full_path}")

    def create_base_repository(self, target_dir: str, repo_name: str) -> Path:
        """Create base repository structure"""
        target_path = Path(target_dir)

        if target_path.exists():
            logger.warning(f"Target directory exists: {target_path}")
            response = input("Remove existing directory? (y/N): ")
            if response.lower() == "y":
                shutil.rmtree(target_path)
            else:
                raise FileExistsError(f"Target directory exists: {target_path}")

        # Copy entire source directory
        logger.info(f"Copying source directory to {target_path}")
        shutil.copytree(self.source_dir, target_path)

        # Update repository-specific files
        self._update_repository_metadata(target_path, repo_name)

        return target_path

    def _update_repository_metadata(self, repo_path: Path, repo_name: str):
        """Update repository metadata files"""

        # Update README if it exists
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            content = content.replace("project-wall-e", repo_name)
            content = content.replace(
                "Wall-E", f"Wall-E {repo_name.split('-')[-1].title()}"
            )
            readme_path.write_text(content)

        # Update pyproject.toml if it exists
        pyproject_path = repo_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            content = content.replace("project-wall-e", repo_name)
            pyproject_path.write_text(content)

    def create_research_repository(self, target_dir: str) -> Path:
        """Create research-specific repository"""
        repo_path = self.create_base_repository(target_dir, "wall-e-research")

        logger.info("Configuring research repository...")

        # Create research-specific default config
        self._create_default_config(repo_path, "research")

        # Add research disclaimers
        self._add_research_disclaimers(repo_path)

        # Update documentation
        self._update_research_documentation(repo_path)

        # Create research-specific scripts
        self._create_research_scripts(repo_path)

        logger.info(f"Research repository created at: {repo_path}")
        return repo_path

    def create_compliance_repository(self, target_dir: str) -> Path:
        """Create compliance-specific repository"""
        repo_path = self.create_base_repository(target_dir, "wall-e-compliance")

        logger.info("Configuring compliance repository...")

        # Create compliance-specific default config
        self._create_default_config(repo_path, "compliance")

        # Remove aggressive anti-detection features
        self._sanitize_anti_detection_code(repo_path)

        # Add compliance features
        self._add_compliance_features(repo_path)

        # Update documentation
        self._update_compliance_documentation(repo_path)

        # Create compliance-specific scripts
        self._create_compliance_scripts(repo_path)

        logger.info(f"Compliance repository created at: {repo_path}")
        return repo_path

    def _create_default_config(self, repo_path: Path, mode: str):
        """Create default configuration file for the repository"""
        config_dir = repo_path / "config"

        # Create default config.yaml that loads the appropriate mode (configuration-driven paths)
        default_config = {
            "_mode": mode,
            "_loader_config": {
                "base_config": self.migration_paths["base_config_rel"],
                f"{mode}_overrides": f"{self.migration_paths['config_dir']}/{mode}_overrides.yaml",
                "environment_override_dir": self.migration_paths["environments_dir"],
            },
            "default_settings": {"mode": mode, "environment": "development"},
        }

        config_path = config_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created default config for {mode} mode")

    def _add_research_disclaimers(self, repo_path: Path):
        """Add research-specific disclaimers and warnings"""

        # Create research disclaimer file
        disclaimer_content = """# RESEARCH DISCLAIMER

## ⚠️ IMPORTANT NOTICE

This version of Wall-E is designed for **RESEARCH AND EDUCATIONAL PURPOSES ONLY**.

### Legal Warnings:
- This software may violate terms of service of target platforms
- Users assume all legal risks and responsibilities
- Not intended for commercial use
- May result in account bans or legal action

### Ethical Considerations:
- Aggressive automation may impact platform stability
- High rate limits may affect other users
- Use responsibly and consider impact on others

### Recommendations:
- Use only on test accounts
- Monitor for platform policy changes
- Consider ethical implications of automation
- Respect platform rate limits and ToS when possible

### Academic Use:
- Suitable for studying automation techniques
- Useful for research on marketplace dynamics
- Can be used for educational demonstrations
- Appropriate for technical skill development

**By using this software, you acknowledge and accept all risks and responsibilities.**
"""

        disclaimer_path = repo_path / "RESEARCH_DISCLAIMER.md"
        disclaimer_path.write_text(disclaimer_content)

        # Update main README with disclaimer
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            disclaimer_notice = "\n\n## ⚠️ RESEARCH VERSION DISCLAIMER\n\n**This is the research version of Wall-E. See [RESEARCH_DISCLAIMER.md](RESEARCH_DISCLAIMER.md) for important legal and ethical considerations.**\n\n"

            # Insert disclaimer after first heading
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# ") and i > 0:
                    lines.insert(i + 1, disclaimer_notice)
                    break

            readme_path.write_text("\n".join(lines))

    def _sanitize_anti_detection_code(self, repo_path: Path):
        """Remove or modify aggressive anti-detection features for compliance"""

        anti_detection_file = (
            repo_path / f"{self.migration_paths['src_dir']}/scraper/anti_detection.py"
        )
        if anti_detection_file.exists():
            logger.info("Sanitizing anti-detection code for compliance...")

            # Read current content
            content = anti_detection_file.read_text()

            # Add compliance warning at the top
            compliance_warning = '''"""
COMPLIANCE MODE: Anti-detection features are disabled for ethical compliance.
This module provides basic browser configuration without evasion techniques.
"""

# COMPLIANCE NOTE: Aggressive anti-detection features have been disabled
# for ethical and legal compliance. Only basic browser configuration remains.

'''

            # Replace aggressive anti-detection with compliance notice
            sanitized_content = compliance_warning + "\n" + content

            # Comment out aggressive functions (simple approach)
            lines = sanitized_content.split("\n")
            sanitized_lines = []

            for line in lines:
                # Comment out specific aggressive functions
                if any(
                    keyword in line.lower()
                    for keyword in [
                        "webdriver_detection_bypass",
                        "automation_markers_hiding",
                        "stealth_mode",
                        "fingerprint_randomization",
                    ]
                ):
                    sanitized_lines.append(f"    # COMPLIANCE: Disabled - {line}")
                else:
                    sanitized_lines.append(line)

            anti_detection_file.write_text("\n".join(sanitized_lines))

    def _add_compliance_features(self, repo_path: Path):
        """Add compliance-specific features"""

        # Create consent management module
        compliance_dir = repo_path / f"{self.migration_paths['src_dir']}/compliance"
        compliance_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (compliance_dir / "__init__.py").write_text(
            '"""Compliance and legal modules"""'
        )

        # Create consent management system
        consent_manager_content = '''"""
Consent Management System for GDPR Compliance
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class ConsentManager:
    """Manages user consent for GDPR compliance"""
    
    def __init__(self, consent_file: str = "data/consent_records.json"):
        self.consent_file = Path(consent_file)
        self.consent_file.parent.mkdir(exist_ok=True)
        self.consents = self._load_consents()
    
    def _load_consents(self) -> Dict:
        """Load consent records from file"""
        if self.consent_file.exists():
            with open(self.consent_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_consents(self):
        """Save consent records to file"""
        with open(self.consent_file, 'w') as f:
            json.dump(self.consents, f, indent=2, default=str)
    
    def collect_consent(self, user_id: str, consent_types: List[str]) -> bool:
        """Collect consent from user"""
        print(f"\\n=== CONSENT REQUEST ===")
        print(f"User ID: {user_id}")
        print(f"We need your consent for the following data processing activities:")
        
        for consent_type in consent_types:
            print(f"  - {consent_type}")
        
        response = input("\\nDo you consent to this data processing? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            self.consents[user_id] = {
                'consent_given': True,
                'consent_types': consent_types,
                'timestamp': datetime.now(),
                'ip_address': 'localhost',  # In real implementation, get actual IP
                'user_agent': 'Wall-E Compliance Bot'
            }
            self._save_consents()
            print("✅ Consent recorded. Thank you!")
            return True
        else:
            print("❌ Consent denied. Cannot process your data.")
            return False
    
    def has_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given specific consent"""
        user_consent = self.consents.get(user_id, {})
        if not user_consent.get('consent_given', False):
            return False
        
        return consent_type in user_consent.get('consent_types', [])
    
    def withdraw_consent(self, user_id: str) -> bool:
        """Allow user to withdraw consent"""
        if user_id in self.consents:
            self.consents[user_id]['consent_given'] = False
            self.consents[user_id]['withdrawal_timestamp'] = datetime.now()
            self._save_consents()
            print(f"✅ Consent withdrawn for user {user_id}")
            return True
        return False
'''

        consent_file = compliance_dir / "consent_manager.py"
        consent_file.write_text(consent_manager_content)

        # Create human oversight module
        oversight_content = '''"""
Human Oversight System for Compliance
"""

from typing import Optional


class HumanOversight:
    """Provides human oversight for automated actions"""
    
    def __init__(self):
        self.enabled = True
    
    def request_approval(self, action: str, context: Dict) -> bool:
        """Request human approval for an action"""
        if not self.enabled:
            return True
        
        print(f"\\n=== HUMAN APPROVAL REQUIRED ===")
        print(f"Action: {action}")
        print(f"Context: {context}")
        
        while True:
            response = input("\\nApprove this action? (yes/no/details): ").lower()
            
            if response in ['yes', 'y']:
                print("✅ Action approved")
                return True
            elif response in ['no', 'n']:
                print("❌ Action denied")
                return False
            elif response == 'details':
                self._show_action_details(action, context)
            else:
                print("Please enter 'yes', 'no', or 'details'")
    
    def _show_action_details(self, action: str, context: Dict):
        """Show detailed information about the requested action"""
        print(f"\\n=== ACTION DETAILS ===")
        print(f"Action Type: {action}")
        for key, value in context.items():
            print(f"{key}: {value}")
        print("=" * 25)
'''

        oversight_file = compliance_dir / "human_oversight.py"
        oversight_file.write_text(oversight_content)

    def _update_research_documentation(self, repo_path: Path):
        """Update documentation for research repository"""
        docs_dir = repo_path / "docs"

        # Create research-specific setup guide
        research_setup = """# Research Setup Guide

## Quick Start for Researchers

This research version includes advanced features for studying marketplace automation:

### Installation
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
playwright install chromium
```

### Configuration
```bash
# Copy and modify research configuration
cp config/research_overrides.yaml config/local.yaml
# Edit config/local.yaml with your research parameters
```

### Research Features
- Advanced price analysis with ML predictions
- Conversation pattern analysis
- A/B testing framework
- Detailed performance metrics
- Data export for academic use

### Ethical Research Guidelines
1. Use only test accounts
2. Monitor platform impact
3. Respect rate limits when possible
4. Document research methodology
5. Share findings responsibly

### Data Collection
The research version collects comprehensive data for analysis:
- Conversation patterns and success rates
- Price prediction accuracy
- User behavior patterns
- Platform response times
- Market trend analysis

All data is stored locally and can be exported for academic research.
"""

        research_setup_file = docs_dir / "research-setup.md"
        research_setup_file.write_text(research_setup)

    def _update_compliance_documentation(self, repo_path: Path):
        """Update documentation for compliance repository"""
        docs_dir = repo_path / "docs"

        # Create compliance setup guide
        compliance_setup = """# Compliance Setup Guide

## Legal and Ethical Operation

This compliance version is designed for commercial use with full legal compliance:

### Legal Requirements Checklist
- [ ] Legal review completed
- [ ] Privacy policy created
- [ ] Terms of service updated
- [ ] GDPR compliance verified
- [ ] Data protection impact assessment
- [ ] Consent management system tested

### Installation
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
playwright install chromium
```

### Compliance Configuration
```bash
# Use compliance configuration
cp config/compliance_overrides.yaml config/local.yaml
# Verify compliance settings are correct
python src/config_loader.py --validate --mode compliance
```

### Mandatory Features
- **Consent Collection**: Users must explicitly consent to data processing
- **Human Oversight**: Critical actions require human approval
- **Transparency**: All automation is clearly disclosed
- **Data Minimization**: Only necessary data is collected
- **Right to be Forgotten**: Users can request data deletion

### Operating Guidelines
1. **Rate Limits**: Maximum 5 messages per hour
2. **Transparency**: Always disclose automation to users
3. **Consent**: Collect explicit consent before data processing
4. **Human Oversight**: Escalate complex situations to humans
5. **Data Protection**: Encrypt all personal data

### Monitoring and Auditing
The system includes comprehensive monitoring:
- Consent collection rates
- Rate limit adherence
- Data retention compliance
- User satisfaction metrics
- Legal compliance alerts

### Support and Legal
For legal questions or compliance issues:
- Consult with legal counsel
- Review GDPR guidelines
- Check platform terms of service
- Monitor regulatory changes
"""

        compliance_setup_file = docs_dir / "compliance-setup.md"
        compliance_setup_file.write_text(compliance_setup)

    def _create_research_scripts(self, repo_path: Path):
        """Create research-specific scripts"""
        scripts_dir = repo_path / self.migration_paths["scripts_dir"]

        # Research launcher script
        research_launcher = '''#!/usr/bin/env python3
"""
Research Version Launcher
Starts Wall-E in research mode with appropriate warnings
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_loader import load_config, ConfigMode


def show_research_disclaimer():
    """Show research disclaimer and get user acknowledgment"""
    print("=" * 60)
    print("           WALL-E RESEARCH VERSION")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This is the research version of Wall-E")
    print("    - Designed for educational and research purposes only")
    print("    - May violate platform terms of service")
    print("    - User assumes all legal risks")
    print("    - Not suitable for commercial use")
    print()
    
    response = input("Do you acknowledge these risks? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Exiting...")
        sys.exit(1)
    
    print()
    print("Starting Wall-E Research Mode...")
    print("=" * 60)


def main():
    show_research_disclaimer()
    
    # Load research configuration
    config = load_config(ConfigMode.RESEARCH)
    
    # Start the bot (placeholder - implement actual bot start)
    print(f"Configuration loaded: {config['app']['name']}")
    print(f"Mode: {config['app']['mode']}")
    print(f"Max messages/hour: {config['wallapop']['behavior']['max_messages_per_hour']}")
    
    # Start the actual bot with research configuration
    try:
        from bot.wallapop_bot import WallapopBot
        bot = WallapopBot(config)
        print("Starting Wall-E Research Bot...")
        # bot.run()  # Uncomment when ready to run
        print("Bot initialization completed (start manually with bot.run())")
    except ImportError:
        print("Bot module not available - configuration loaded successfully")
    except Exception as e:
        print(f"Bot initialization error: {e}")


if __name__ == "__main__":
    main()
'''

        launcher_file = scripts_dir / "start_research_mode.py"
        launcher_file.write_text(research_launcher)
        launcher_file.chmod(0o755)

    def _create_compliance_scripts(self, repo_path: Path):
        """Create compliance-specific scripts"""
        scripts_dir = repo_path / self.migration_paths["scripts_dir"]

        # Compliance launcher script
        compliance_launcher = '''#!/usr/bin/env python3
"""
Compliance Version Launcher
Starts Wall-E in compliance mode with legal safeguards
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_loader import load_config, ConfigMode


def verify_compliance_setup():
    """Verify compliance setup is correct"""
    print("=" * 60)
    print("         WALL-E COMPLIANCE VERSION")
    print("=" * 60)
    print()
    print("✅ Verifying compliance setup...")
    
    # Load and validate compliance configuration
    try:
        config = load_config(ConfigMode.COMPLIANCE)
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check critical compliance settings
    checks = [
        ("Rate limiting", config['wallapop']['behavior']['max_messages_per_hour'] <= 5),
        ("Anti-detection disabled", not config['anti_detection']['enabled']),
        ("GDPR compliance", config['security']['gdpr_compliance']['enabled']),
        ("Human oversight", config['human_oversight']['enabled']),
        ("Consent management", config['consent_management']['enabled'])
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        print()
        print("❌ Compliance checks failed. Please review configuration.")
        sys.exit(1)
    
    print()
    print("✅ All compliance checks passed")
    print("✅ Ready to start in compliance mode")
    
    return config


def main():
    config = verify_compliance_setup()
    
    print()
    print("Starting Wall-E Compliance Mode...")
    print(f"- Mode: {config['app']['mode']}")
    print(f"- Max messages/hour: {config['wallapop']['behavior']['max_messages_per_hour']}")
    print(f"- Human oversight: {'Enabled' if config['human_oversight']['enabled'] else 'Disabled'}")
    print("=" * 60)
    
    # Start the actual bot with compliance features
    try:
        from bot.wallapop_bot import WallapopBot
        from compliance.consent_manager import ConsentManager
        from compliance.human_oversight import HumanOversight
        
        # Initialize compliance components
        consent_manager = ConsentManager()
        human_oversight = HumanOversight()
        
        bot = WallapopBot(config, consent_manager=consent_manager, oversight=human_oversight)
        print("Starting Wall-E Compliance Bot with legal safeguards...")
        # bot.run()  # Uncomment when ready to run
        print("Compliance bot initialization completed (start manually with bot.run())")
    except ImportError:
        print("Bot or compliance modules not available - configuration loaded successfully")
    except Exception as e:
        print(f"Compliance bot initialization error: {e}")


if __name__ == "__main__":
    main()
'''

        launcher_file = scripts_dir / "start_compliance_mode.py"
        launcher_file.write_text(compliance_launcher)
        launcher_file.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Wall-E to separate repositories"
    )
    parser.add_argument(
        "--source", default=".", help="Source directory (current project)"
    )
    parser.add_argument(
        "--research-target", help="Target directory for research repository"
    )
    parser.add_argument(
        "--compliance-target", help="Target directory for compliance repository"
    )

    args = parser.parse_args()

    if not args.research_target and not args.compliance_target:
        print(
            "Please specify at least one target directory (--research-target or --compliance-target)"
        )
        sys.exit(1)

    migrator = RepositoryMigrator(args.source)

    if args.research_target:
        research_repo = migrator.create_research_repository(args.research_target)
        print(f"✅ Research repository created: {research_repo}")

    if args.compliance_target:
        compliance_repo = migrator.create_compliance_repository(args.compliance_target)
        print(f"✅ Compliance repository created: {compliance_repo}")

    print("\n🎉 Repository migration completed!")
    print("\nNext steps:")
    print("1. Review generated configurations")
    print("2. Test both repositories")
    print("3. Legal review of compliance version")
    print("4. Update documentation")
    print("5. Set up separate git repositories")


if __name__ == "__main__":
    main()
