"""
Hierarchical Configuration Loader for Wall-E
Supports loading base configuration with version-specific overrides
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import deepmerge

logger = logging.getLogger(__name__)


class ConfigMode(Enum):
    """Configuration modes for different repository versions"""

    RESEARCH = "research"
    COMPLIANCE = "compliance"
    DEVELOPMENT = "development"


@dataclass
class ConfigPaths:
    """Configuration file paths (relative to config_dir)"""

    base_config: str = "base_config.yaml"
    research_overrides: str = "research_overrides.yaml"
    compliance_overrides: str = "compliance_overrides.yaml"
    environment_config: str = "environment.yaml"  # Optional
    local_config: str = "local.yaml"  # Optional, git-ignored


class ConfigurationLoader:
    """
    Hierarchical configuration loader that merges configurations in order:
    1. Base configuration (shared settings)
    2. Mode-specific overrides (research/compliance)
    3. Environment overrides (optional)
    4. Local overrides (optional, git-ignored)
    """

    def __init__(self, config_dir: Union[str, Path] = "config"):
        self.config_dir = Path(config_dir)
        self.paths = ConfigPaths()
        self._validate_config_directory()

    def _validate_config_directory(self) -> None:
        """Validate that the configuration directory exists"""
        if not self.config_dir.exists():
            raise FileNotFoundError(
                f"Configuration directory not found: {self.config_dir}"
            )

        base_config_path = self.config_dir / "base_config.yaml"
        if not base_config_path.exists():
            raise FileNotFoundError(
                f"Base configuration file not found: {base_config_path}"
            )

    def _load_yaml_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load a YAML file and return its contents"""
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}
                logger.debug(f"Loaded configuration from: {file_path}")
                return content
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading configuration file {file_path}: {e}")
            raise

    def _substitute_environment_variables(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively substitute environment variables in configuration values"""

        def substitute_value(value):
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                env_var = value[2:-1]  # Remove ${ and }
                env_value = os.getenv(env_var)
                if env_value is None:
                    logger.warning(
                        f"Environment variable {env_var} not found, using original value"
                    )
                    return value
                return env_value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value

        return substitute_value(config)

    def _merge_configurations(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        if not override:
            return base

        # Use deepmerge for sophisticated merging
        merger = deepmerge.Merger(
            [(list, ["append"]), (dict, ["merge"])], ["override"], ["override"]
        )

        return merger.merge(base, override)

    def load_configuration(
        self, mode: ConfigMode, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load complete configuration for the specified mode

        Args:
            mode: Configuration mode (research/compliance/development)
            environment: Optional environment name (dev/staging/prod)

        Returns:
            Complete merged configuration dictionary
        """
        logger.info(f"Loading configuration for mode: {mode.value}")

        # 1. Load base configuration
        base_config = self._load_yaml_file(self.config_dir / self.paths.base_config)

        # 2. Load mode-specific overrides
        mode_overrides = {}
        if mode == ConfigMode.RESEARCH:
            mode_overrides = self._load_yaml_file(
                self.config_dir / self.paths.research_overrides
            )
        elif mode == ConfigMode.COMPLIANCE:
            mode_overrides = self._load_yaml_file(
                self.config_dir / self.paths.compliance_overrides
            )

        # 3. Load environment-specific overrides (optional)
        env_overrides = {}
        if environment:
            env_file = self.config_dir / f"environments/{environment}.yaml"
            env_overrides = self._load_yaml_file(env_file)

        # 4. Load local overrides (optional, git-ignored)
        local_overrides = self._load_yaml_file(
            self.config_dir / self.paths.local_config
        )

        # 5. Merge configurations in order
        config = base_config
        config = self._merge_configurations(config, mode_overrides)
        config = self._merge_configurations(config, env_overrides)
        config = self._merge_configurations(config, local_overrides)

        # 6. Substitute environment variables
        config = self._substitute_environment_variables(config)

        # 7. Add runtime metadata
        config["_runtime"] = {
            "mode": mode.value,
            "environment": environment,
            "loaded_at": str(Path.cwd()),
            "config_files_loaded": [
                str(self.config_dir / self.paths.base_config),
                (
                    str(self.config_dir / self.paths.research_overrides)
                    if mode == ConfigMode.RESEARCH
                    else None
                ),
                (
                    str(self.config_dir / self.paths.compliance_overrides)
                    if mode == ConfigMode.COMPLIANCE
                    else None
                ),
                (
                    str(self.config_dir / f"environments/{environment}.yaml")
                    if environment
                    else None
                ),
                str(self.config_dir / self.paths.local_config),
            ],
        }

        # Remove None values from loaded files list
        config["_runtime"]["config_files_loaded"] = [
            f for f in config["_runtime"]["config_files_loaded"] if f is not None
        ]

        logger.info(f"Configuration loaded successfully for mode: {mode.value}")
        return config

    def validate_configuration(
        self, config: Dict[str, Any], mode: ConfigMode
    ) -> bool:  # noqa: C901
        """
        Validate configuration for compliance and correctness

        Args:
            config: Configuration dictionary
            mode: Configuration mode

        Returns:
            True if configuration is valid
        """
        validation_errors = []

        # Common validations
        if "app" not in config:
            validation_errors.append("Missing 'app' section in configuration")

        if "database" not in config:
            validation_errors.append("Missing 'database' section in configuration")

        # Mode-specific validations
        if mode == ConfigMode.COMPLIANCE:
            # Validate compliance-specific requirements
            wallapop = config.get("wallapop", {}).get("behavior", {})

            # CRITICAL: Check rate limits for compliance (max 5 messages/hour)
            max_messages_per_hour = wallapop.get("max_messages_per_hour", 0)
            if max_messages_per_hour > 5:
                validation_errors.append(
                    f"COMPLIANCE VIOLATION: max_messages_per_hour must be <= 5, got {max_messages_per_hour}"
                )

            # CRITICAL: Check anti-detection is disabled for transparency
            anti_detection = config.get("anti_detection", {})
            if anti_detection.get("enabled", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: anti_detection.enabled must be false for transparency"
                )

            # CRITICAL: Check GDPR compliance is enabled
            gdpr_compliance = config.get("security", {}).get("gdpr_compliance", {})
            if not gdpr_compliance.get("enabled", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: security.gdpr_compliance.enabled must be true"
                )

            # CRITICAL: Check human confirmation is required
            if not wallapop.get("human_confirmation_required", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: wallapop.behavior.human_confirmation_required must be true"
                )

            # CRITICAL: Check transparency disclosure is enabled
            if not wallapop.get("transparency_disclosure", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: wallapop.behavior.transparency_disclosure must be true"
                )

            # CRITICAL: Check consent collection is enabled
            if not wallapop.get("consent_collection", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: wallapop.behavior.consent_collection must be true"
                )

            # Check consent management system
            consent_mgmt = config.get("consent_management", {})
            if not consent_mgmt.get("enabled", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: consent_management.enabled must be true"
                )

            # Check human oversight system
            human_oversight = config.get("human_oversight", {})
            if not human_oversight.get("enabled", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: human_oversight.enabled must be true"
                )

            # Check legal documentation is enabled
            legal_docs = config.get("legal_documentation", {})
            if not legal_docs.get("enabled", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: legal_documentation.enabled must be true"
                )

            # Validate GDPR data retention limits
            data_retention = gdpr_compliance.get("data_retention", {})
            personal_data_days = data_retention.get("personal_data_days", 999)
            if personal_data_days > 30:
                validation_errors.append(
                    f"COMPLIANCE VIOLATION: GDPR requires personal_data_days <= 30, got {personal_data_days}"
                )

            # Validate conservative limits
            max_concurrent = wallapop.get("max_concurrent_conversations", 999)
            if max_concurrent > 5:
                validation_errors.append(
                    f"COMPLIANCE VIOLATION: max_concurrent_conversations should be <= 5, got {max_concurrent}"
                )

            # Check audit logging is enabled
            development = config.get("development", {}).get("compliance_tools", {})
            if not development.get("audit_logging", False):
                validation_errors.append(
                    "COMPLIANCE VIOLATION: development.compliance_tools.audit_logging must be true"
                )

        elif mode == ConfigMode.RESEARCH:
            # Validate research disclaimers exist
            app = config.get("app", {})
            if "research" not in app.get("mode", ""):
                validation_errors.append(
                    "Research mode requires app.mode to contain 'research'"
                )

        # Log validation results
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Configuration validation error: {error}")
            return False

        logger.info(f"Configuration validation passed for mode: {mode.value}")
        return True

    def get_config_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of key configuration settings"""
        wallapop_behavior = config.get("wallapop", {}).get("behavior", {})
        gdpr_compliance = config.get("security", {}).get("gdpr_compliance", {})

        summary = {
            "mode": config.get("app", {}).get("mode", "unknown"),
            "app_name": config.get("app", {}).get("name", "unknown"),
            "wallapop_settings": {
                "max_messages_per_hour": wallapop_behavior.get("max_messages_per_hour"),
                "max_concurrent_conversations": wallapop_behavior.get(
                    "max_concurrent_conversations"
                ),
                "anti_detection_enabled": config.get("anti_detection", {}).get(
                    "enabled", False
                ),
                "human_confirmation_required": wallapop_behavior.get(
                    "human_confirmation_required", False
                ),
                "transparency_disclosure": wallapop_behavior.get(
                    "transparency_disclosure", False
                ),
                "consent_collection": wallapop_behavior.get(
                    "consent_collection", False
                ),
            },
            "compliance_features": {
                "gdpr_enabled": gdpr_compliance.get("enabled", False),
                "human_oversight": config.get("human_oversight", {}).get(
                    "enabled", False
                ),
                "consent_management": config.get("consent_management", {}).get(
                    "enabled", False
                ),
                "legal_documentation": config.get("legal_documentation", {}).get(
                    "enabled", False
                ),
                "audit_logging": config.get("development", {})
                .get("compliance_tools", {})
                .get("audit_logging", False),
            },
            "gdpr_settings": {
                "data_minimization": gdpr_compliance.get("data_minimization", False),
                "purpose_limitation": gdpr_compliance.get("purpose_limitation", False),
                "consent_required": gdpr_compliance.get("consent_required", False),
                "right_to_be_forgotten": gdpr_compliance.get(
                    "right_to_be_forgotten", False
                ),
                "personal_data_retention_days": gdpr_compliance.get(
                    "data_retention", {}
                ).get("personal_data_days", None),
            },
            "security_settings": {
                "fraud_detection_enabled": config.get("security", {})
                .get("fraud_detection", {})
                .get("enabled", False),
                "strict_mode": config.get("security", {})
                .get("fraud_detection", {})
                .get("strict_mode", False),
                "encryption_at_rest": config.get("security", {})
                .get("data_collection", {})
                .get("encryption_at_rest", False),
                "anonymize_data": config.get("security", {})
                .get("data_collection", {})
                .get("anonymize_data", False),
            },
            "database": {
                "host": config.get("database", {}).get("host"),
                "name": config.get("database", {}).get("name"),
            },
        }

        return summary


def load_config(
    mode: Union[str, ConfigMode],
    environment: Optional[str] = None,
    config_dir: str = "config",
) -> Dict[str, Any]:
    """
    Convenience function to load configuration

    Args:
        mode: Configuration mode (research/compliance/development)
        environment: Optional environment name
        config_dir: Configuration directory path

    Returns:
        Complete configuration dictionary
    """
    if isinstance(mode, str):
        mode = ConfigMode(mode.lower())

    loader = ConfigurationLoader(config_dir)
    config = loader.load_configuration(mode, environment)

    # Validate configuration
    if not loader.validate_configuration(config, mode):
        raise ValueError(f"Configuration validation failed for mode: {mode.value}")

    return config


# Example usage
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)

    # Test loading research configuration
    try:
        research_config = load_config(ConfigMode.RESEARCH)
        print("Research configuration loaded successfully")

        loader = ConfigurationLoader()
        summary = loader.get_config_summary(research_config)
        print(f"Research config summary: {summary}")

    except Exception as e:
        print(f"Error loading research configuration: {e}")

    # Test loading compliance configuration
    try:
        compliance_config = load_config(ConfigMode.COMPLIANCE)
        print("Compliance configuration loaded successfully")

        loader = ConfigurationLoader()
        summary = loader.get_config_summary(compliance_config)
        print(f"Compliance config summary: {summary}")

    except Exception as e:
        print(f"Error loading compliance configuration: {e}")
