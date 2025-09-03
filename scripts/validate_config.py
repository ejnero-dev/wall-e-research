#!/usr/bin/env python3
"""
Configuration Validation Script
Tests the hierarchical configuration system and validates compliance
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from config_loader import ConfigurationLoader, ConfigMode, load_config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to install dependencies: pip install -r requirements.txt")
    sys.exit(1)


def test_configuration_loading():
    """Test loading both research and compliance configurations"""
    print("=" * 60)
    print("           CONFIGURATION VALIDATION")
    print("=" * 60)
    
    results = {}
    
    # Test research configuration
    print("\n📊 Testing Research Configuration...")
    try:
        research_config = load_config(ConfigMode.RESEARCH)
        print("✅ Research configuration loaded successfully")
        results['research'] = {
            'loaded': True,
            'config': research_config
        }
    except Exception as e:
        print(f"❌ Research configuration failed: {e}")
        results['research'] = {
            'loaded': False,
            'error': str(e)
        }
    
    # Test compliance configuration
    print("\n🔒 Testing Compliance Configuration...")
    try:
        compliance_config = load_config(ConfigMode.COMPLIANCE)
        print("✅ Compliance configuration loaded successfully")
        results['compliance'] = {
            'loaded': True,
            'config': compliance_config
        }
    except Exception as e:
        print(f"❌ Compliance configuration failed: {e}")
        results['compliance'] = {
            'loaded': False,
            'error': str(e)
        }
    
    return results


def validate_compliance_requirements(config):
    """Validate that compliance configuration meets requirements"""
    print("\n🔍 Validating Compliance Requirements...")
    
    violations = []
    
    # Check rate limits
    wallapop_behavior = config.get('wallapop', {}).get('behavior', {})
    max_messages_per_hour = wallapop_behavior.get('max_messages_per_hour', 0)
    if max_messages_per_hour > 5:
        violations.append(f"Rate limit too high: {max_messages_per_hour} messages/hour (max: 5)")
    
    max_actions_per_minute = wallapop_behavior.get('max_actions_per_minute', 0)
    if max_actions_per_minute > 0.5:
        violations.append(f"Action rate too high: {max_actions_per_minute} actions/minute (max: 0.5)")
    
    # Check anti-detection is disabled
    anti_detection = config.get('anti_detection', {})
    if anti_detection.get('enabled', True):
        violations.append("Anti-detection must be disabled for compliance")
    
    # Check GDPR compliance
    gdpr_compliance = config.get('security', {}).get('gdpr_compliance', {})
    if not gdpr_compliance.get('enabled', False):
        violations.append("GDPR compliance must be enabled")
    
    # Check human oversight
    human_oversight = config.get('human_oversight', {})
    if not human_oversight.get('enabled', False):
        violations.append("Human oversight must be enabled")
    
    # Check consent management
    consent_management = config.get('consent_management', {})
    if not consent_management.get('enabled', False):
        violations.append("Consent management must be enabled")
    
    # Report results
    if violations:
        print("❌ Compliance violations found:")
        for violation in violations:
            print(f"   • {violation}")
        return False
    else:
        print("✅ All compliance requirements met")
        return True


def validate_research_features(config):
    """Validate that research configuration has expected features"""
    print("\n🔬 Validating Research Features...")
    
    missing_features = []
    
    # Check research mode is set
    app_mode = config.get('app', {}).get('mode', '')
    if 'research' not in app_mode:
        missing_features.append("App mode should indicate research")
    
    # Check anti-detection is available
    anti_detection = config.get('anti_detection', {})
    if not anti_detection.get('enabled', False):
        missing_features.append("Anti-detection should be enabled for research")
    
    # Check higher rate limits
    wallapop_behavior = config.get('wallapop', {}).get('behavior', {})
    max_messages_per_hour = wallapop_behavior.get('max_messages_per_hour', 0)
    if max_messages_per_hour < 20:
        missing_features.append(f"Research rate limits seem low: {max_messages_per_hour} messages/hour")
    
    # Check research features
    research_features = config.get('wallapop', {}).get('behavior', {}).get('experimental_features', {})
    if not research_features.get('enabled', False):
        missing_features.append("Experimental features should be enabled for research")
    
    # Report results
    if missing_features:
        print("⚠️ Missing research features:")
        for feature in missing_features:
            print(f"   • {feature}")
        return False
    else:
        print("✅ All research features present")
        return True


def compare_configurations(research_config, compliance_config):
    """Compare key differences between configurations"""
    print("\n📊 Configuration Comparison:")
    print("-" * 40)
    
    # Rate limit comparison
    research_rate = research_config.get('wallapop', {}).get('behavior', {}).get('max_messages_per_hour', 0)
    compliance_rate = compliance_config.get('wallapop', {}).get('behavior', {}).get('max_messages_per_hour', 0)
    
    print(f"Messages/Hour:")
    print(f"  Research:   {research_rate}")
    print(f"  Compliance: {compliance_rate}")
    print(f"  Difference: {research_rate - compliance_rate}x more aggressive")
    
    # Anti-detection comparison
    research_anti = research_config.get('anti_detection', {}).get('enabled', False)
    compliance_anti = compliance_config.get('anti_detection', {}).get('enabled', False)
    
    print(f"\nAnti-Detection:")
    print(f"  Research:   {'Enabled' if research_anti else 'Disabled'}")
    print(f"  Compliance: {'Enabled' if compliance_anti else 'Disabled'}")
    
    # GDPR comparison
    research_gdpr = research_config.get('security', {}).get('gdpr_compliance', {}).get('enabled', False)
    compliance_gdpr = compliance_config.get('security', {}).get('gdpr_compliance', {}).get('enabled', False)
    
    print(f"\nGDPR Compliance:")
    print(f"  Research:   {'Enabled' if research_gdpr else 'Disabled'}")
    print(f"  Compliance: {'Enabled' if compliance_gdpr else 'Disabled'}")


def generate_config_summary(results):
    """Generate a summary report of configuration validation"""
    print("\n" + "=" * 60)
    print("           VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    
    for config_type, result in results.items():
        if result['loaded']:
            print(f"✅ {config_type.title()} configuration: LOADED")
        else:
            print(f"❌ {config_type.title()} configuration: FAILED")
            print(f"   Error: {result['error']}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All configurations loaded successfully!")
        print("\nNext steps:")
        print("1. Test configurations in actual application")
        print("2. Perform legal review of compliance settings")
        print("3. Create repository separation")
        print("4. Set up monitoring and alerts")
    else:
        print("\n❌ Configuration validation failed!")
        print("\nFix the errors above before proceeding.")
    
    return all_passed


def main():
    """Main validation function"""
    # Test configuration loading
    results = test_configuration_loading()
    
    # Validate compliance if loaded
    if results.get('compliance', {}).get('loaded', False):
        compliance_valid = validate_compliance_requirements(results['compliance']['config'])
        results['compliance']['compliant'] = compliance_valid
    
    # Validate research if loaded
    if results.get('research', {}).get('loaded', False):
        research_valid = validate_research_features(results['research']['config'])
        results['research']['valid'] = research_valid
    
    # Compare configurations if both loaded
    if (results.get('research', {}).get('loaded', False) and 
        results.get('compliance', {}).get('loaded', False)):
        compare_configurations(
            results['research']['config'],
            results['compliance']['config']
        )
    
    # Generate summary
    success = generate_config_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()