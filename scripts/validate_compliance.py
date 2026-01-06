#!/usr/bin/env python3
"""
COMPLIANCE VALIDATION SCRIPT
============================

This script validates that the Wall-E Compliance Assistant meets all
ethical and legal requirements for commercial use.

Usage: python scripts/validate_compliance.py
"""

import os
import sys
import json
import yaml
import logging
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ComplianceLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    PASS = "PASS"


@dataclass
class ValidationResult:
    check_name: str
    level: ComplianceLevel
    passed: bool
    message: str
    recommendation: str = ""


class ComplianceValidator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.results: List[ValidationResult] = []

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all compliance validations"""

        print("🛡️  WALL-E COMPLIANCE VALIDATION")
        print("=" * 50)

        # Critical checks
        self._validate_config_compliance()
        self._validate_rate_limits()
        self._validate_anti_detection_disabled()
        self._validate_human_oversight()
        self._validate_gdpr_compliance()

        # Documentation checks
        self._validate_legal_documentation()
        self._validate_transparency_features()

        # Code compliance checks
        self._validate_code_restrictions()

        # Generate report
        return self._generate_report()

    def _validate_config_compliance(self):
        """Validate configuration compliance"""
        config_path = self.base_path / "config" / "base_config.yaml"

        if not config_path.exists():
            self.results.append(
                ValidationResult(
                    "Configuration File",
                    ComplianceLevel.CRITICAL,
                    False,
                    "Configuration file missing",
                    "Ensure config/base_config.yaml exists with compliance settings",
                )
            )
            return

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # Check critical compliance settings
            wallapop_config = config.get("wallapop", {})
            behavior = wallapop_config.get("behavior", {})

            if behavior.get("human_confirmation_required") != True:
                self.results.append(
                    ValidationResult(
                        "Human Confirmation",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Human confirmation not enabled",
                        "Set wallapop.behavior.human_confirmation_required = true",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Human Confirmation",
                        ComplianceLevel.PASS,
                        True,
                        "Human confirmation properly enabled",
                    )
                )

            # Check transparency
            if behavior.get("transparency_disclosure") != True:
                self.results.append(
                    ValidationResult(
                        "Transparency Disclosure",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Transparency disclosure not enabled",
                        "Set wallapop.behavior.transparency_disclosure = true",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Transparency Disclosure",
                        ComplianceLevel.PASS,
                        True,
                        "Transparency properly configured",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    "Configuration Parsing",
                    ComplianceLevel.CRITICAL,
                    False,
                    f"Failed to parse configuration: {e}",
                    "Fix YAML syntax errors in configuration file",
                )
            )

    def _validate_rate_limits(self):
        """Validate rate limiting compliance"""
        config_path = self.base_path / "config" / "base_config.yaml"

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            behavior = config.get("wallapop", {}).get("behavior", {})

            # Check messages per hour
            max_messages_hour = behavior.get("max_messages_per_hour", 0)
            if max_messages_hour > 5:
                self.results.append(
                    ValidationResult(
                        "Hourly Rate Limit",
                        ComplianceLevel.CRITICAL,
                        False,
                        f"Rate limit too high: {max_messages_hour}/hour (max: 5)",
                        "Reduce max_messages_per_hour to 5 or less",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Hourly Rate Limit",
                        ComplianceLevel.PASS,
                        True,
                        f"Rate limit compliant: {max_messages_hour}/hour",
                    )
                )

            # Check actions per minute
            max_actions_minute = behavior.get("max_actions_per_minute", 1.0)
            if max_actions_minute > 0.2:
                self.results.append(
                    ValidationResult(
                        "Minute Rate Limit",
                        ComplianceLevel.HIGH,
                        False,
                        f"Action rate too high: {max_actions_minute}/min (max: 0.2)",
                        "Reduce max_actions_per_minute to 0.2 or less",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Minute Rate Limit",
                        ComplianceLevel.PASS,
                        True,
                        f"Action rate compliant: {max_actions_minute}/min",
                    )
                )

            # Check minimum delay
            min_delay = behavior.get("min_delay_between_messages", 0)
            if min_delay < 120:
                self.results.append(
                    ValidationResult(
                        "Minimum Delay",
                        ComplianceLevel.HIGH,
                        False,
                        f"Minimum delay too short: {min_delay}s (min: 120s)",
                        "Increase min_delay_between_messages to 120 seconds",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Minimum Delay",
                        ComplianceLevel.PASS,
                        True,
                        f"Minimum delay compliant: {min_delay}s",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    "Rate Limit Validation",
                    ComplianceLevel.CRITICAL,
                    False,
                    f"Failed to validate rate limits: {e}",
                    "Check configuration file syntax and completeness",
                )
            )

    def _validate_anti_detection_disabled(self):
        """Validate anti-detection features are properly disabled"""

        try:
            with open(self.base_path / "config" / "base_config.yaml", "r") as f:
                config = yaml.safe_load(f)

            anti_detection = config.get("anti_detection", {})

            if anti_detection.get("enabled") != False:
                self.results.append(
                    ValidationResult(
                        "Anti-Detection Disabled",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Anti-detection features must be disabled",
                        "Set anti_detection.enabled = false",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Anti-Detection Disabled",
                        ComplianceLevel.PASS,
                        True,
                        "Anti-detection properly disabled",
                    )
                )

            # Check specific evasion features
            evasion = anti_detection.get("evasion", {})
            if evasion.get("webdriver_detection_bypass") != False:
                self.results.append(
                    ValidationResult(
                        "WebDriver Bypass Disabled",
                        ComplianceLevel.CRITICAL,
                        False,
                        "WebDriver detection bypass must be disabled",
                        "Set anti_detection.evasion.webdriver_detection_bypass = false",
                    )
                )

            browser = anti_detection.get("browser", {})
            if browser.get("user_agent_rotation") != False:
                self.results.append(
                    ValidationResult(
                        "User Agent Rotation Disabled",
                        ComplianceLevel.HIGH,
                        False,
                        "User agent rotation must be disabled",
                        "Set anti_detection.browser.user_agent_rotation = false",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    "Anti-Detection Validation",
                    ComplianceLevel.CRITICAL,
                    False,
                    f"Failed to validate anti-detection settings: {e}",
                    "Check configuration file",
                )
            )

    def _validate_human_oversight(self):
        """Validate human oversight mechanisms"""

        try:
            with open(self.base_path / "config" / "base_config.yaml", "r") as f:
                config = yaml.safe_load(f)

            oversight = config.get("human_oversight", {})

            if oversight.get("enabled") != True:
                self.results.append(
                    ValidationResult(
                        "Human Oversight Enabled",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Human oversight system must be enabled",
                        "Set human_oversight.enabled = true",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Human Oversight Enabled",
                        ComplianceLevel.PASS,
                        True,
                        "Human oversight properly enabled",
                    )
                )

            # Check escalation triggers
            triggers = oversight.get("escalation_triggers", [])
            required_triggers = ["user_requests_human", "compliance_violation"]

            missing_triggers = [t for t in required_triggers if t not in triggers]
            if missing_triggers:
                self.results.append(
                    ValidationResult(
                        "Escalation Triggers",
                        ComplianceLevel.HIGH,
                        False,
                        f"Missing escalation triggers: {missing_triggers}",
                        "Add all required escalation triggers to configuration",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    "Human Oversight Validation",
                    ComplianceLevel.CRITICAL,
                    False,
                    f"Failed to validate human oversight: {e}",
                    "Check configuration file",
                )
            )

    def _validate_gdpr_compliance(self):
        """Validate GDPR compliance features"""

        try:
            with open(self.base_path / "config" / "base_config.yaml", "r") as f:
                config = yaml.safe_load(f)

            gdpr = config.get("security", {}).get("gdpr_compliance", {})

            if gdpr.get("enabled") != True:
                self.results.append(
                    ValidationResult(
                        "GDPR Features Enabled",
                        ComplianceLevel.CRITICAL,
                        False,
                        "GDPR compliance features must be enabled",
                        "Set security.gdpr_compliance.enabled = true",
                    )
                )

            required_features = [
                "consent_required",
                "data_minimization",
                "right_to_be_forgotten",
            ]

            for feature in required_features:
                if gdpr.get(feature) != True:
                    self.results.append(
                        ValidationResult(
                            f"GDPR {feature.title()}",
                            ComplianceLevel.CRITICAL,
                            False,
                            f"GDPR {feature} must be enabled",
                            f"Set security.gdpr_compliance.{feature} = true",
                        )
                    )

            # Check consent management
            consent = config.get("consent_management", {})
            if consent.get("enabled") != True:
                self.results.append(
                    ValidationResult(
                        "Consent Management",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Consent management system must be enabled",
                        "Set consent_management.enabled = true",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    "GDPR Validation",
                    ComplianceLevel.CRITICAL,
                    False,
                    f"Failed to validate GDPR compliance: {e}",
                    "Check configuration file",
                )
            )

    def _validate_legal_documentation(self):
        """Validate required legal documentation exists"""

        required_docs = {
            "LICENSE": "License with commercial use restrictions",
            "LEGAL_NOTICE.md": "Legal notice and warnings",
            "README.md": "README with compliance warnings",
        }

        for doc_name, description in required_docs.items():
            doc_path = self.base_path / doc_name

            if not doc_path.exists():
                self.results.append(
                    ValidationResult(
                        f"Legal Documentation - {doc_name}",
                        ComplianceLevel.CRITICAL,
                        False,
                        f"Missing required document: {doc_name}",
                        f"Create {description}",
                    )
                )
            else:
                # Check if file has compliance content
                content = doc_path.read_text()
                if (
                    "compliance" not in content.lower()
                    and "gdpr" not in content.lower()
                ):
                    self.results.append(
                        ValidationResult(
                            f"Legal Content - {doc_name}",
                            ComplianceLevel.HIGH,
                            False,
                            f"{doc_name} lacks compliance warnings",
                            f"Add proper compliance notices to {doc_name}",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            f"Legal Documentation - {doc_name}",
                            ComplianceLevel.PASS,
                            True,
                            f"{doc_name} exists with compliance content",
                        )
                    )

    def _validate_transparency_features(self):
        """Validate transparency and disclosure features"""

        # Check bot file for human confirmation
        bot_file = self.base_path / "src" / "bot" / "wallapop_bot.py"

        if bot_file.exists():
            content = bot_file.read_text()

            if "request_human_confirmation" not in content:
                self.results.append(
                    ValidationResult(
                        "Human Confirmation Code",
                        ComplianceLevel.CRITICAL,
                        False,
                        "Bot lacks human confirmation implementation",
                        "Implement request_human_confirmation method",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        "Human Confirmation Code",
                        ComplianceLevel.PASS,
                        True,
                        "Human confirmation method found",
                    )
                )

            if "GDPR" not in content and "gdpr" not in content:
                self.results.append(
                    ValidationResult(
                        "GDPR Implementation",
                        ComplianceLevel.HIGH,
                        False,
                        "Bot lacks GDPR compliance code",
                        "Add GDPR consent and data protection features",
                    )
                )
        else:
            self.results.append(
                ValidationResult(
                    "Bot File Exists",
                    ComplianceLevel.CRITICAL,
                    False,
                    "Bot implementation file missing",
                    "Ensure src/bot/wallapop_bot.py exists",
                )
            )

    def _validate_code_restrictions(self):
        """Validate code compliance and restrictions"""

        # Check anti-detection file
        anti_detection_file = self.base_path / "src" / "scraper" / "anti_detection.py"

        if anti_detection_file.exists():
            content = anti_detection_file.read_text()

            # Check for compliance notices
            if "COMPLIANCE" not in content:
                self.results.append(
                    ValidationResult(
                        "Anti-Detection Compliance",
                        ComplianceLevel.HIGH,
                        False,
                        "Anti-detection lacks compliance notices",
                        "Add compliance warnings to anti-detection code",
                    )
                )

            # Check for disabled features
            if "webdriver_detection_bypass: false" not in content:
                if "webdriver" in content.lower():
                    self.results.append(
                        ValidationResult(
                            "WebDriver Bypass Check",
                            ComplianceLevel.CRITICAL,
                            False,
                            "WebDriver bypass code may still be active",
                            "Ensure all WebDriver evasion is disabled",
                        )
                    )

        # Check scraper config
        scraper_config = self.base_path / "src" / "scraper" / "config.py"

        if scraper_config.exists():
            content = scraper_config.read_text()

            if "COMPLIANCE" not in content:
                self.results.append(
                    ValidationResult(
                        "Scraper Config Compliance",
                        ComplianceLevel.MEDIUM,
                        False,
                        "Scraper config lacks compliance markers",
                        "Add compliance notices to scraper configuration",
                    )
                )

    def _generate_report(self) -> Tuple[bool, List[ValidationResult]]:
        """Generate compliance validation report"""

        print(f"\n📊 COMPLIANCE VALIDATION REPORT")
        print("=" * 50)

        # Count results by level
        counts = {level: 0 for level in ComplianceLevel}
        failed_critical = 0

        for result in self.results:
            counts[result.level] += 1
            if not result.passed and result.level == ComplianceLevel.CRITICAL:
                failed_critical += 1

        print(f"Total Checks: {len(self.results)}")
        print(f"✅ Passed: {counts[ComplianceLevel.PASS]}")
        print(f"🚨 Critical Issues: {counts[ComplianceLevel.CRITICAL]}")
        print(f"⚠️  High Issues: {counts[ComplianceLevel.HIGH]}")
        print(f"📋 Medium Issues: {counts[ComplianceLevel.MEDIUM]}")
        print(f"ℹ️  Low Issues: {counts[ComplianceLevel.LOW]}")

        print(f"\n📝 DETAILED RESULTS:")
        print("-" * 50)

        # Group by compliance level
        for level in [
            ComplianceLevel.CRITICAL,
            ComplianceLevel.HIGH,
            ComplianceLevel.MEDIUM,
            ComplianceLevel.LOW,
            ComplianceLevel.PASS,
        ]:

            level_results = [r for r in self.results if r.level == level]
            if not level_results:
                continue

            print(f"\n{level.value} ISSUES:")
            for result in level_results:
                status = "✅" if result.passed else "❌"
                print(f"  {status} {result.check_name}: {result.message}")
                if not result.passed and result.recommendation:
                    print(f"     💡 {result.recommendation}")

        # Final assessment
        print(f"\n🏁 FINAL ASSESSMENT:")
        print("=" * 30)

        if failed_critical > 0:
            print("❌ COMPLIANCE VALIDATION FAILED")
            print(f"   {failed_critical} CRITICAL issues must be resolved")
            print("   🚫 NOT READY for commercial use")
            overall_passed = False
        elif counts[ComplianceLevel.HIGH] > 0:
            print("⚠️  COMPLIANCE VALIDATION PARTIAL")
            print(f"   {counts[ComplianceLevel.HIGH]} HIGH priority issues remain")
            print("   ⚡ Address before commercial use")
            overall_passed = False
        else:
            print("✅ COMPLIANCE VALIDATION PASSED")
            print("   🎉 Ready for legal review and commercial use")
            print("   📋 Remember: Legal consultation still required")
            overall_passed = True

        return overall_passed, self.results


def main():
    """Main validation function"""

    validator = ComplianceValidator()
    passed, results = validator.validate_all()

    # Exit with appropriate code
    if passed:
        print(f"\n🎯 Next Steps:")
        print("  1. Schedule legal consultation")
        print("  2. Obtain professional liability insurance")
        print("  3. Create business privacy policy")
        print("  4. Setup GDPR compliance documentation")
        sys.exit(0)
    else:
        print(f"\n🚨 Action Required:")
        print("  1. Fix all CRITICAL issues immediately")
        print("  2. Address HIGH priority issues")
        print("  3. Re-run validation")
        print("  4. Only then proceed to legal review")
        sys.exit(1)


if __name__ == "__main__":
    main()
