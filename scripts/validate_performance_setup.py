#!/usr/bin/env python3
"""
Performance Setup Validator for Wall-E AI Engine
Validates that all performance optimizations are properly installed and configured
"""

import sys
import os
import importlib
import platform
import subprocess
from typing import List, Dict, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def check_python_packages() -> Tuple[bool, List[str]]:
    """Check if required Python packages are installed"""
    
    required_packages = [
        'psutil',
        'redis', 
        'ollama',
        'asyncio',
        'threading',
        'concurrent.futures',
        'dataclasses',
        'weakref',
        'gc',
        'statistics'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages


def check_ai_engine_modules() -> Tuple[bool, List[str]]:
    """Check if AI Engine performance modules are available"""
    
    modules = [
        'ai_engine.config',
        'ai_engine.llm_manager', 
        'ai_engine.performance_monitor',
        'ai_engine.ai_engine',
        'ai_engine.response_generator',
        'ai_engine.performance_tests'
    ]
    
    missing_modules = []
    
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            missing_modules.append(f"{module}: {str(e)}")
    
    return len(missing_modules) == 0, missing_modules


def check_system_resources() -> Dict[str, any]:
    """Check system resources and capabilities"""
    
    try:
        import psutil
        
        # Get system info
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_cores': cpu_count,
            'total_ram_gb': memory.total / (1024**3),
            'available_ram_gb': memory.available / (1024**3),
            'disk_free_gb': disk.free / (1024**3),
            'platform': platform.platform(),
            'python_version': platform.python_version()
        }
    except Exception as e:
        return {'error': str(e)}


def check_ollama_availability() -> Tuple[bool, str]:
    """Check if Ollama is available"""
    
    try:
        # Try to import ollama client
        import ollama
        
        # Try to connect to Ollama server
        try:
            client = ollama.Client()
            models = client.list()
            return True, f"Ollama available with {len(models.get('models', []))} models"
        except Exception as e:
            return False, f"Ollama client available but server not accessible: {str(e)}"
    
    except ImportError:
        return False, "Ollama client not installed"


def check_redis_availability() -> Tuple[bool, str]:
    """Check if Redis is available"""
    
    try:
        import redis
        
        # Try to connect to Redis
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            info = r.info()
            return True, f"Redis available (version {info.get('redis_version', 'unknown')})"
        except Exception as e:
            return False, f"Redis client available but server not accessible: {str(e)}"
    
    except ImportError:
        return False, "Redis client not installed"


def test_ai_engine_basic() -> Tuple[bool, str]:
    """Test basic AI Engine functionality"""
    
    try:
        from ai_engine.config import AIEngineConfig
        from ai_engine.performance_monitor import initialize_performance_monitor
        
        # Test configuration
        config = AIEngineConfig.for_research()
        system_info = config.get_system_info()
        warnings = config.validate_config()
        
        # Test performance monitor initialization
        monitor = initialize_performance_monitor(config)
        health = monitor.get_health_status()
        
        return True, f"AI Engine basic test passed (health: {health['status']})"
        
    except Exception as e:
        return False, f"AI Engine basic test failed: {str(e)}"


def print_status(check_name: str, success: bool, message: str, details: List[str] = None):
    """Print formatted status message"""
    
    status = "✅" if success else "❌"
    print(f"{status} {check_name}: {message}")
    
    if details:
        for detail in details:
            print(f"   - {detail}")


def main():
    """Main validation function"""
    
    print("🔧 Wall-E AI Engine Performance Setup Validator")
    print("=" * 60)
    print()
    
    # Check Python packages
    packages_ok, missing_packages = check_python_packages()
    print_status(
        "Python Packages", 
        packages_ok,
        "All required packages installed" if packages_ok else f"Missing {len(missing_packages)} packages",
        missing_packages if not packages_ok else None
    )
    
    # Check AI Engine modules
    modules_ok, missing_modules = check_ai_engine_modules()
    print_status(
        "AI Engine Modules",
        modules_ok,
        "All modules available" if modules_ok else f"Missing {len(missing_modules)} modules",
        missing_modules if not modules_ok else None
    )
    
    # Check system resources
    system_info = check_system_resources()
    if 'error' not in system_info:
        meets_requirements = (
            system_info['cpu_cores'] >= 4 and
            system_info['total_ram_gb'] >= 8 and
            system_info['disk_free_gb'] >= 10
        )
        
        print_status(
            "System Resources",
            meets_requirements,
            "System meets minimum requirements" if meets_requirements else "System below minimum requirements",
            [
                f"CPU Cores: {system_info['cpu_cores']} (min: 4)",
                f"Total RAM: {system_info['total_ram_gb']:.1f} GB (min: 8 GB)",
                f"Available RAM: {system_info['available_ram_gb']:.1f} GB",
                f"Free Disk: {system_info['disk_free_gb']:.1f} GB (min: 10 GB)",
                f"Platform: {system_info['platform']}",
                f"Python: {system_info['python_version']}"
            ]
        )
    else:
        print_status("System Resources", False, f"Error checking system: {system_info['error']}")
    
    # Check Ollama
    ollama_ok, ollama_msg = check_ollama_availability()
    print_status("Ollama Server", ollama_ok, ollama_msg)
    
    # Check Redis
    redis_ok, redis_msg = check_redis_availability()
    print_status("Redis Server", redis_ok, redis_msg)
    
    # Test AI Engine
    if modules_ok:
        engine_ok, engine_msg = test_ai_engine_basic()
        print_status("AI Engine Basic Test", engine_ok, engine_msg)
    else:
        print_status("AI Engine Basic Test", False, "Skipped due to missing modules")
    
    print()
    print("📋 SETUP SUMMARY:")
    print("-" * 30)
    
    # Overall assessment
    critical_checks = [packages_ok, modules_ok]
    optional_checks = [ollama_ok, redis_ok]
    
    if all(critical_checks):
        if all(optional_checks):
            print("🎉 SETUP COMPLETE: All performance optimizations are ready!")
            print("   You can run performance benchmarks and use all features.")
        else:
            print("⚠️  PARTIAL SETUP: Core optimizations ready, some features limited.")
            if not ollama_ok:
                print("   - Install Ollama for AI response generation")
            if not redis_ok:
                print("   - Install Redis for distributed caching")
    else:
        print("❌ SETUP INCOMPLETE: Critical components missing.")
        if not packages_ok:
            print("   - Install missing Python packages: pip install -r requirements.txt")
        if not modules_ok:
            print("   - Ensure AI Engine modules are properly installed")
    
    print()
    print("📖 NEXT STEPS:")
    print("-" * 15)
    
    if not packages_ok:
        print("1. Install missing Python packages:")
        print("   pip install -r requirements.txt")
    
    if not ollama_ok:
        print("2. Install and setup Ollama:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   ollama pull llama3.2:11b-vision-instruct-q4_0")
    
    if not redis_ok:
        print("3. Install Redis (optional for caching):")
        print("   # Ubuntu/Debian: sudo apt install redis-server")
        print("   # macOS: brew install redis")
        print("   # Or use Docker: docker run -d -p 6379:6379 redis:alpine")
    
    if all(critical_checks):
        print("4. Run performance benchmarks:")
        print("   python scripts/run_performance_benchmark.py --quick")
        print("   python scripts/run_performance_benchmark.py --full")
    
    print()
    print("📚 Documentation: docs/AI_ENGINE_PERFORMANCE_OPTIMIZATION.md")
    
    # Exit code
    if all(critical_checks):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Critical issues


if __name__ == '__main__':
    main()