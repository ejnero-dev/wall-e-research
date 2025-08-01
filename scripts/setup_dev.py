#!/usr/bin/env python3
"""
Development environment setup script for Wallapop Automation Bot.

This script helps developers set up their development environment with all
necessary dependencies, pre-commit hooks, and configurations.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🤖 Wallapop Automation Bot - Development Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent
    if not (project_root / "requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing production dependencies"),
        ("pip install -r requirements-dev.txt", "Installing development dependencies"),
        ("pre-commit install", "Installing pre-commit hooks"),
        ("python -m spacy download es_core_news_sm", "Installing spaCy Spanish model"),
        ("playwright install chromium", "Installing Playwright browser"),
        ("playwright install-deps", "Installing Playwright system dependencies"),
    ]
    
    failed_commands = []
    
    for command, description in commands:
        if not run_command(command, description):
            failed_commands.append(description)
    
    print("\n" + "=" * 50)
    
    if failed_commands:
        print("⚠️  Setup completed with some errors:")
        for failed in failed_commands:
            print(f"   - {failed}")
        print("\nPlease resolve these issues manually.")
    else:
        print("🎉 Development environment setup completed successfully!")
    
    print("\n📋 Next steps:")
    print("1. Copy config/config.example.yaml to config/config.yaml")
    print("2. Copy config/price_analyzer.example.yaml to config/price_analyzer.yaml")
    print("3. Update configuration files with your settings")
    print("4. Run 'pytest' to ensure everything is working")
    print("5. Run 'pre-commit run --all-files' to check code quality")
    
    print("\n🚀 Happy coding!")


if __name__ == "__main__":
    main()