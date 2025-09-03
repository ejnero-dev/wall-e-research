"""
AI Response Validator with Anti-Fraud Detection
Advanced validation pipeline for AI-generated responses in Spanish
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import spacy

# Load Spanish model
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    logging.warning(
        "Spanish spacy model not found. Install with: python -m spacy download es_core_news_sm"
    )
    nlp = None


class RiskLevel(Enum):
    """Risk levels for validation"""

    SAFE = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    CRITICAL = 100


@dataclass
class ValidationResult:
    """Result of validation process"""

    is_valid: bool
    risk_score: int
    risk_level: RiskLevel
    issues: List[str]
    blocked_patterns: List[str]
    source: str = "ai_generation"

    def __bool__(self):
        return self.is_valid


class AIResponseValidator:
    """Advanced validator for AI responses with fraud detection"""

    # Critical fraud patterns - instant block
    CRITICAL_FRAUD_PATTERNS = [
        r"\bwestern\s+union\b",
        r"\bpaypal\s+familia\b",
        r"\bpaypal\s+amigos\b",
        r"\bcrypto\b",
        r"\bbitcoin\b",
        r"\bethers?\b",
        r"\bdogecoin\b",
        r"\bmonero\b",
        r"\btether\b",
        r"\busdt\b",
        r"\benvío\s+primero\b",
        r"\bpago\s+adelantado\b",
        r"\btransferencia\s+internacional\b",
        r"\bmoneygram\b",
        r"\bwu\b",  # Western Union abbreviation
    ]

    # High risk patterns
    HIGH_RISK_PATTERNS = [
        r"\b\d{8}[a-z]\b",  # DNI pattern
        r"\b\d{9}\b",  # Phone number pattern
        r"@[a-z0-9.-]+\.[a-z]{2,}",  # Email pattern
        r"https?://[^\s]+",  # URL pattern
        r"\bmi\s+teléfono\b",
        r"\bmi\s+email\b",
        r"\bmi\s+dirección\b",
        r"\burgen[te]\b",
        r"\bmuy\s+urgente\b",
        r"\bahora\s+mismo\b",
        r"\bante[rs]\s+de\b",
    ]

    # Medium risk patterns
    MEDIUM_RISK_PATTERNS = [
        r"\bsin\s+ver\b",
        r"\bno\s+hace\s+falta\s+ver\b",
        r"\bcompro\s+sin\s+ver\b",
        r"\bpago\s+sin\s+ver\b",
        r"\bendeudam\w+",
        r"\bproblemas?\s+económicos?\b",
        r"\bnecesito\s+dinero\b",
        r"\bvendo\s+rápido\b",
    ]

    # Allowed safe payment methods
    SAFE_PAYMENT_METHODS = [
        "efectivo",
        "cash",
        "bizum",
        "en mano",
        "en persona",
        "transferencia bancaria",
        "ingreso bancario",
    ]

    # Prohibited payment methods
    PROHIBITED_PAYMENTS = [
        "western union",
        "paypal familia",
        "paypal amigos",
        "crypto",
        "bitcoin",
        "ethereum",
        "dogecoin",
        "monero",
        "tether",
        "usdt",
        "moneygram",
        "pago adelantado",
    ]

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.fraud_threshold = self.config.get("fraud_threshold", 70)
        self.strict_mode = self.config.get("enable_strict_validation", True)
        self.logger = logging.getLogger(__name__)

    def validate_response(
        self, response: str, context: Optional[Dict] = None
    ) -> ValidationResult:
        """Comprehensive validation of AI response"""

        if not response or not response.strip():
            return ValidationResult(
                is_valid=False,
                risk_score=100,
                risk_level=RiskLevel.CRITICAL,
                issues=["Empty response"],
                blocked_patterns=[],
            )

        issues = []
        blocked_patterns = []
        risk_score = 0

        # 1. Critical fraud pattern detection
        critical_score, critical_issues, critical_patterns = (
            self._check_critical_patterns(response)
        )
        risk_score += critical_score
        issues.extend(critical_issues)
        blocked_patterns.extend(critical_patterns)

        # 2. High risk pattern detection
        high_score, high_issues, high_patterns = self._check_high_risk_patterns(
            response
        )
        risk_score += high_score
        issues.extend(high_issues)
        blocked_patterns.extend(high_patterns)

        # 3. Medium risk pattern detection
        medium_score, medium_issues, medium_patterns = self._check_medium_risk_patterns(
            response
        )
        risk_score += medium_score
        issues.extend(medium_issues)
        blocked_patterns.extend(medium_patterns)

        # 4. Context validation
        context_score, context_issues = self._validate_context(response, context)
        risk_score += context_score
        issues.extend(context_issues)

        # 5. Language and format validation
        format_score, format_issues = self._validate_format(response)
        risk_score += format_score
        issues.extend(format_issues)

        # 6. NLP-based validation
        nlp_score, nlp_issues = self._validate_with_nlp(response)
        risk_score += nlp_score
        issues.extend(nlp_issues)

        # Determine risk level
        risk_level = self._get_risk_level(risk_score)

        # Determine if valid
        is_valid = self._is_response_valid(risk_score, risk_level, blocked_patterns)

        return ValidationResult(
            is_valid=is_valid,
            risk_score=min(risk_score, 100),
            risk_level=risk_level,
            issues=issues,
            blocked_patterns=blocked_patterns,
        )

    def _check_critical_patterns(
        self, response: str
    ) -> Tuple[int, List[str], List[str]]:
        """Check for critical fraud patterns - instant block"""
        response_lower = response.lower()
        issues = []
        patterns = []
        score = 0

        for pattern in self.CRITICAL_FRAUD_PATTERNS:
            if re.search(pattern, response_lower, re.IGNORECASE):
                issues.append(f"Critical fraud pattern detected: {pattern}")
                patterns.append(pattern)
                score = 100  # Instant critical
                break

        return score, issues, patterns

    def _check_high_risk_patterns(
        self, response: str
    ) -> Tuple[int, List[str], List[str]]:
        """Check for high risk patterns"""
        response_lower = response.lower()
        issues = []
        patterns = []
        score = 0

        for pattern in self.HIGH_RISK_PATTERNS:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                issues.append(f"High risk pattern: {pattern}")
                patterns.append(pattern)
                score += 30  # High risk adds significant score

        return min(score, 75), issues, patterns

    def _check_medium_risk_patterns(
        self, response: str
    ) -> Tuple[int, List[str], List[str]]:
        """Check for medium risk patterns"""
        response_lower = response.lower()
        issues = []
        patterns = []
        score = 0

        for pattern in self.MEDIUM_RISK_PATTERNS:
            if re.search(pattern, response_lower, re.IGNORECASE):
                issues.append(f"Medium risk pattern: {pattern}")
                patterns.append(pattern)
                score += 15  # Medium risk

        return min(score, 50), issues, patterns

    def _validate_context(
        self, response: str, context: Optional[Dict]
    ) -> Tuple[int, List[str]]:
        """Validate response against conversation context"""
        issues = []
        score = 0

        if not context:
            return 0, []

        # Check if response is appropriate for context
        conversation_state = context.get("conversation_state", "")
        buyer_intent = context.get("buyer_intent", "")

        # Contextual validation rules
        if conversation_state == "INICIAL" and "precio" in response.lower():
            if "disponible" not in response.lower():
                issues.append("Missing availability confirmation in initial response")
                score += 10

        if buyer_intent == "precio" and not any(
            word in response.lower()
            for word in ["€", "euro", "precio", "vale", "cuesta"]
        ):
            issues.append("Price inquiry not properly addressed")
            score += 15

        return score, issues

    def _validate_format(self, response: str) -> Tuple[int, List[str]]:
        """Validate response format and structure"""
        issues = []
        score = 0

        # Length validation
        if len(response) > 500:
            issues.append("Response too long")
            score += 20

        if len(response) < 10:
            issues.append("Response too short")
            score += 15

        # Check for excessive punctuation
        if response.count("!") > 3:
            issues.append("Excessive exclamation marks")
            score += 10

        if response.count("?") > 2:
            issues.append("Too many question marks")
            score += 5

        # Check for appropriate Spanish
        if not re.search(r"[aeiouáéíóú]", response.lower()):
            issues.append("Does not appear to be Spanish text")
            score += 30

        return score, issues

    def _validate_with_nlp(self, response: str) -> Tuple[int, List[str]]:
        """Use spaCy for advanced NLP validation"""
        issues = []
        score = 0

        if not nlp:
            return 0, []

        try:
            doc = nlp(response)

            # Check for entities that might be problematic
            for ent in doc.ents:
                if (
                    ent.label_ == "PER" and len(ent.text) > 15
                ):  # Long person names might be suspicious
                    issues.append(f"Suspicious person entity: {ent.text}")
                    score += 10

                if ent.label_ == "ORG" and ent.text.lower() in [
                    "western union",
                    "paypal",
                ]:
                    issues.append(f"Prohibited organization mentioned: {ent.text}")
                    score += 50

            # Sentiment analysis (basic)
            negative_words = ["malo", "terrible", "horrible", "odio", "estafa"]
            for word in negative_words:
                if word in response.lower():
                    issues.append("Negative sentiment detected")
                    score += 5
                    break

        except Exception as e:
            self.logger.warning(f"NLP validation failed: {e}")

        return score, issues

    def _get_risk_level(self, score: int) -> RiskLevel:
        """Determine risk level from score"""
        if score >= 100:
            return RiskLevel.CRITICAL
        elif score >= 75:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.MEDIUM
        elif score >= 25:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    def _is_response_valid(
        self, score: int, risk_level: RiskLevel, blocked_patterns: List[str]
    ) -> bool:
        """Determine if response is valid based on score and patterns"""

        # Always block critical patterns
        if blocked_patterns and any(
            pattern in self.CRITICAL_FRAUD_PATTERNS for pattern in blocked_patterns
        ):
            return False

        # Block based on threshold
        if score >= self.fraud_threshold:
            return False

        # In strict mode, be more restrictive
        if self.strict_mode and risk_level == RiskLevel.HIGH:
            return False

        return True

    def get_safe_alternative(
        self, blocked_response: str, context: Optional[Dict] = None
    ) -> str:
        """Generate safe alternative when response is blocked"""

        # Simple template-based safe responses
        safe_responses = [
            "Gracias por tu interés. ¿Puedes contarme más sobre lo que necesitas?",
            "Por supuesto. El producto está disponible. ¿Te gustaría saber algo específico?",
            "Hola. Sí, sigue disponible. ¿En qué puedo ayudarte?",
            "Perfecto. ¿Cuándo te vendría bien quedar para verlo?",
            "Claro. ¿Tienes alguna pregunta sobre el producto?",
        ]

        # Context-aware selection
        if context:
            buyer_intent = context.get("buyer_intent", "")
            if "precio" in buyer_intent:
                return "El precio está en el anuncio. ¿Te interesa el producto?"
            elif "disponible" in buyer_intent:
                return "Sí, está disponible. ¿Te gustaría saber algo más?"

        import random

        return random.choice(safe_responses)
