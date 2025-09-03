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
    """Configuration file paths"""

    base_config: str = "config/base_config.yaml"
    research_overrides: str = "config/research_overrides.yaml"
    compliance_overrides: str = "config/compliance_overrides.yaml"
    environment_config: str = "config/environment.yaml"  # Optional
    local_config: str = "config/local.yaml"  # Optional, git-ignored


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

    def validate_configuration(self, config: Dict[str, Any], mode: ConfigMode) -> bool:
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

            # Check rate limits for compliance
            max_messages_per_hour = wallapop.get("max_messages_per_hour", 0)
            if max_messages_per_hour > 5:
                validation_errors.append(
                    f"Compliance mode requires max_messages_per_hour <= 5, got {max_messages_per_hour}"
                )

            # Check anti-detection is disabled
            anti_detection = config.get("anti_detection", {})
            if anti_detection.get("enabled", False):
                validation_errors.append(
                    "Compliance mode requires anti_detection.enabled = false"
                )

            # Check GDPR compliance is enabled
            gdpr_compliance = config.get("security", {}).get("gdpr_compliance", {})
            if not gdpr_compliance.get("enabled", False):
                validation_errors.append(
                    "Compliance mode requires security.gdpr_compliance.enabled = true"
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

        logger.info("Configuration validation passed")
        return True

    def get_config_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of key configuration settings"""
        summary = {
            "mode": config.get("app", {}).get("mode", "unknown"),
            "app_name": config.get("app", {}).get("name", "unknown"),
            "wallapop_settings": {
                "max_messages_per_hour": config.get("wallapop", {})
                .get("behavior", {})
                .get("max_messages_per_hour"),
                "max_concurrent_conversations": config.get("wallapop", {})
                .get("behavior", {})
                .get("max_concurrent_conversations"),
                "anti_detection_enabled": config.get("anti_detection", {}).get(
                    "enabled", False
                ),
            },
            "compliance_features": {
                "gdpr_enabled": config.get("security", {})
                .get("gdpr_compliance", {})
                .get("enabled", False),
                "human_oversight": config.get("human_oversight", {}).get(
                    "enabled", False
                ),
                "consent_management": config.get("consent_management", {}).get(
                    "enabled", False
                ),
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
