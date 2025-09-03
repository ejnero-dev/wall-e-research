"""
AI Engine for Wall-E Wallapop Bot

This module provides AI-powered conversation generation with fraud detection
and fallback mechanisms for natural Spanish conversations.
"""

from .ai_engine import AIEngine
from .llm_manager import LLMManager
from .prompt_templates import SpanishPromptTemplates
from .response_generator import AIResponseGenerator
from .validator import AIResponseValidator
from .fallback_handler import FallbackHandler
from .config import AIEngineConfig

__all__ = [
    "AIEngine",
    "LLMManager",
    "SpanishPromptTemplates",
    "AIResponseGenerator",
    "AIResponseValidator",
    "FallbackHandler",
    "AIEngineConfig",
]

__version__ = "1.0.0"
