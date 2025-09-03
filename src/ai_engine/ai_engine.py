"""
Main AI Engine Orchestrator
Central coordinator for AI-powered conversation generation with validation and fallback
"""

import logging
import time
import asyncio
import gc
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import threading

from .config import AIEngineConfig
from .llm_manager import LLMManager
from .response_generator import AIResponseGenerator, GenerationRequest, GenerationResult
from .validator import AIResponseValidator, ValidationResult
from .fallback_handler import FallbackHandler, FallbackMode
from .prompt_templates import SpanishPromptTemplates
from .performance_monitor import (
    PerformanceMonitor,
    initialize_performance_monitor,
    get_performance_monitor,
)


class EngineStatus(Enum):
    """AI Engine status"""

    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ConversationRequest:
    """Request for conversation response"""

    buyer_message: str
    buyer_name: str
    product_name: str
    price: float
    conversation_history: List[Dict] = None
    buyer_profile: Optional[Dict] = None
    personality: str = "profesional_cordial"
    condition: str = "buen estado"
    location: str = "Madrid"
    require_validation: bool = True
    max_retries: int = 3

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


@dataclass
class ConversationResponse:
    """Response from AI Engine"""

    response_text: str
    source: str
    confidence: float
    generation_time: float
    validation_passed: bool
    risk_score: int
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None


class AIEngine:
    """Main AI Engine for natural Spanish conversation generation"""

    def __init__(self, config: Optional[AIEngineConfig] = None):
        # Configuration
        self.config = config or AIEngineConfig.for_research()
        self.logger = logging.getLogger(__name__)

        # Engine status
        self.status = EngineStatus.INITIALIZING
        self.initialization_time = None
        self.last_maintenance = time.time()

        # Core components
        self.response_generator = None
        self.validator = None
        self.fallback_handler = None

        # Performance tracking
        self.engine_stats = {
            "total_requests": 0,
            "successful_responses": 0,
            "ai_responses": 0,
            "template_responses": 0,
            "validation_blocks": 0,
            "total_response_time": 0.0,
            "uptime_start": time.time(),
        }

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all AI Engine components"""
        try:
            self.logger.info("Initializing AI Engine components...")

            # Initialize response generator (includes LLM manager)
            self.response_generator = AIResponseGenerator(self.config)

            # Initialize validator
            self.validator = AIResponseValidator(self.config.__dict__)

            # Initialize fallback handler
            self.fallback_handler = FallbackHandler(self.config)

            # Check if LLM is available
            if self.response_generator.is_ready():
                self.status = EngineStatus.READY
                self.logger.info("AI Engine initialized successfully with LLM support")
            else:
                self.logger.warning(
                    "AI Engine initialized in template-only mode (LLM not available)"
                )
                self.fallback_handler.mode = FallbackMode.TEMPLATE_ONLY
                self.status = EngineStatus.READY

            self.initialization_time = time.time()

        except Exception as e:
            self.logger.error(f"Failed to initialize AI Engine: {e}")
            self.status = EngineStatus.ERROR
            raise

    def generate_response(self, request: ConversationRequest) -> ConversationResponse:
        """Generate response for buyer message"""

        if self.status != EngineStatus.READY:
            return ConversationResponse(
                response_text="Sistema temporalmente no disponible. Inténtalo más tarde.",
                source="error_fallback",
                confidence=0.0,
                generation_time=0.0,
                validation_passed=False,
                risk_score=0,
                metadata={"error": f"Engine status: {self.status.value}"},
                success=False,
                error=f"Engine not ready: {self.status.value}",
            )

        start_time = time.time()
        self.status = EngineStatus.BUSY
        self.engine_stats["total_requests"] += 1

        try:
            # Prepare generation request
            generation_request = self._prepare_generation_request(request)

            # Generate response
            if (
                self.fallback_handler.is_ai_enabled()
                and self.response_generator.is_ready()
            ):
                result = self.response_generator.generate_response(generation_request)
            else:
                # Use fallback only
                result = self._generate_fallback_only(generation_request)

            # Create response
            response = self._create_conversation_response(result, start_time)

            # Update statistics
            self._update_stats(response)

            # Adaptive mode adjustment
            self._adapt_performance()

            return response

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._create_error_response(str(e), start_time)

        finally:
            self.status = EngineStatus.READY

    def _prepare_generation_request(
        self, request: ConversationRequest
    ) -> GenerationRequest:
        """Prepare internal generation request"""

        # Build context
        context = {
            "product_name": request.product_name,
            "price": request.price,
            "condition": request.condition,
            "location": request.location,
            "conversation_history": request.conversation_history,
            "buyer_name": request.buyer_name,
            "buyer_profile": request.buyer_profile,
            "conversation_state": self._determine_conversation_state(
                request.conversation_history
            ),
            "buyer_intent": self._analyze_buyer_intent(request.buyer_message),
        }

        return GenerationRequest(
            buyer_message=request.buyer_message,
            conversation_context=context,
            personality=request.personality,
            max_retries=request.max_retries,
            require_validation=request.require_validation,
        )

    def _determine_conversation_state(self, history: List[Dict]) -> str:
        """Determine current conversation state"""
        if not history:
            return "INICIAL"

        # Simple state determination based on history length
        if len(history) < 3:
            return "INICIAL"
        elif len(history) < 6:
            return "EXPLORANDO"
        elif len(history) < 10:
            return "NEGOCIANDO"
        else:
            return "COORDINANDO"

    def _analyze_buyer_intent(self, message: str) -> str:
        """Quick intent analysis"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["precio", "vale", "cuesta"]):
            return "precio"
        elif any(word in message_lower for word in ["disponible", "libre"]):
            return "disponibilidad"
        elif any(word in message_lower for word in ["quedar", "recoger", "venir"]):
            return "coordinacion"
        elif any(word in message_lower for word in ["hola", "buenas", "buenos"]):
            return "saludo"
        else:
            return "general"

    def _generate_fallback_only(self, request: GenerationRequest) -> GenerationResult:
        """Generate response using only fallback templates"""

        start_time = time.time()

        # Get fallback response
        response = self.fallback_handler.get_fallback_response(
            buyer_message=request.buyer_message,
            context=request.conversation_context,
            fallback_reason="template_only_mode",
        )

        generation_time = time.time() - start_time

        return GenerationResult(
            response=response,
            source="fallback_template",
            validation_result=None,
            generation_time=generation_time,
            retries_used=0,
            success=True,
        )

    def _create_conversation_response(
        self, result: GenerationResult, start_time: float
    ) -> ConversationResponse:
        """Create final conversation response"""

        total_time = time.time() - start_time

        # Calculate confidence based on source and validation
        confidence = self._calculate_confidence(result)

        # Extract validation info
        validation_passed = (
            result.validation_result.is_valid if result.validation_result else True
        )
        risk_score = (
            result.validation_result.risk_score if result.validation_result else 0
        )

        # Build metadata
        metadata = {
            "source": result.source,
            "retries_used": result.retries_used,
            "generation_time": result.generation_time,
            "total_time": total_time,
        }

        if result.validation_result:
            metadata.update(
                {
                    "validation_issues": result.validation_result.issues,
                    "blocked_patterns": result.validation_result.blocked_patterns,
                    "risk_level": result.validation_result.risk_level.name,
                }
            )

        return ConversationResponse(
            response_text=result.response,
            source=result.source,
            confidence=confidence,
            generation_time=total_time,
            validation_passed=validation_passed,
            risk_score=risk_score,
            metadata=metadata,
            success=result.success,
            error=result.error,
        )

    def _calculate_confidence(self, result: GenerationResult) -> float:
        """Calculate confidence score for response"""

        if not result.success:
            return 0.0

        base_confidence = {
            "ai_generation": 0.9,
            "fallback_template": 0.7,
            "safe_alternative": 0.5,
        }.get(result.source, 0.3)

        # Adjust based on validation
        if result.validation_result:
            risk_penalty = result.validation_result.risk_score / 100.0
            base_confidence *= 1.0 - risk_penalty * 0.5

        # Adjust based on retries
        retry_penalty = (result.retries_used - 1) * 0.1
        base_confidence *= 1.0 - retry_penalty

        return max(0.0, min(1.0, base_confidence))

    def _create_error_response(
        self, error: str, start_time: float
    ) -> ConversationResponse:
        """Create error response"""

        safe_response = "Gracias por tu mensaje. ¿Puedes contarme más específicamente qué necesitas?"

        return ConversationResponse(
            response_text=safe_response,
            source="error_fallback",
            confidence=0.1,
            generation_time=time.time() - start_time,
            validation_passed=True,
            risk_score=0,
            metadata={"error": error},
            success=False,
            error=error,
        )

    def _update_stats(self, response: ConversationResponse):
        """Update engine statistics"""

        if response.success:
            self.engine_stats["successful_responses"] += 1

        if response.source == "ai_generation":
            self.engine_stats["ai_responses"] += 1
        elif "template" in response.source:
            self.engine_stats["template_responses"] += 1

        if not response.validation_passed:
            self.engine_stats["validation_blocks"] += 1

        self.engine_stats["total_response_time"] += response.generation_time

    def _adapt_performance(self):
        """Adapt engine performance based on metrics"""

        # Get performance metrics
        performance_metrics = self.get_performance_stats()

        # Adapt fallback mode
        self.fallback_handler.adapt_mode(performance_metrics)

        # Periodic maintenance
        if time.time() - self.last_maintenance > 3600:  # Every hour
            self._perform_maintenance()

    def _perform_maintenance(self):
        """Perform periodic maintenance"""

        self.logger.info("Performing AI Engine maintenance...")

        # Reset some counters to prevent overflow
        if self.engine_stats["total_requests"] > 10000:
            self.engine_stats = {
                k: int(v * 0.9) if isinstance(v, int) else v
                for k, v in self.engine_stats.items()
            }

        self.last_maintenance = time.time()

    async def generate_response_async(
        self, request: ConversationRequest
    ) -> ConversationResponse:
        """Async version of generate_response"""

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_response, request)

    def test_engine(self) -> Dict[str, Any]:
        """Test all engine components"""

        test_results = {
            "engine_status": self.status.value,
            "llm_available": False,
            "validator_working": False,
            "fallback_working": False,
            "test_response": None,
            "errors": [],
        }

        try:
            # Test LLM availability
            if self.response_generator and self.response_generator.is_ready():
                test_results["llm_available"] = True

            # Test validator
            self.validator.validate_response("Test response", {})
            test_results["validator_working"] = True

            # Test fallback
            fallback_test = self.fallback_handler.get_fallback_response("test", {})
            test_results["fallback_working"] = len(fallback_test) > 0

            # Test full pipeline
            test_request = ConversationRequest(
                buyer_message="¡Hola! ¿Está disponible?",
                buyer_name="TestBuyer",
                product_name="iPhone Test",
                price=100,
            )

            test_response = self.generate_response(test_request)
            test_results["test_response"] = {
                "success": test_response.success,
                "source": test_response.source,
                "confidence": test_response.confidence,
                "response_length": len(test_response.response_text),
            }

        except Exception as e:
            test_results["errors"].append(str(e))

        return test_results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""

        total_requests = max(self.engine_stats["total_requests"], 1)
        uptime = time.time() - self.engine_stats["uptime_start"]

        base_stats = {
            "engine_status": self.status.value,
            "uptime_seconds": uptime,
            "total_requests": self.engine_stats["total_requests"],
            "success_rate": self.engine_stats["successful_responses"] / total_requests,
            "ai_response_rate": self.engine_stats["ai_responses"] / total_requests,
            "template_response_rate": self.engine_stats["template_responses"]
            / total_requests,
            "validation_block_rate": self.engine_stats["validation_blocks"]
            / total_requests,
            "average_response_time": self.engine_stats["total_response_time"]
            / total_requests,
            "requests_per_second": total_requests / max(uptime, 1),
        }

        # Add component stats
        if self.response_generator:
            base_stats["generation_stats"] = (
                self.response_generator.get_performance_stats()
            )

        if self.fallback_handler:
            base_stats["fallback_stats"] = self.fallback_handler.get_fallback_stats()

        return base_stats

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""

        return {
            "status": self.status.value,
            "initialized_at": self.initialization_time,
            "llm_available": (
                self.response_generator.is_ready() if self.response_generator else False
            ),
            "fallback_mode": (
                self.fallback_handler.mode.value if self.fallback_handler else None
            ),
            "config": asdict(self.config),
            "component_status": {
                "response_generator": self.response_generator is not None,
                "validator": self.validator is not None,
                "fallback_handler": self.fallback_handler is not None,
            },
        }

    def shutdown(self):
        """Gracefully shutdown the engine"""

        self.logger.info("Shutting down AI Engine...")
        self.status = EngineStatus.MAINTENANCE

        if self.response_generator:
            self.response_generator.cleanup()

        self.logger.info("AI Engine shutdown complete")
