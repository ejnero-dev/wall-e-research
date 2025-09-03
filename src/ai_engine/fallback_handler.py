"""
Fallback Handler for AI Engine
Manages fallback strategies when AI generation fails or is blocked
"""

import logging
import json
import random
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .validator import ValidationResult, RiskLevel


class FallbackMode(Enum):
    """Fallback operation modes"""

    AUTO = "auto"  # Intelligent fallback decision
    AI_ONLY = "ai_only"  # Only AI, fail if not possible
    TEMPLATE_ONLY = "template_only"  # Only templates
    HYBRID = "hybrid"  # Mix AI and templates


@dataclass
class FallbackRule:
    """Rule for fallback decision"""

    condition: str  # When to apply
    action: str  # What action to take
    priority: int  # Rule priority
    params: Dict[str, Any]  # Additional parameters


class FallbackHandler:
    """Advanced fallback system for AI responses"""

    def __init__(self, config, templates_path: Optional[str] = None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.mode = FallbackMode(config.fallback_mode)
        self.fallback_threshold = config.fallback_threshold

        # Load template responses
        self.templates = self._load_templates(templates_path)

        # Fallback statistics
        self.fallback_stats = {
            "total_fallbacks": 0,
            "template_uses": 0,
            "safe_alternatives": 0,
            "ai_retries": 0,
            "mode_switches": 0,
        }

        # Define fallback rules
        self.fallback_rules = self._define_fallback_rules()

    def _load_templates(self, templates_path: Optional[str]) -> Dict:
        """Load template responses from JSON"""

        if templates_path is None:
            # Try to find templates in standard location
            current_dir = Path(__file__).parent.parent
            templates_path = current_dir / "templates" / "responses.json"

        try:
            if Path(templates_path).exists():
                with open(templates_path, "r", encoding="utf-8") as f:
                    templates = json.load(f)
                    self.logger.info(f"Loaded templates from {templates_path}")
                    return templates
            else:
                self.logger.warning(f"Templates file not found: {templates_path}")
                return self._get_default_templates()

        except Exception as e:
            self.logger.error(f"Failed to load templates: {e}")
            return self._get_default_templates()

    def _get_default_templates(self) -> Dict:
        """Get default template responses"""
        return {
            "greetings": [
                "¡Hola! Sí, está disponible. ¿Te interesa?",
                "Buenas. Efectivamente, sigue disponible. ¿En qué puedo ayudarte?",
                "Hola. Sí está libre. ¿Tienes alguna pregunta?",
            ],
            "price_inquiry": [
                "El precio es {price}€ tal como aparece en el anuncio.",
                "Son {price}€ según las características del producto.",
                "Vale {price}€, precio fijo.",
            ],
            "negotiation": [
                "El precio está bastante ajustado para lo que es.",
                "Es un precio justo considerando el estado del producto.",
                "Podríamos hablar del precio si hay interés serio.",
            ],
            "availability": [
                "Sí, está disponible.",
                "Efectivamente, sigue libre.",
                "Correcto, aún no está vendido.",
            ],
            "meeting": [
                "Perfecto. ¿Cuándo te vendría bien quedar?",
                "Podemos quedar cuando te vaya mejor.",
                "Sin problema. ¿Qué día y hora te va bien?",
            ],
            "general": [
                "Gracias por tu interés. ¿En qué puedo ayudarte?",
                "Por supuesto. ¿Qué necesitas saber?",
                "Claro. ¿Tienes alguna pregunta específica?",
            ],
            "safe_responses": [
                "Gracias por tu mensaje. ¿Puedes ser más específico?",
                "Perfecto. ¿En qué puedo ayudarte exactamente?",
                "Claro. ¿Qué información necesitas?",
            ],
        }

    def _define_fallback_rules(self) -> List[FallbackRule]:
        """Define fallback decision rules"""
        return [
            FallbackRule(
                condition="critical_fraud_detected",
                action="use_safe_alternative",
                priority=1,
                params={"force_safe": True},
            ),
            FallbackRule(
                condition="high_risk_score",
                action="use_template",
                priority=2,
                params={"risk_threshold": 75},
            ),
            FallbackRule(
                condition="validation_failed_multiple",
                action="use_template",
                priority=3,
                params={"retry_limit": 3},
            ),
            FallbackRule(
                condition="llm_unavailable",
                action="use_template",
                priority=4,
                params={},
            ),
            FallbackRule(
                condition="response_too_slow",
                action="use_template",
                priority=5,
                params={"time_threshold": 5.0},
            ),
        ]

    def should_fallback(
        self,
        validation_result: Optional[ValidationResult],
        generation_error: Optional[str],
        generation_time: float,
        retry_count: int,
    ) -> bool:
        """Determine if fallback should be used"""

        # Check each fallback rule
        for rule in sorted(self.fallback_rules, key=lambda r: r.priority):
            if self._check_rule_condition(
                rule, validation_result, generation_error, generation_time, retry_count
            ):
                self.logger.info(f"Fallback triggered by rule: {rule.condition}")
                return True

        return False

    def _check_rule_condition(
        self,
        rule: FallbackRule,
        validation_result: Optional[ValidationResult],
        generation_error: Optional[str],
        generation_time: float,
        retry_count: int,
    ) -> bool:
        """Check if rule condition is met"""

        if rule.condition == "critical_fraud_detected":
            return (
                validation_result and validation_result.risk_level == RiskLevel.CRITICAL
            )

        elif rule.condition == "high_risk_score":
            threshold = rule.params.get("risk_threshold", 75)
            return validation_result and validation_result.risk_score >= threshold

        elif rule.condition == "validation_failed_multiple":
            retry_limit = rule.params.get("retry_limit", 3)
            return retry_count >= retry_limit

        elif rule.condition == "llm_unavailable":
            return generation_error and "not available" in generation_error.lower()

        elif rule.condition == "response_too_slow":
            threshold = rule.params.get("time_threshold", 5.0)
            return generation_time > threshold

        return False

    def get_fallback_response(
        self,
        buyer_message: str,
        context: Dict,
        validation_result: Optional[ValidationResult] = None,
        fallback_reason: str = "general",
    ) -> str:
        """Get appropriate fallback response"""

        self.fallback_stats["total_fallbacks"] += 1

        # Determine fallback strategy based on validation result
        if validation_result and validation_result.risk_level == RiskLevel.CRITICAL:
            return self._get_safe_alternative(buyer_message, context)

        # Use template-based fallback
        return self._get_template_response(buyer_message, context)

    def _get_safe_alternative(self, buyer_message: str, context: Dict) -> str:
        """Get ultra-safe response for high-risk situations"""

        self.fallback_stats["safe_alternatives"] += 1

        safe_responses = self.templates.get(
            "safe_responses",
            [
                "Gracias por tu mensaje. ¿Puedes ser más específico?",
                "Perfecto. ¿En qué puedo ayudarte exactamente?",
                "Claro. ¿Qué información necesitas?",
            ],
        )

        return random.choice(safe_responses)

    def _get_template_response(self, buyer_message: str, context: Dict) -> str:
        """Get template-based response"""

        self.fallback_stats["template_uses"] += 1

        # Analyze message to determine intent
        intent = self._analyze_intent(buyer_message)

        # Get templates for intent
        intent_templates = self.templates.get(intent, self.templates.get("general", []))

        if not intent_templates:
            intent_templates = ["Gracias por tu interés. ¿En qué puedo ayudarte?"]

        # Select random template
        template = random.choice(intent_templates)

        # Fill template with context
        return self._fill_template(template, context)

    def _analyze_intent(self, message: str) -> str:
        """Analyze buyer message intent for template selection"""

        message_lower = message.lower()

        # Intent patterns
        intent_patterns = {
            "greetings": ["hola", "buenas", "buenos", "hey", "hi"],
            "price_inquiry": ["precio", "vale", "cuesta", "euro", "€"],
            "negotiation": [
                "acepta",
                "aceptas",
                "cambio",
                "intercambio",
                "negocio",
                "rebaja",
            ],
            "availability": ["disponible", "libre", "vendido"],
            "meeting": ["quedar", "venir", "recoger", "cuando", "donde", "hora"],
        }

        # Check patterns
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent

        return "general"

    def _fill_template(self, template: str, context: Dict) -> str:
        """Fill template with context variables"""

        try:
            # Common template variables
            template_vars = {
                "price": context.get("price", "100"),
                "product_name": context.get("product_name", "producto"),
                "condition": context.get("condition", "buen estado"),
                "location": context.get("location", "Madrid"),
            }

            return template.format(**template_vars)

        except KeyError as e:
            self.logger.warning(f"Template variable missing: {e}")
            return template
        except Exception as e:
            self.logger.error(f"Template filling failed: {e}")
            return "Gracias por tu interés. ¿En qué puedo ayudarte?"

    def adapt_mode(self, performance_metrics: Dict):
        """Adapt fallback mode based on performance"""

        ai_success_rate = performance_metrics.get("ai_success_rate", 0)
        validation_failure_rate = performance_metrics.get("validation_failure_rate", 0)
        average_response_time = performance_metrics.get("average_generation_time", 0)

        old_mode = self.mode

        # Decision logic for mode adaptation
        if ai_success_rate < 0.3:  # Less than 30% AI success
            self.mode = FallbackMode.TEMPLATE_ONLY

        elif validation_failure_rate > 0.5:  # More than 50% validation failures
            self.mode = FallbackMode.HYBRID

        elif average_response_time > 5.0:  # Too slow
            self.mode = FallbackMode.TEMPLATE_ONLY

        elif ai_success_rate > 0.8 and validation_failure_rate < 0.1:
            self.mode = FallbackMode.AUTO

        if old_mode != self.mode:
            self.fallback_stats["mode_switches"] += 1
            self.logger.info(
                f"Fallback mode changed from {old_mode.value} to {self.mode.value}"
            )

    def get_fallback_stats(self) -> Dict:
        """Get fallback usage statistics"""
        total_fallbacks = max(self.fallback_stats["total_fallbacks"], 1)

        return {
            **self.fallback_stats,
            "template_use_rate": self.fallback_stats["template_uses"] / total_fallbacks,
            "safe_alternative_rate": self.fallback_stats["safe_alternatives"]
            / total_fallbacks,
            "current_mode": self.mode.value,
        }

    def is_template_mode(self) -> bool:
        """Check if currently in template-only mode"""
        return self.mode == FallbackMode.TEMPLATE_ONLY

    def is_ai_enabled(self) -> bool:
        """Check if AI generation is enabled"""
        return self.mode in [
            FallbackMode.AUTO,
            FallbackMode.AI_ONLY,
            FallbackMode.HYBRID,
        ]
