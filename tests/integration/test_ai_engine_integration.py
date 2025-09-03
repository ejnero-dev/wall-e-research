#!/usr/bin/env python3
"""
AI Engine Integration Testing
Tests integration with existing Wall-E conversation engine
"""

import pytest

# Mark all tests in this file as integration tests for AI Engine
pytestmark = [pytest.mark.integration, pytest.mark.ai_engine]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.ai_engine import AIEngine, AIEngineConfig
from src.ai_engine.ai_engine import ConversationRequest, ConversationResponse


def test_conversation_scenarios():
    """Test various conversation scenarios"""
    print("🧪 Testing conversation scenarios...")

    # Initialize AI Engine in template mode
    config = AIEngineConfig.for_research()
    config.fallback_mode = "template_only"  # Ensure templates work without Ollama

    engine = AIEngine(config)

    scenarios = [
        {
            "name": "Saludo inicial",
            "message": "¡Hola! ¿Está disponible el iPhone?",
            "expected_keywords": ["disponible", "hola", "interesa"],
        },
        {
            "name": "Consulta de precio",
            "message": "¿Cuánto vale?",
            "expected_keywords": ["precio", "€", "vale"],
        },
        {
            "name": "Negociación",
            "message": "¿Aceptas 350€?",
            "expected_keywords": ["precio", "acepta", "justo"],
        },
        {
            "name": "Coordinación",
            "message": "¿Cuándo podemos quedar?",
            "expected_keywords": ["quedar", "cuando", "hora"],
        },
        {
            "name": "Fraude - Western Union",
            "message": "¿Aceptas Western Union?",
            "expected_keywords": ["efectivo", "bizum", "persona"],
        },
    ]

    results = []

    for scenario in scenarios:
        print(f"\n📝 Testing: {scenario['name']}")

        request = ConversationRequest(
            buyer_message=scenario["message"],
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
            conversation_history=[],
            personality="profesional_cordial",
        )

        try:
            response = engine.generate_response(request)

            print(f"✅ Response: '{response.response_text}'")
            print(
                f"📊 Source: {response.source}, Risk: {response.risk_score}, Confidence: {response.confidence:.2f}"
            )

            # Check if any expected keywords are present
            response_lower = response.response_text.lower()
            keywords_found = [
                kw for kw in scenario["expected_keywords"] if kw in response_lower
            ]

            results.append(
                {
                    "scenario": scenario["name"],
                    "success": response.success,
                    "keywords_found": keywords_found,
                    "response": response.response_text,
                    "risk_score": response.risk_score,
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(
                {"scenario": scenario["name"], "success": False, "error": str(e)}
            )

    return results


def test_fraud_detection():
    """Test fraud detection with various patterns"""
    print("\n🛡️ Testing fraud detection...")

    config = AIEngineConfig.for_research()
    engine = AIEngine(config)

    fraud_tests = [
        {
            "message": "Pago con Western Union",
            "should_block": True,
            "description": "Western Union payment",
        },
        {
            "message": "¿Tu DNI y teléfono?",
            "should_block": True,
            "description": "Personal info request",
        },
        {
            "message": "Envío sin ver, pago adelantado",
            "should_block": True,
            "description": "Payment before delivery",
        },
        {
            "message": "¿Cuándo podemos quedar en persona?",
            "should_block": False,
            "description": "Legitimate meeting request",
        },
        {
            "message": "Acepto efectivo en mano",
            "should_block": False,
            "description": "Safe payment method",
        },
    ]

    fraud_results = []

    for test in fraud_tests:
        print(f"\n🔍 Testing: {test['description']}")

        request = ConversationRequest(
            buyer_message=test["message"],
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
        )

        try:
            response = engine.generate_response(request)

            is_blocked = response.risk_score >= 70 or not response.validation_passed
            correct_detection = is_blocked == test["should_block"]

            print(f"Message: '{test['message']}'")
            print(f"Risk Score: {response.risk_score}")
            print(f"Blocked: {is_blocked}, Should Block: {test['should_block']}")
            print(f"Detection: {'✅ Correct' if correct_detection else '❌ Incorrect'}")

            fraud_results.append(
                {
                    "test": test["description"],
                    "correct": correct_detection,
                    "risk_score": response.risk_score,
                    "blocked": is_blocked,
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            fraud_results.append(
                {"test": test["description"], "correct": False, "error": str(e)}
            )

    return fraud_results


def test_performance():
    """Test basic performance metrics"""
    print("\n⚡ Testing performance...")

    config = AIEngineConfig.for_research()
    engine = AIEngine(config)

    import time

    # Single request test
    start_time = time.time()

    request = ConversationRequest(
        buyer_message="¡Hola! ¿Está disponible?",
        buyer_name="TestBuyer",
        product_name="iPhone 12",
        price=400,
    )

    response = engine.generate_response(request)
    response_time = time.time() - start_time

    print(f"Single request time: {response_time:.3f}s")

    # Multiple requests test
    start_time = time.time()
    successful_requests = 0

    for i in range(5):
        try:
            response = engine.generate_response(request)
            if response.success:
                successful_requests += 1
        except Exception as e:
            print(f"Request {i} failed: {e}")

    total_time = time.time() - start_time
    avg_time = total_time / 5

    print(f"5 requests total time: {total_time:.3f}s")
    print(f"Average time per request: {avg_time:.3f}s")
    print(f"Successful requests: {successful_requests}/5")

    # Get engine stats
    stats = engine.get_performance_stats()
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Template response rate: {stats['template_response_rate']:.2%}")

    return {
        "single_request_time": response_time,
        "average_request_time": avg_time,
        "success_rate": successful_requests / 5,
        "engine_stats": stats,
    }


def main():
    """Run integration tests"""
    print("🚀 Wall-E AI Engine Integration Testing")
    print("=" * 60)

    # Test conversation scenarios
    scenario_results = test_conversation_scenarios()

    # Test fraud detection
    fraud_results = test_fraud_detection()

    # Test performance
    performance_results = test_performance()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    # Scenario results
    successful_scenarios = sum(1 for r in scenario_results if r.get("success", False))
    print(
        f"Conversation scenarios: {successful_scenarios}/{len(scenario_results)} passed"
    )

    # Fraud detection results
    correct_fraud_detection = sum(1 for r in fraud_results if r.get("correct", False))
    print(f"Fraud detection: {correct_fraud_detection}/{len(fraud_results)} correct")

    # Performance results
    avg_time = performance_results["average_request_time"]
    print(f"Average response time: {avg_time:.3f}s")

    target_time = 3.0  # 3 second target
    time_status = "✅ GOOD" if avg_time < target_time else "⚠️ SLOW"
    print(f"Performance target (<{target_time}s): {time_status}")

    # Overall status
    all_tests_passed = (
        successful_scenarios == len(scenario_results)
        and correct_fraud_detection == len(fraud_results)
        and avg_time < target_time
    )

    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED! AI Engine integration successful.")
        print("🚀 Ready for production deployment.")
    else:
        print("\n⚠️ Some tests failed. Review results above.")

    print("\n💡 Next steps:")
    print("1. Install Ollama: python scripts/setup_ollama.py")
    print("2. Test with real LLM: python scripts/test_ai_engine_basic.py")
    print("3. Integrate with existing Wall-E conversation engine")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
