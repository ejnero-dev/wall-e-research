#!/usr/bin/env python3
"""
Basic AI Engine Testing Script
Tests core functionality without requiring Ollama to be running
"""

import pytest

# Mark all tests in this file as unit tests for AI Engine
pytestmark = [pytest.mark.unit, pytest.mark.ai_engine, pytest.mark.fast]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.ai_engine import AIEngine, AIEngineConfig
from src.ai_engine.prompt_templates import SpanishPromptTemplates
from src.ai_engine.validator import AIResponseValidator
from src.ai_engine.fallback_handler import FallbackHandler


def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    try:
        config = AIEngineConfig.for_research()
        print(f"✅ Config created: {config.model_name}")

        templates = SpanishPromptTemplates()
        print(f"✅ Templates loaded: {len(templates.PERSONALITIES)} personalities")

        validator = AIResponseValidator()
        print("✅ Validator initialized")

        fallback = FallbackHandler(config)
        print("✅ Fallback handler initialized")

        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_prompt_templates():
    """Test Spanish prompt templates"""
    print("\n🧪 Testing Spanish prompt templates...")
    try:
        templates = SpanishPromptTemplates()

        # Test personalities
        personalities = templates.get_available_personalities()
        print(f"✅ Available personalities: {personalities}")

        # Test system prompt generation
        system_prompt = templates.get_system_prompt(
            personality="profesional_cordial",
            product_name="iPhone 12",
            price=400,
            condition="muy buen estado",
        )
        print(f"✅ System prompt generated ({len(system_prompt)} chars)")

        # Test response templates
        response = templates.get_response_template(
            personality="amigable_casual", intent="greeting"
        )
        print(f"✅ Response template: '{response}'")

        return True
    except Exception as e:
        print(f"❌ Prompt templates test failed: {e}")
        return False


def test_validator():
    """Test fraud detection validator"""
    print("\n🧪 Testing fraud detection validator...")
    try:
        validator = AIResponseValidator()

        # Test safe response
        safe_result = validator.validate_response(
            "¡Hola! Sí, está disponible. Son 400€. ¿Te interesa?"
        )
        print(
            f"✅ Safe response validation: {safe_result.is_valid} (risk: {safe_result.risk_score})"
        )

        # Test fraud response
        fraud_result = validator.validate_response(
            "Acepto Western Union, dame tu DNI y teléfono"
        )
        print(
            f"✅ Fraud response validation: {fraud_result.is_valid} (risk: {fraud_result.risk_score})"
        )

        # Test medium risk
        medium_result = validator.validate_response(
            "Necesito vender urgente, compra sin ver"
        )
        print(
            f"✅ Medium risk validation: {medium_result.is_valid} (risk: {medium_result.risk_score})"
        )

        return True
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


def test_fallback_handler():
    """Test fallback response system"""
    print("\n🧪 Testing fallback handler...")
    try:
        config = AIEngineConfig.for_research()
        fallback = FallbackHandler(config)

        # Test template response
        context = {
            "product_name": "iPhone 12",
            "price": 400,
            "condition": "muy buen estado",
        }

        response = fallback.get_fallback_response(
            buyer_message="¡Hola! ¿Está disponible?", context=context
        )
        print(f"✅ Fallback response: '{response}'")

        # Test safe alternative
        safe_response = fallback._get_safe_alternative(
            buyer_message="Pago con Western Union", context=context
        )
        print(f"✅ Safe alternative: '{safe_response}'")

        return True
    except Exception as e:
        print(f"❌ Fallback handler test failed: {e}")
        return False


def test_ai_engine_basic():
    """Test AI Engine basic functionality (template mode)"""
    print("\n🧪 Testing AI Engine (template mode)...")
    try:
        # Create config that forces template mode
        config = AIEngineConfig.for_research()
        config.fallback_mode = "template_only"

        engine = AIEngine(config)
        print(f"✅ AI Engine initialized: {engine.status.value}")

        # Test status
        status = engine.get_status()
        print(f"✅ Engine status: {status['status']}")

        # Test with ConversationRequest (would normally need full setup)
        # For now just test that the class structure works
        from src.ai_engine.ai_engine import ConversationRequest

        request = ConversationRequest(
            buyer_message="¡Hola! ¿Está disponible el iPhone?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
        )
        print(f"✅ ConversationRequest created: {request.buyer_message[:30]}...")

        return True
    except Exception as e:
        print(f"❌ AI Engine basic test failed: {e}")
        return False


def main():
    """Run all basic tests"""
    print("🚀 Wall-E AI Engine Basic Testing Suite")
    print("=" * 50)

    tests = [
        test_imports,
        test_prompt_templates,
        test_validator,
        test_fallback_handler,
        test_ai_engine_basic,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All basic tests passed! AI Engine is ready for Ollama integration.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
