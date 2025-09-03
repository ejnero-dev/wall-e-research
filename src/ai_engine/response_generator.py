"""
AI Response Generator with Validation
Generates natural Spanish responses with validation and fallback
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio

from .llm_manager import LLMManager, LLMResponse
from .validator import AIResponseValidator, ValidationResult
from .prompt_templates import SpanishPromptTemplates
from .config import AIEngineConfig


@dataclass
class GenerationRequest:
    """Request for response generation"""

    buyer_message: str
    conversation_context: Dict
    personality: str = "profesional_cordial"
    max_retries: int = 3
    require_validation: bool = True


@dataclass
class GenerationResult:
    """Result of response generation"""

    response: str
    source: str  # 'ai_generation', 'fallback_template', 'safe_alternative'
    validation_result: Optional[ValidationResult]
    generation_time: float
    retries_used: int
    success: bool
    error: Optional[str] = None


class AIResponseGenerator:
    """Advanced response generator with validation and fallback"""

    def __init__(self, config: AIEngineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.llm_manager = LLMManager(config)
        self.validator = AIResponseValidator(config.__dict__)
        self.prompt_templates = SpanishPromptTemplates()

        # Performance tracking
        self.generation_stats = {
            "total_requests": 0,
            "ai_successes": 0,
            "validation_failures": 0,
            "fallback_uses": 0,
            "total_generation_time": 0.0,
        }

    def generate_response(self, request: GenerationRequest) -> GenerationResult:
        """Generate validated response with fallback"""

        start_time = time.time()
        self.generation_stats["total_requests"] += 1

        # Extract context
        context = request.conversation_context
        buyer_message = request.buyer_message
        personality = request.personality

        # Attempt AI generation with retries
        for attempt in range(request.max_retries):
            try:
                # Generate AI response
                ai_result = self._generate_ai_response(
                    buyer_message=buyer_message,
                    context=context,
                    personality=personality,
                )

                if not ai_result.success:
                    self.logger.warning(
                        f"AI generation failed (attempt {attempt + 1}): {ai_result.error}"
                    )
                    continue

                # Validate response
                if request.require_validation:
                    validation_result = self.validator.validate_response(
                        ai_result.text, context
                    )

                    if validation_result.is_valid:
                        # Success!
                        self.generation_stats["ai_successes"] += 1
                        generation_time = time.time() - start_time
                        self.generation_stats[
                            "total_generation_time"
                        ] += generation_time

                        return GenerationResult(
                            response=ai_result.text,
                            source="ai_generation",
                            validation_result=validation_result,
                            generation_time=generation_time,
                            retries_used=attempt + 1,
                            success=True,
                        )
                    else:
                        # Validation failed
                        self.generation_stats["validation_failures"] += 1
                        self.logger.warning(
                            f"AI response validation failed (attempt {attempt + 1}): "
                            f"Risk score {validation_result.risk_score}, "
                            f"Issues: {validation_result.issues}"
                        )

                        # Try different temperature for retry
                        if attempt < request.max_retries - 1:
                            self.logger.info("Retrying with adjusted parameters...")
                            continue
                else:
                    # Skip validation
                    generation_time = time.time() - start_time
                    return GenerationResult(
                        response=ai_result.text,
                        source="ai_generation",
                        validation_result=None,
                        generation_time=generation_time,
                        retries_used=attempt + 1,
                        success=True,
                    )

            except Exception as e:
                self.logger.error(
                    f"Error in AI generation (attempt {attempt + 1}): {e}"
                )
                continue

        # AI generation failed, use fallback
        return self._use_fallback(request, start_time)

    def _generate_ai_response(
        self,
        buyer_message: str,
        context: Dict,
        personality: str,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Generate AI response using LLM"""

        # Extract context information
        product_name = context.get("product_name", "producto")
        price = context.get("price", 100)
        condition = context.get("condition", "buen estado")
        location = context.get("location", "Madrid")
        conversation_history = context.get("conversation_history", [])
        buyer_name = context.get("buyer_name", "comprador")
        buyer_profile = context.get("buyer_profile")

        # Generate conversation context
        conversation_context = self.prompt_templates.get_conversation_context_prompt(
            buyer_name=buyer_name,
            conversation_history=conversation_history,
            buyer_profile=buyer_profile,
        )

        # Generate system prompt
        system_prompt = self.prompt_templates.get_system_prompt(
            personality=personality,
            product_name=product_name,
            price=price,
            condition=condition,
            location=location,
            conversation_context=conversation_context,
        )

        # Create user prompt
        user_prompt = f'MENSAJE DEL COMPRADOR: "{buyer_message}"\n\nResponde de forma natural y segura:'

        # Generate response
        return self.llm_manager.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    def _use_fallback(
        self, request: GenerationRequest, start_time: float
    ) -> GenerationResult:
        """Use fallback when AI generation fails"""

        self.generation_stats["fallback_uses"] += 1
        generation_time = time.time() - start_time

        # Analyze buyer message to determine intent
        buyer_intent = self._analyze_buyer_intent(request.buyer_message)

        # Get appropriate template response
        fallback_response = self.prompt_templates.get_response_template(
            personality=request.personality,
            intent=buyer_intent,
            **request.conversation_context,
        )

        # Create validation result for fallback
        validation_result = ValidationResult(
            is_valid=True,
            risk_score=0,
            risk_level=self.validator._get_risk_level(0),
            issues=[],
            blocked_patterns=[],
            source="fallback_template",
        )

        self.logger.info(f"Used fallback template for intent: {buyer_intent}")

        return GenerationResult(
            response=fallback_response,
            source="fallback_template",
            validation_result=validation_result,
            generation_time=generation_time,
            retries_used=request.max_retries,
            success=True,
        )

    def _analyze_buyer_intent(self, message: str) -> str:
        """Simple intent analysis for fallback"""
        message_lower = message.lower()

        # Greeting patterns
        if any(
            word in message_lower for word in ["hola", "buenas", "buenos", "hey", "hi"]
        ):
            return "greeting"

        # Price inquiry patterns
        if any(
            word in message_lower for word in ["precio", "vale", "cuesta", "euro", "€"]
        ):
            return "price_inquiry"

        # Negotiation patterns
        if any(
            word in message_lower
            for word in ["acepta", "aceptas", "cambio", "intercambio", "negocio"]
        ):
            return "negotiation"

        # Availability patterns
        if any(word in message_lower for word in ["disponible", "libre", "vendido"]):
            return "availability"

        # Meeting patterns
        if any(
            word in message_lower
            for word in ["quedar", "venir", "recoger", "cuando", "donde"]
        ):
            return "meeting"

        return "general"

    async def generate_response_async(
        self, request: GenerationRequest
    ) -> GenerationResult:
        """Async version of generate_response with optimized concurrency"""

        # Use LLM manager's async method directly for better performance
        if hasattr(self.llm_manager, "generate_response_async"):
            # Direct async path for better concurrency
            start_time = time.time()
            self.generation_stats["total_requests"] += 1

            # Extract context
            context = request.conversation_context
            buyer_message = request.buyer_message
            personality = request.personality

            # Attempt AI generation with retries
            for attempt in range(request.max_retries):
                try:
                    # Generate AI response using async method
                    ai_result = await self._generate_ai_response_async(
                        buyer_message=buyer_message,
                        context=context,
                        personality=personality,
                    )

                    if not ai_result.success:
                        self.logger.warning(
                            f"AI generation failed (attempt {attempt + 1}): {ai_result.error}"
                        )
                        continue

                    # Validate response
                    if request.require_validation:
                        validation_result = self.validator.validate_response(
                            ai_result.text, context
                        )

                        if validation_result.is_valid:
                            # Success!
                            self.generation_stats["ai_successes"] += 1
                            generation_time = time.time() - start_time
                            self.generation_stats[
                                "total_generation_time"
                            ] += generation_time

                            return GenerationResult(
                                response=ai_result.text,
                                source="ai_generation",
                                validation_result=validation_result,
                                generation_time=generation_time,
                                retries_used=attempt + 1,
                                success=True,
                            )
                        else:
                            # Validation failed
                            self.generation_stats["validation_failures"] += 1
                            self.logger.warning(
                                f"AI response validation failed (attempt {attempt + 1}): "
                                f"Risk score {validation_result.risk_score}, "
                                f"Issues: {validation_result.issues}"
                            )
                            continue
                    else:
                        # Skip validation
                        generation_time = time.time() - start_time
                        return GenerationResult(
                            response=ai_result.text,
                            source="ai_generation",
                            validation_result=None,
                            generation_time=generation_time,
                            retries_used=attempt + 1,
                            success=True,
                        )

                except Exception as e:
                    self.logger.error(
                        f"Error in AI generation (attempt {attempt + 1}): {e}"
                    )
                    continue

            # AI generation failed, use fallback
            return await self._use_fallback_async(request, start_time)
        else:
            # Fallback to sync version in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.generate_response, request)

    async def _generate_ai_response_async(
        self,
        buyer_message: str,
        context: Dict,
        personality: str,
        temperature: Optional[float] = None,
    ):
        """Generate AI response using async LLM"""

        # Extract context information
        product_name = context.get("product_name", "producto")
        price = context.get("price", 100)
        condition = context.get("condition", "buen estado")
        location = context.get("location", "Madrid")
        conversation_history = context.get("conversation_history", [])
        buyer_name = context.get("buyer_name", "comprador")
        buyer_profile = context.get("buyer_profile")

        # Generate conversation context
        conversation_context = self.prompt_templates.get_conversation_context_prompt(
            buyer_name=buyer_name,
            conversation_history=conversation_history,
            buyer_profile=buyer_profile,
        )

        # Generate system prompt
        system_prompt = self.prompt_templates.get_system_prompt(
            personality=personality,
            product_name=product_name,
            price=price,
            condition=condition,
            location=location,
            conversation_context=conversation_context,
        )

        # Create user prompt
        user_prompt = f'MENSAJE DEL COMPRADOR: "{buyer_message}"\n\nResponde de forma natural y segura:'

        # Generate response using async method
        return await self.llm_manager.generate_response_async(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    async def _use_fallback_async(
        self, request: GenerationRequest, start_time: float
    ) -> GenerationResult:
        """Use fallback when AI generation fails (async version)"""

        self.generation_stats["fallback_uses"] += 1
        generation_time = time.time() - start_time

        # Run fallback in executor to avoid blocking
        loop = asyncio.get_event_loop()

        def fallback_task():
            # Analyze buyer message to determine intent
            buyer_intent = self._analyze_buyer_intent(request.buyer_message)

            # Get appropriate template response
            fallback_response = self.prompt_templates.get_response_template(
                personality=request.personality,
                intent=buyer_intent,
                **request.conversation_context,
            )

            return fallback_response, buyer_intent

        fallback_response, buyer_intent = await loop.run_in_executor(
            None, fallback_task
        )

        # Create validation result for fallback
        validation_result = ValidationResult(
            is_valid=True,
            risk_score=0,
            risk_level=self.validator._get_risk_level(0),
            issues=[],
            blocked_patterns=[],
            source="fallback_template",
        )

        self.logger.info(f"Used fallback template for intent: {buyer_intent}")

        return GenerationResult(
            response=fallback_response,
            source="fallback_template",
            validation_result=validation_result,
            generation_time=generation_time,
            retries_used=request.max_retries,
            success=True,
        )

    def test_generation(
        self, test_message: str = "¡Hola! ¿Está disponible?"
    ) -> GenerationResult:
        """Test generation with default context"""

        test_context = {
            "product_name": "iPhone 12",
            "price": 400,
            "condition": "muy buen estado",
            "location": "Madrid",
            "conversation_history": [],
            "buyer_name": "TestBuyer",
            "buyer_profile": None,
            "conversation_state": "INICIAL",
            "buyer_intent": "greeting",
        }

        request = GenerationRequest(
            buyer_message=test_message,
            conversation_context=test_context,
            personality="profesional_cordial",
        )

        return self.generate_response(request)

    def get_performance_stats(self) -> Dict:
        """Get generation performance statistics"""
        total_requests = max(self.generation_stats["total_requests"], 1)

        return {
            **self.generation_stats,
            "ai_success_rate": self.generation_stats["ai_successes"] / total_requests,
            "validation_failure_rate": self.generation_stats["validation_failures"]
            / total_requests,
            "fallback_rate": self.generation_stats["fallback_uses"] / total_requests,
            "average_generation_time": self.generation_stats["total_generation_time"]
            / total_requests,
            "llm_stats": self.llm_manager.get_performance_stats(),
        }

    def is_ready(self) -> bool:
        """Check if generator is ready for use"""
        return self.llm_manager.is_available()

    def cleanup(self):
        """Cleanup resources"""
        self.llm_manager.cleanup()
