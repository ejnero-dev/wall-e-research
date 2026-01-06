#!/usr/bin/env python3
"""
Compliance Configuration Validation Script

This script validates that the wall-e-research project configuration meets all
GDPR and ethical compliance requirements. Run this before deploying to ensure
compliance with legal and ethical standards.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_loader import ConfigurationLoader, ConfigMode


def setup_logging():
    """Configure logging for validation script"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/tmp/compliance_validation.log"),
        ],
    )


def validate_compliance_mode_config() -> bool:
    """
    Validate compliance mode configuration meets all requirements

    Returns:
        True if configuration is fully compliant
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting compliance configuration validation...")

    try:
        # Initialize configuration loader with absolute path
        config_path = Path(__file__).parent.parent / "config"
        loader = ConfigurationLoader(config_dir=config_path)

        # Load compliance configuration
        config = loader.load_configuration(ConfigMode.COMPLIANCE)

        # Validate using built-in validation
        if not loader.validate_configuration(config, ConfigMode.COMPLIANCE):
            logger.error("Built-in configuration validation failed")
            return False

        # Additional compliance-specific checks
        compliance_errors = []

        # Check critical GDPR compliance settings
        gdpr_compliance = config.get("security", {}).get("gdpr_compliance", {})

        # Ensure all GDPR rights are implemented
        required_gdpr_rights = [
            "data_minimization",
            "purpose_limitation",
            "consent_required",
            "right_to_be_forgotten",
            "data_portability",
            "breach_notification",
        ]

        for right in required_gdpr_rights:
            if not gdpr_compliance.get(right, False):
                compliance_errors.append(f"GDPR right '{right}' must be enabled")

        # Check data retention limits
        data_retention = gdpr_compliance.get("data_retention", {})
        max_personal_retention = data_retention.get("personal_data_days", 999)
        if max_personal_retention > 30:
            compliance_errors.append(
                f"Personal data retention exceeds GDPR limits: {max_personal_retention} > 30 days"
            )

        # Check rate limiting is ethical
        wallapop_behavior = config.get("wallapop", {}).get("behavior", {})
        max_messages_hour = wallapop_behavior.get("max_messages_per_hour", 999)
        if max_messages_hour > 5:
            compliance_errors.append(
                f"Message rate exceeds ethical limits: {max_messages_hour} > 5 per hour"
            )

        # Check transparency requirements
        transparency_checks = [
            ("human_confirmation_required", "Human confirmation"),
            ("transparency_disclosure", "Transparency disclosure"),
            ("consent_collection", "Consent collection"),
            ("opt_out_mechanism", "Opt-out mechanism"),
        ]

        for setting, description in transparency_checks:
            if not wallapop_behavior.get(setting, False):
                compliance_errors.append(
                    f"{description} must be enabled for compliance"
                )

        # Check anti-detection is disabled
        anti_detection = config.get("anti_detection", {})
        if anti_detection.get("enabled", False):
            compliance_errors.append("Anti-detection must be disabled for transparency")

        # Check that stealth features are disabled
        stealth_features = [
            ("stealth_mode", "Stealth mode"),
            ("fingerprint_randomization", "Fingerprint randomization"),
            ("webdriver_detection_bypass", "WebDriver detection bypass"),
            ("automation_markers_hiding", "Automation markers hiding"),
        ]

        browser_config = anti_detection.get("browser", {})
        evasion_config = anti_detection.get("evasion", {})

        for setting, description in stealth_features:
            if browser_config.get(setting, False) or evasion_config.get(setting, False):
                compliance_errors.append(
                    f"{description} must be disabled for compliance"
                )

        # Check compliance mode transparency settings
        compliance_mode_config = anti_detection.get("compliance_mode", {})
        transparency_requirements = [
            ("identify_as_automated", "Must identify as automated"),
            ("display_automation_notice", "Must display automation notice"),
            ("allow_detection", "Must allow platform detection"),
        ]

        for setting, description in transparency_requirements:
            if not compliance_mode_config.get(setting, False):
                compliance_errors.append(f"{description} for compliance")

        # Check mandatory systems are enabled
        mandatory_systems = [
            ("consent_management", "Consent management system"),
            ("human_oversight", "Human oversight system"),
            ("legal_documentation", "Legal documentation system"),
        ]

        for system, description in mandatory_systems:
            if not config.get(system, {}).get("enabled", False):
                compliance_errors.append(f"{description} must be enabled")

        # Check audit logging is enabled
        compliance_tools = config.get("development", {}).get("compliance_tools", {})
        if not compliance_tools.get("audit_logging", False):
            compliance_errors.append("Audit logging must be enabled for compliance")

        # Check data collection settings
        data_collection = config.get("security", {}).get("data_collection", {})
        required_data_protection = [
            ("anonymize_data", "Data anonymization"),
            ("pseudonymization", "Data pseudonymization"),
            ("encryption_at_rest", "Encryption at rest"),
            ("encryption_in_transit", "Encryption in transit"),
        ]

        for setting, description in required_data_protection:
            if not data_collection.get(setting, False):
                compliance_errors.append(f"{description} must be enabled")

        # Report results
        if compliance_errors:
            logger.error("COMPLIANCE VALIDATION FAILED:")
            for error in compliance_errors:
                logger.error(f"  - {error}")
            return False

        logger.info("✅ Compliance configuration validation PASSED")
        logger.info("Configuration meets all GDPR and ethical requirements")

        return True

    except Exception as e:
        logger.error(f"Compliance validation failed with error: {e}")
        return False


def print_compliance_summary(config: Dict[str, Any]) -> None:
    """Print a summary of compliance settings"""
    logger = logging.getLogger(__name__)

    logger.info("\n=== COMPLIANCE CONFIGURATION SUMMARY ===")

    # Basic app info
    app = config.get("app", {})
    logger.info(
        f"App: {app.get('name', 'Unknown')} (Mode: {app.get('mode', 'Unknown')})"
    )

    # Rate limiting
    wallapop_behavior = config.get("wallapop", {}).get("behavior", {})
    logger.info(f"Rate Limits:")
    logger.info(
        f"  - Max messages/hour: {wallapop_behavior.get('max_messages_per_hour', 'Not set')}"
    )
    logger.info(
        f"  - Max concurrent conversations: {wallapop_behavior.get('max_concurrent_conversations', 'Not set')}"
    )

    # Transparency features
    logger.info("Transparency Features:")
    logger.info(
        f"  - Human confirmation required: {wallapop_behavior.get('human_confirmation_required', False)}"
    )
    logger.info(
        f"  - Transparency disclosure: {wallapop_behavior.get('transparency_disclosure', False)}"
    )
    logger.info(
        f"  - Consent collection: {wallapop_behavior.get('consent_collection', False)}"
    )

    # GDPR compliance
    gdpr = config.get("security", {}).get("gdpr_compliance", {})
    logger.info("GDPR Compliance:")
    logger.info(f"  - GDPR enabled: {gdpr.get('enabled', False)}")
    logger.info(f"  - Data minimization: {gdpr.get('data_minimization', False)}")
    logger.info(f"  - Purpose limitation: {gdpr.get('purpose_limitation', False)}")
    logger.info(
        f"  - Personal data retention: {gdpr.get('data_retention', {}).get('personal_data_days', 'Not set')} days"
    )

    # Mandatory systems
    logger.info("Mandatory Systems:")
    logger.info(
        f"  - Consent management: {config.get('consent_management', {}).get('enabled', False)}"
    )
    logger.info(
        f"  - Human oversight: {config.get('human_oversight', {}).get('enabled', False)}"
    )
    logger.info(
        f"  - Legal documentation: {config.get('legal_documentation', {}).get('enabled', False)}"
    )

    # Anti-detection status
    anti_detection = config.get("anti_detection", {})
    logger.info(
        f"Anti-detection: {anti_detection.get('enabled', False)} (Must be False for compliance)"
    )


def main():
    """Main validation function"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Wall-E Research Project - GDPR Compliance Configuration Validation")
    logger.info("=" * 70)

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    try:
        # Validate compliance configuration
        is_compliant = validate_compliance_mode_config()

        if is_compliant:
            # Load config for summary
            config_path = Path(__file__).parent.parent / "config"
            loader = ConfigurationLoader(config_dir=config_path)
            config = loader.load_configuration(ConfigMode.COMPLIANCE)
            print_compliance_summary(config)

            logger.info("\n🎉 COMPLIANCE VALIDATION SUCCESSFUL")
            logger.info("Configuration is ready for ethical and legal deployment")
            sys.exit(0)
        else:
            logger.error("\n❌ COMPLIANCE VALIDATION FAILED")
            logger.error("Configuration does not meet compliance requirements")
            logger.error("Please review and fix the reported issues before deployment")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
