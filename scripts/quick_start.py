#!/usr/bin/env python3
"""
Quick start script for Wallapop Bot database setup
Run this to get everything up and running quickly
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command, description, check=True):
    """Run a shell command with description"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def check_docker():
    """Check if Docker is available"""
    return run_command("docker --version", "Checking Docker installation", check=False)


def check_docker_compose():
    """Check if Docker Compose is available"""
    return run_command(
        "docker-compose --version", "Checking Docker Compose installation", check=False
    )


def main():
    """Main setup flow"""
    print("🚀 Wallapop Bot Database Quick Start")
    print("=" * 50)

    # Check prerequisites
    print("\n📋 Checking prerequisites...")

    if not check_docker():
        print("❌ Docker is required. Please install Docker first.")
        return 1

    if not check_docker_compose():
        print("❌ Docker Compose is required. Please install Docker Compose first.")
        return 1

    print("✅ All prerequisites met!")

    # Start services
    print("\n🐳 Starting Docker services...")
    if not run_command(
        "docker-compose up -d postgres redis", "Starting PostgreSQL and Redis"
    ):
        return 1

    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(10)

    # Check service health
    if not run_command("docker-compose ps", "Checking service status"):
        print("⚠️  Services may not be fully ready yet. Continuing...")

    # Test connections
    print("\n🔍 Testing database connections...")
    try:
        from src.database.config import DatabaseConfig

        config = DatabaseConfig()

        print("   Testing PostgreSQL connection...")
        connections = config.validate_connection()

        if connections["database"]:
            print("✅ PostgreSQL connection successful")
        else:
            print("❌ PostgreSQL connection failed")
            print("   Retrying in 5 seconds...")
            time.sleep(5)
            connections = config.validate_connection()
            if not connections["database"]:
                print(
                    "❌ PostgreSQL still not available. Check logs with: docker-compose logs postgres"
                )
                return 1
            print("✅ PostgreSQL connection successful on retry")

        if connections["redis"]:
            print("✅ Redis connection successful")
        else:
            print("⚠️  Redis connection failed (optional for basic functionality)")

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print(
            "   You may need to install dependencies: pip install -r requirements.txt"
        )
        return 1

    # Initialize database
    print("\n📊 Initializing database...")
    if not run_command(
        "python scripts/init_database.py --sample-data",
        "Setting up database tables and sample data",
    ):
        return 1

    # Show final status
    print("\n📈 Checking final status...")
    run_command("python scripts/db_manager.py stats", "Displaying database statistics")

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Check the database with pgAdmin: http://localhost:8080")
    print("   - Email: admin@example.local")
    print("   - Password: admin123")
    print("2. Check Redis with Redis Commander: http://localhost:8081")
    print("3. Start the bot: python -m src.bot.wallapop_bot")
    print("4. Run tests: pytest tests/")
    print("\nUseful commands:")
    print("- View services: docker-compose ps")
    print("- View logs: docker-compose logs postgres redis")
    print("- Stop services: docker-compose down")
    print("- Database stats: python scripts/db_manager.py stats")

    return 0


if __name__ == "__main__":
    sys.exit(main())
