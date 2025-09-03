"""
Configuration for AI Engine
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import platform
import psutil


@dataclass
class AIEngineConfig:
    """Configuration for AI Engine components"""

    # LLM Configuration
    model_name: str = "phi3.5:3.8b-mini-instruct-q4_0"
    ollama_host: str = "http://localhost:11434"
    context_window: int = 128000
    temperature: float = 0.6
    max_tokens: int = 150
    timeout: int = 60

    # Performance Configuration
    max_retries: int = 3
    response_timeout: float = 3.0
    enable_caching: bool = True
    cache_ttl: int = 3600

    # Validation Configuration
    fraud_threshold: int = 70
    enable_strict_validation: bool = True
    allowed_risk_patterns: List[str] = None

    # Fallback Configuration
    fallback_mode: str = "auto"  # auto, ai_only, template_only, hybrid
    fallback_threshold: float = 0.5

    # Personalities
    default_personality: str = "profesional_cordial"
    enable_personality_adaptation: bool = True

    # Language Configuration
    language: str = "es"
    region: str = "ES"
    currency: str = "EUR"

    # Debug Configuration
    debug_mode: bool = False
    log_level: str = "INFO"
    save_prompts: bool = False

    def __post_init__(self):
        if self.allowed_risk_patterns is None:
            self.allowed_risk_patterns = []

        # Environment variable overrides
        self.model_name = os.getenv("AI_MODEL_NAME", self.model_name)
        self.ollama_host = os.getenv("OLLAMA_HOST", self.ollama_host)
        self.debug_mode = os.getenv("AI_DEBUG", "false").lower() == "true"

    @classmethod
    def for_hardware(cls, ram_gb: int) -> "AIEngineConfig":
        """Create configuration optimized for specific hardware"""
        if ram_gb >= 64:
            return cls(
                model_name="llama3.3:70b-instruct-q4_0", max_tokens=800, temperature=0.8
            )
        elif ram_gb >= 32:
            return cls(
                model_name="qwen2.5:14b-instruct-q4_0", max_tokens=600, temperature=0.75
            )
        elif ram_gb >= 16:
            return cls(
                model_name="llama3.2:11b-vision-instruct-q4_0",
                max_tokens=500,
                temperature=0.7,
            )
        else:
            return cls(
                model_name="phi3.5:3.8b-mini-instruct-q4_0",
                max_tokens=300,
                temperature=0.6,
            )

    @classmethod
    def for_compliance(cls) -> "AIEngineConfig":
        """Create configuration for compliance version"""
        return cls(
            fraud_threshold=50,
            enable_strict_validation=True,
            fallback_mode="hybrid",
            debug_mode=False,
            save_prompts=True,
        )

    @classmethod
    def for_research(cls) -> "AIEngineConfig":
        """Create configuration for research version"""
        return cls(
            fraud_threshold=70,
            enable_strict_validation=False,
            fallback_mode="auto",
            debug_mode=True,
            save_prompts=True,
        )

    def get_system_info(self) -> Dict:
        """Get system information for performance optimization"""
        return {
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage": psutil.disk_usage("/")._asdict(),
            "python_version": platform.python_version(),
        }

    def validate_config(self) -> List[str]:
        """Validate configuration and return warnings"""
        warnings = []

        system_info = self.get_system_info()
        available_ram_gb = system_info["memory_available_gb"]

        # Check memory requirements
        if self.memory_threshold_mb > available_ram_gb * 1024 * 0.9:
            warnings.append(
                f"Memory threshold ({self.memory_threshold_mb}MB) is very close to available RAM ({available_ram_gb:.1f}GB)"
            )

        # Check concurrency settings
        cpu_count = system_info["cpu_count"]
        if self.max_concurrent_requests > cpu_count * 4:
            warnings.append(
                f"Max concurrent requests ({self.max_concurrent_requests}) may be too high for {cpu_count} CPU cores"
            )

        # Check thread pool settings
        if self.thread_pool_size > cpu_count * 4:
            warnings.append(
                f"Thread pool size ({self.thread_pool_size}) may be excessive for {cpu_count} CPU cores"
            )

        return warnings
