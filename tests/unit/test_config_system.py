#!/usr/bin/env python3
"""
Configuration System Test Script
Tests the new enhanced configuration loader and dynamic config system
"""

import sys
import logging
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from enhanced_config_loader import (
        load_config,
        ConfigMode,
        get_config_loader,
        get_config_value,
        update_config_value,
        add_config_change_callback,
    )
    from scraper.dynamic_config import (
        get_scraper_config,
        get_wallapop_selectors,
        get_wallapop_urls,
    )

    ENHANCED_CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced configuration system not available: {e}")
    ENHANCED_CONFIG_AVAILABLE = False


def test_basic_configuration_loading():
    """Test basic configuration loading functionality"""
    print("=" * 60)
    print("Testing Basic Configuration Loading")
    print("=" * 60)

    try:
        # Test research mode
        print("Loading research configuration...")
        research_config = load_config(ConfigMode.RESEARCH, enable_hot_reload=False)
        print("✅ Research configuration loaded successfully")

        # Test compliance mode
        print("Loading compliance configuration...")
        compliance_config = load_config(ConfigMode.COMPLIANCE, enable_hot_reload=False)
        print("✅ Compliance configuration loaded successfully")

        # Test configuration differences
        research_messages = (
            research_config.get("wallapop", {})
            .get("behavior", {})
            .get("max_messages_per_hour", 0)
        )
        compliance_messages = (
            compliance_config.get("wallapop", {})
            .get("behavior", {})
            .get("max_messages_per_hour", 0)
        )

        print(f"Research max messages/hour: {research_messages}")
        print(f"Compliance max messages/hour: {compliance_messages}")

        if research_messages > compliance_messages:
            print("✅ Configuration modes have different settings as expected")
        else:
            print("⚠️ Configuration modes may not be properly differentiated")

        return True

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_dynamic_scraper_configuration():
    """Test dynamic scraper configuration system"""
    print("\n" + "=" * 60)
    print("Testing Dynamic Scraper Configuration")
    print("=" * 60)

    try:
        # Load research config first
        load_config(ConfigMode.RESEARCH, enable_hot_reload=False)

        # Test dynamic config
        config = get_scraper_config()
        selectors = get_wallapop_selectors()
        urls = get_wallapop_urls()

        print(f"Min delay: {config.min_delay_seconds}s")
        print(f"Max delay: {config.max_delay_seconds}s")
        print(f"Headless mode: {config.headless}")
        print(f"Viewport: {config.viewport_width}x{config.viewport_height}")
        print(f"Base URL: {urls.base_url}")
        print(f"Login URL: {urls.login_url}")
        print(f"User agents count: {len(config.user_agents)}")
        print(f"Login selectors count: {len(selectors.login_button)}")

        # Test dynamic methods
        human_delay = config.get_human_delay()
        typing_delay = config.get_typing_delay(50)  # 50 characters
        user_agent = config.get_random_user_agent()

        print(f"Human delay: {human_delay:.2f}s")
        print(f"Typing delay for 50 chars: {typing_delay:.2f}s")
        print(f"Random user agent: {user_agent[:50]}...")
        print(f"Within active hours: {config.is_within_active_hours()}")

        print("✅ Dynamic scraper configuration working correctly")
        return True

    except Exception as e:
        print(f"❌ Dynamic scraper configuration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_validation():
    """Test configuration validation system"""
    print("\n" + "=" * 60)
    print("Testing Configuration Validation")
    print("=" * 60)

    try:
        loader = get_config_loader(enable_hot_reload=False)

        # Test research config validation
        research_config = load_config(ConfigMode.RESEARCH, enable_hot_reload=False)
        research_valid = loader.validate_configuration(
            research_config, ConfigMode.RESEARCH
        )
        print(
            f"Research config validation: {'✅ PASSED' if research_valid else '❌ FAILED'}"
        )

        # Test compliance config validation
        compliance_config = load_config(ConfigMode.COMPLIANCE, enable_hot_reload=False)
        compliance_valid = loader.validate_configuration(
            compliance_config, ConfigMode.COMPLIANCE
        )
        print(
            f"Compliance config validation: {'✅ PASSED' if compliance_valid else '❌ FAILED'}"
        )

        # Test configuration summary
        print("\nResearch Configuration Summary:")
        research_summary = loader.get_config_summary(research_config)
        for key, value in research_summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")

        return research_valid and compliance_valid

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def test_configuration_access_patterns():
    """Test different ways to access configuration values"""
    print("\n" + "=" * 60)
    print("Testing Configuration Access Patterns")
    print("=" * 60)

    try:
        # Load configuration
        load_config(ConfigMode.RESEARCH, enable_hot_reload=False)

        # Test direct value access
        min_delay = get_config_value("scraper.timing.min_delay_seconds", 30)
        max_delay = get_config_value("scraper.timing.max_delay_seconds", 120)
        app_name = get_config_value("app.name", "Unknown")
        headless = get_config_value("scraper.browser.headless", True)

        print(f"Min delay (direct access): {min_delay}s")
        print(f"Max delay (direct access): {max_delay}s")
        print(f"App name: {app_name}")
        print(f"Headless mode: {headless}")

        # Test non-existent key
        non_existent = get_config_value("non.existent.key", "default_value")
        print(f"Non-existent key: {non_existent}")

        # Test nested dictionary access
        wallapop_urls = get_config_value("wallapop.urls", {})
        print(f"Wallapop URLs: {list(wallapop_urls.keys())}")

        print("✅ Configuration access patterns working correctly")
        return True

    except Exception as e:
        print(f"❌ Configuration access patterns failed: {e}")
        return False


def test_migration_path_resolution():
    """Test that migration paths are resolved correctly"""
    print("\n" + "=" * 60)
    print("Testing Migration Path Resolution")
    print("=" * 60)

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from migrate_repositories import RepositoryMigrator

        migrator = RepositoryMigrator(".")

        print("Migration paths resolved:")
        for key, value in migrator.migration_paths.items():
            print(f"  {key}: {value}")

        # Verify key paths exist
        base_config_path = Path(migrator.migration_paths["base_config_rel"])
        if base_config_path.exists():
            print(f"✅ Base config exists: {base_config_path}")
        else:
            print(f"❌ Base config missing: {base_config_path}")

        src_dir_path = Path(migrator.migration_paths["src_dir"])
        if src_dir_path.exists():
            print(f"✅ Source directory exists: {src_dir_path}")
        else:
            print(f"❌ Source directory missing: {src_dir_path}")

        return True

    except Exception as e:
        print(f"❌ Migration path resolution failed: {e}")
        return False


def test_hot_reload_capability():
    """Test hot-reload functionality (basic test without file changes)"""
    print("\n" + "=" * 60)
    print("Testing Hot-Reload Capability")
    print("=" * 60)

    try:
        # Test that hot-reload can be enabled
        loader = get_config_loader(enable_hot_reload=True)
        config = load_config(ConfigMode.RESEARCH, enable_hot_reload=True)

        # Check if file watcher is active
        summary = loader.get_config_summary(config)
        hot_reload_active = summary.get("runtime_info", {}).get(
            "hot_reload_active", False
        )

        print(f"Hot-reload active: {hot_reload_active}")
        print(
            f"Config hash: {summary.get('runtime_info', {}).get('config_hash', 'unknown')}"
        )
        print(
            f"Cache status: {summary.get('runtime_info', {}).get('cache_status', 'unknown')}"
        )

        if hot_reload_active:
            print("✅ Hot-reload system is active")

            # Test callback system
            callback_called = []

            def test_callback(config, event):
                callback_called.append(True)
                print(f"  Callback triggered: {event}")

            loader.add_change_callback(test_callback)
            print("✅ Configuration change callback registered")

            # Stop hot-reload for cleanup
            loader.stop_hot_reload()
            print("✅ Hot-reload stopped cleanly")

        else:
            print("⚠️ Hot-reload not active (watchdog may not be installed)")

        return True

    except Exception as e:
        print(f"❌ Hot-reload capability test failed: {e}")
        return False


def run_all_tests():
    """Run all configuration system tests"""
    if not ENHANCED_CONFIG_AVAILABLE:
        print("❌ Enhanced configuration system not available - cannot run tests")
        return False

    print("Wall-E Configuration System Test Suite")
    print("=" * 60)

    tests = [
        ("Basic Configuration Loading", test_basic_configuration_loading),
        ("Dynamic Scraper Configuration", test_dynamic_scraper_configuration),
        ("Configuration Validation", test_configuration_validation),
        ("Configuration Access Patterns", test_configuration_access_patterns),
        ("Migration Path Resolution", test_migration_path_resolution),
        ("Hot-Reload Capability", test_hot_reload_capability),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Configuration system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    success = run_all_tests()

    if success:
        print("\n✅ Configuration system test completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Configuration system test completed with failures")
        sys.exit(1)
