"""
Advanced Hierarchical Configuration Loader for Wall-E
Supports loading base configuration with version-specific overrides and hot-reloading
"""

import os
import yaml
import json
import logging
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import deepmerge

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    WATCHDOG_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConfigChangeEvent:
    """Event fired when configuration changes"""

    def __init__(self, file_path: str, change_type: str, timestamp: datetime = None):
        self.file_path = file_path
        self.change_type = change_type  # 'modified', 'created', 'deleted'
        self.timestamp = timestamp or datetime.now()

    def __str__(self):
        return f"ConfigChangeEvent({self.change_type}: {self.file_path} at {self.timestamp})"


class ConfigFileWatcher(FileSystemEventHandler):
    """File system event handler for configuration file changes"""

    def __init__(
        self, callback: Callable[[ConfigChangeEvent], None], patterns: List[str] = None
    ):
        super().__init__()
        self.callback = callback
        self.patterns = patterns or ["*.yaml", "*.yml", "*.json"]
        self.last_modified = {}

    def _should_handle_file(self, file_path: str) -> bool:
        """Check if file matches watch patterns"""
        path = Path(file_path)
        return any(path.match(pattern) for pattern in self.patterns)

    def _debounce_file_change(self, file_path: str) -> bool:
        """Debounce rapid file changes (common with editors)"""
        now = time.time()
        last_time = self.last_modified.get(file_path, 0)

        if now - last_time < 1.0:  # Ignore changes within 1 second
            return False

        self.last_modified[file_path] = now
        return True

    def on_modified(self, event):
        if not event.is_directory and self._should_handle_file(event.src_path):
            if self._debounce_file_change(event.src_path):
                self.callback(ConfigChangeEvent(event.src_path, "modified"))

    def on_created(self, event):
        if not event.is_directory and self._should_handle_file(event.src_path):
            self.callback(ConfigChangeEvent(event.src_path, "created"))

    def on_deleted(self, event):
        if not event.is_directory and self._should_handle_file(event.src_path):
            self.callback(ConfigChangeEvent(event.src_path, "deleted"))


class ConfigMode(Enum):
    """Configuration modes for different repository versions"""

    RESEARCH = "research"
    COMPLIANCE = "compliance"
    DEVELOPMENT = "development"


@dataclass
class ConfigPaths:
    """Configuration file paths"""

    base_config: str = "base_config.yaml"
    research_overrides: str = "research_overrides.yaml"
    compliance_overrides: str = "compliance_overrides.yaml"
    environment_config: str = "environment.yaml"  # Optional
    local_config: str = "local.yaml"  # Optional, git-ignored

    # Hot-reload configuration
    hot_reload_backup_dir: str = "backups/config"
    change_log_file: str = "logs/config_changes.log"

    # Migration script paths - moved from hardcoded values
    migration_paths: Dict[str, str] = field(
        default_factory=lambda: {
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
    )


class EnhancedConfigurationLoader:
    """
    Advanced Hierarchical configuration loader with hot-reloading capabilities:
    1. Base configuration (shared settings)
    2. Mode-specific overrides (research/compliance)
    3. Environment overrides (optional)
    4. Local overrides (optional, git-ignored)
    5. Hot-reloading with file watchers
    6. Configuration validation and backup
    """

    def __init__(
        self, config_dir: Union[str, Path] = "config", enable_hot_reload: bool = True
    ):
        self.config_dir = Path(config_dir)
        self.paths = ConfigPaths()
        self.enable_hot_reload = enable_hot_reload and WATCHDOG_AVAILABLE

        # Configuration cache and state
        self._current_config: Optional[Dict[str, Any]] = None
        self._current_mode: Optional[ConfigMode] = None
        self._current_environment: Optional[str] = None
        self._config_hash: Optional[str] = None

        # Hot-reload components
        self._file_observer: Optional[Observer] = None
        self._change_callbacks: List[
            Callable[[Dict[str, Any], ConfigChangeEvent], None]
        ] = []
        self._reload_lock = threading.Lock()

        # Initialize
        self._validate_config_directory()
        self._setup_hot_reload_directories()

        if not WATCHDOG_AVAILABLE and enable_hot_reload:
            logger.warning("Watchdog not available - hot-reload functionality disabled")

    def _setup_hot_reload_directories(self):
        """Create necessary directories for hot-reload functionality"""
        backup_dir = Path(self.paths.hot_reload_backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        log_file = Path(self.paths.change_log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    def add_change_callback(
        self, callback: Callable[[Dict[str, Any], ConfigChangeEvent], None]
    ):
        """Add a callback to be called when configuration changes"""
        self._change_callbacks.append(callback)

    def remove_change_callback(
        self, callback: Callable[[Dict[str, Any], ConfigChangeEvent], None]
    ):
        """Remove a configuration change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

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

    def _compute_config_hash(self, config: Dict[str, Any]) -> str:
        """Compute hash of configuration for change detection"""
        import hashlib

        config_str = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def _backup_config(self, config: Dict[str, Any], reason: str = "manual_backup"):
        """Create a backup of the current configuration"""
        try:
            backup_dir = Path(self.paths.hot_reload_backup_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"config_backup_{timestamp}_{reason}.json"

            with open(backup_file, "w") as f:
                json.dump(config, f, indent=2, default=str)

            logger.info(f"Configuration backed up to: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")

    def _log_config_change(
        self, event: ConfigChangeEvent, success: bool = True, error: str = None
    ):
        """Log configuration change events"""
        try:
            log_file = Path(self.paths.change_log_file)
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "file_path": event.file_path,
                "change_type": event.change_type,
                "success": success,
                "error": error,
                "config_hash": self._config_hash,
            }

            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Failed to log config change: {e}")

    def _on_config_file_changed(self, event: ConfigChangeEvent):
        """Handle configuration file change events"""
        logger.info(f"Configuration file changed: {event}")

        with self._reload_lock:
            try:
                # Only reload if we have a current configuration loaded
                if self._current_config is None:
                    logger.debug("No current configuration to reload")
                    return

                # Backup current config before reloading
                self._backup_config(
                    self._current_config, f"before_reload_{event.change_type}"
                )

                # Reload configuration
                new_config = self.load_configuration(
                    self._current_mode, self._current_environment, force_reload=True
                )

                # Check if configuration actually changed
                new_hash = self._compute_config_hash(new_config)
                if new_hash == self._config_hash:
                    logger.debug("Configuration unchanged after file modification")
                    return

                # Update cached configuration
                old_config = self._current_config.copy()
                self._current_config = new_config
                self._config_hash = new_hash

                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        callback(new_config, event)
                    except Exception as e:
                        logger.error(f"Configuration change callback failed: {e}")

                self._log_config_change(event, success=True)
                logger.info("Configuration reloaded successfully")

            except Exception as e:
                error_msg = f"Failed to reload configuration: {e}"
                logger.error(error_msg)
                self._log_config_change(event, success=False, error=str(e))

    def start_hot_reload(self):
        """Start the file watcher for hot-reload functionality"""
        if not self.enable_hot_reload:
            logger.info("Hot-reload is disabled")
            return

        if self._file_observer is not None:
            logger.warning("Hot-reload already started")
            return

        try:
            self._file_observer = Observer()
            event_handler = ConfigFileWatcher(
                callback=self._on_config_file_changed,
                patterns=["*.yaml", "*.yml", "*.json"],
            )

            self._file_observer.schedule(
                event_handler, str(self.config_dir), recursive=True
            )

            self._file_observer.start()
            logger.info(f"Hot-reload started for directory: {self.config_dir}")

        except Exception as e:
            logger.error(f"Failed to start hot-reload: {e}")

    def stop_hot_reload(self):
        """Stop the file watcher"""
        if self._file_observer is None:
            return

        try:
            self._file_observer.stop()
            self._file_observer.join(timeout=5)
            self._file_observer = None
            logger.info("Hot-reload stopped")
        except Exception as e:
            logger.error(f"Error stopping hot-reload: {e}")

    def __del__(self):
        """Cleanup file watcher on destruction"""
        self.stop_hot_reload()

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
        self,
        mode: ConfigMode,
        environment: Optional[str] = None,
        force_reload: bool = False,
    ) -> Dict[str, Any]:
        """
        Load complete configuration for the specified mode

        Args:
            mode: Configuration mode (research/compliance/development)
            environment: Optional environment name (dev/staging/prod)
            force_reload: Force reload even if configuration is cached

        Returns:
            Complete merged configuration dictionary
        """
        # Return cached configuration if available and not forcing reload
        if (
            not force_reload
            and self._current_config is not None
            and self._current_mode == mode
            and self._current_environment == environment
        ):
            logger.debug(f"Returning cached configuration for mode: {mode.value}")
            return self._current_config

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

        # Cache the loaded configuration
        self._current_config = config
        self._current_mode = mode
        self._current_environment = environment
        self._config_hash = self._compute_config_hash(config)

        # Start hot-reload if this is the first configuration load
        if self.enable_hot_reload and self._file_observer is None:
            self.start_hot_reload()

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
            "scraper_settings": {
                "headless": config.get("scraper", {})
                .get("browser", {})
                .get("headless"),
                "min_delay": config.get("scraper", {})
                .get("timing", {})
                .get("min_delay_seconds"),
                "max_delay": config.get("scraper", {})
                .get("timing", {})
                .get("max_delay_seconds"),
                "hot_reload_enabled": config.get("config_management", {})
                .get("hot_reload", {})
                .get("enabled", False),
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
            "file_paths": config.get("file_paths", {}),
            "runtime_info": {
                "config_hash": self._config_hash,
                "hot_reload_active": self._file_observer is not None,
                "cache_status": (
                    "cached" if self._current_config is not None else "not_cached"
                ),
            },
        }

        return summary

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'scraper.timing.min_delay_seconds')"""
        if self._current_config is None:
            logger.warning("No configuration loaded")
            return default

        keys = key_path.split(".")
        value = self._current_config

        try:
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except Exception as e:
            logger.error(f"Error getting config value '{key_path}': {e}")
            return default

    def update_config_value(
        self, key_path: str, new_value: Any, persist: bool = False
    ) -> bool:
        """Update a configuration value using dot notation"""
        if self._current_config is None:
            logger.error("No configuration loaded")
            return False

        keys = key_path.split(".")
        config = self._current_config

        try:
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]

            # Set the value
            config[keys[-1]] = new_value

            # Update hash
            self._config_hash = self._compute_config_hash(self._current_config)

            # Optionally persist to file
            if persist:
                self._persist_config_change(key_path, new_value)

            logger.info(f"Configuration value updated: {key_path} = {new_value}")
            return True

        except Exception as e:
            logger.error(f"Error updating config value '{key_path}': {e}")
            return False

    def _persist_config_change(self, key_path: str, new_value: Any):
        """Persist a configuration change to the local config file"""
        try:
            local_config_path = self.config_dir / self.paths.local_config

            # Load existing local config or create new
            if local_config_path.exists():
                local_config = self._load_yaml_file(local_config_path)
            else:
                local_config = {}

            # Set the value in local config
            keys = key_path.split(".")
            config = local_config

            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]

            config[keys[-1]] = new_value

            # Write back to file
            with open(local_config_path, "w") as f:
                yaml.dump(local_config, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration change persisted to: {local_config_path}")

        except Exception as e:
            logger.error(f"Failed to persist configuration change: {e}")


# Global configuration loader instance for shared use
_global_config_loader: Optional[EnhancedConfigurationLoader] = None


def get_config_loader(
    config_dir: str = "config", enable_hot_reload: bool = True
) -> EnhancedConfigurationLoader:
    """Get or create a global configuration loader instance"""
    global _global_config_loader

    if _global_config_loader is None:
        _global_config_loader = EnhancedConfigurationLoader(
            config_dir, enable_hot_reload
        )

    return _global_config_loader


def load_config(
    mode: Union[str, ConfigMode],
    environment: Optional[str] = None,
    config_dir: str = "config",
    enable_hot_reload: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to load configuration

    Args:
        mode: Configuration mode (research/compliance/development)
        environment: Optional environment name
        config_dir: Configuration directory path
        enable_hot_reload: Enable hot-reloading capabilities

    Returns:
        Complete configuration dictionary
    """
    if isinstance(mode, str):
        mode = ConfigMode(mode.lower())

    loader = get_config_loader(config_dir, enable_hot_reload)
    config = loader.load_configuration(mode, environment)

    # Validate configuration
    if not loader.validate_configuration(config, mode):
        raise ValueError(f"Configuration validation failed for mode: {mode.value}")

    return config


def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a configuration value from the global config loader"""
    global _global_config_loader
    if _global_config_loader is None:
        logger.warning("No global configuration loader available")
        return default
    return _global_config_loader.get_config_value(key_path, default)


def update_config_value(key_path: str, new_value: Any, persist: bool = False) -> bool:
    """Update a configuration value in the global config loader"""
    global _global_config_loader
    if _global_config_loader is None:
        logger.error("No global configuration loader available")
        return False
    return _global_config_loader.update_config_value(key_path, new_value, persist)


def add_config_change_callback(
    callback: Callable[[Dict[str, Any], ConfigChangeEvent], None],
):
    """Add a callback for configuration changes"""
    global _global_config_loader
    if _global_config_loader is not None:
        _global_config_loader.add_change_callback(callback)
    else:
        logger.warning(
            "No global configuration loader available for callback registration"
        )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    def config_change_handler(config: Dict[str, Any], event: ConfigChangeEvent):
        """Example configuration change handler"""
        print(f"Configuration changed: {event}")
        print(f"New app name: {config.get('app', {}).get('name', 'unknown')}")

    # Test loading research configuration with hot-reload
    try:
        loader = get_config_loader(enable_hot_reload=True)
        loader.add_change_callback(config_change_handler)

        research_config = load_config(ConfigMode.RESEARCH, enable_hot_reload=True)
        print("Research configuration loaded successfully")

        summary = loader.get_config_summary(research_config)
        print(f"Research config summary: {summary}")

        # Test configuration value access
        min_delay = get_config_value("scraper.timing.min_delay_seconds", 30)
        print(f"Current min delay: {min_delay} seconds")

        # Test configuration update
        if update_config_value("scraper.timing.min_delay_seconds", 45):
            print("Configuration updated successfully")

        print("Hot-reload is active. Modify configuration files to test...")
        print("Press Ctrl+C to exit")

        # Keep running to test hot-reload
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping hot-reload...")
            loader.stop_hot_reload()

    except Exception as e:
        print(f"Error in configuration testing: {e}")
        import traceback

        traceback.print_exc()
