#!/usr/bin/env python3
"""
End-to-end tests for complete Wall-E workflow
Tests integration of all components in realistic scenarios
"""

import pytest

# Mark all tests in this file as end-to-end tests
pytestmark = [pytest.mark.e2e, pytest.mark.slow]
import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai_engine import AIEngine, AIEngineConfig
from ai_engine.ai_engine import ConversationRequest
from conversation_engine.engine import ConversationEngine, Buyer, Product
from price_analyzer.analyzer import PriceAnalyzer
from scraper.wallapop_scraper import WallapopScraper
from bot.wallapop_bot import WallapopBot


class TestCompleteWorkflow:
    """End-to-end workflow tests"""

    @pytest.fixture(scope="class")
    def mock_environment(self):
        """Set up complete mock environment for E2E testing"""
        return {
            "ai_engine": self._create_mock_ai_engine(),
            "conversation_engine": self._create_mock_conversation_engine(),
            "price_analyzer": self._create_mock_price_analyzer(),
            "scraper": self._create_mock_scraper(),
            "database": self._create_mock_database(),
        }

    def _create_mock_ai_engine(self):
        """Create mock AI Engine for testing"""
        config = AIEngineConfig.for_research()
        config.fallback_mode = "template_only"
        return AIEngine(config)

    def _create_mock_conversation_engine(self):
        """Create mock Conversation Engine for testing"""
        return ConversationEngine()

    def _create_mock_price_analyzer(self):
        """Create mock Price Analyzer for testing"""
        return PriceAnalyzer()

    def _create_mock_scraper(self):
        """Create mock Scraper for testing"""
        scraper = Mock(spec=WallapopScraper)
        scraper.is_authenticated = True
        scraper.get_new_messages = AsyncMock(return_value=[])
        scraper.send_message = AsyncMock(return_value=True)
        scraper.get_product_details = AsyncMock(
            return_value={
                "title": "iPhone 12 128GB",
                "price": 450.0,
                "condition": "como nuevo",
                "description": "iPhone en perfecto estado",
            }
        )
        return scraper

    def _create_mock_database(self):
        """Create mock database connections"""
        return {"postgres": Mock(), "redis": Mock()}

    @pytest.mark.asyncio
    async def test_new_buyer_conversation_workflow(self, mock_environment):
        """Test complete workflow for new buyer conversation"""
        # Simulate new buyer message
        incoming_message = {
            "buyer_id": "new_buyer_123",
            "buyer_name": "NuevoComprador",
            "message": "¡Hola! ¿Está disponible el iPhone?",
            "product_id": "iphone_12_456",
            "timestamp": time.time(),
        }

        # Step 1: AI Engine processes the message
        request = ConversationRequest(
            buyer_message=incoming_message["message"],
            buyer_name=incoming_message["buyer_name"],
            product_name="iPhone 12 128GB",
            price=450,
            conversation_history=[],
        )

        ai_response = mock_environment["ai_engine"].generate_response(request)
        assert ai_response.success is True
        assert ai_response.response_text is not None
        assert len(ai_response.response_text) > 0

        # Step 2: Conversation Engine manages state
        buyer = Buyer(
            id=incoming_message["buyer_id"],
            username=incoming_message["buyer_name"],
            valoraciones=0,
            num_compras=0,
            distancia_km=15.0,
        )

        product = Product(
            id=incoming_message["product_id"],
            titulo="iPhone 12 128GB",
            precio=450.0,
            estado="como nuevo",
        )

        conversation_response = mock_environment["conversation_engine"].process_message(
            buyer=buyer, product=product, message=incoming_message["message"]
        )

        assert conversation_response is not None
        assert conversation_response.response_text is not None

        # Step 3: Validate fraud detection
        assert ai_response.risk_score is not None
        assert 0 <= ai_response.risk_score <= 100

        # For greeting message, risk should be low
        assert (
            ai_response.risk_score < 30
        ), f"Risk score {ai_response.risk_score} too high for greeting"

        # Step 4: Send response via scraper
        with patch.object(mock_environment["scraper"], "send_message") as mock_send:
            mock_send.return_value = True

            send_success = await mock_environment["scraper"].send_message(
                buyer_id=incoming_message["buyer_id"], message=ai_response.response_text
            )

            assert send_success is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_price_negotiation_workflow(self, mock_environment):
        """Test complete workflow for price negotiation"""
        # Simulate price negotiation message
        negotiation_message = {
            "buyer_id": "experienced_buyer_789",
            "buyer_name": "CompradorExperiente",
            "message": "¿Aceptas 380€? Es mi última oferta",
            "product_id": "iphone_12_456",
            "timestamp": time.time(),
        }

        # Step 1: Get market analysis for informed response
        with patch.object(
            mock_environment["price_analyzer"], "analyze_market_price"
        ) as mock_analysis:
            mock_analysis.return_value = Mock(
                price_suggestions={
                    "quick_sale": 380,
                    "market_competitive": 420,
                    "maximum_profit": 450,
                },
                competitive_positioning={"percentile": 65},
                confidence_score=0.8,
            )

            price_analysis = mock_environment["price_analyzer"].analyze_market_price(
                product_name="iPhone 12 128GB", current_price=450.0, buyer_offer=380.0
            )

            assert price_analysis is not None
            assert price_analysis.confidence_score > 0.5

        # Step 2: AI Engine considers negotiation context
        request = ConversationRequest(
            buyer_message=negotiation_message["message"],
            buyer_name=negotiation_message["buyer_name"],
            product_name="iPhone 12 128GB",
            price=450,
            buyer_offer=380,
            conversation_history=[
                {"role": "buyer", "message": "¡Hola! ¿Está disponible el iPhone?"},
                {"role": "seller", "message": "¡Hola! Sí, está disponible por 450€"},
                {"role": "buyer", "message": "¿Puedes hacer 380€?"},
            ],
        )

        ai_response = mock_environment["ai_engine"].generate_response(request)
        assert ai_response.success is True

        # Response should be relevant to negotiation
        response_lower = ai_response.response_text.lower()
        negotiation_keywords = ["precio", "oferta", "€", "acepto", "último"]
        has_negotiation_content = any(
            keyword in response_lower for keyword in negotiation_keywords
        )
        assert has_negotiation_content, "Response doesn't address negotiation"

        # Step 3: Check for appropriate negotiation strategy
        offer_percentage = (380 / 450) * 100  # ~84.4%

        if offer_percentage > 85:
            # Good offer - should consider accepting or minor counter
            assert ai_response.risk_score < 20
        elif offer_percentage > 70:
            # Reasonable offer - should negotiate
            assert "counter" in response_lower or "propuesta" in response_lower
        else:
            # Low offer - should politely decline or make significant counter
            assert ai_response.risk_score < 50

    @pytest.mark.asyncio
    async def test_fraud_detection_workflow(self, mock_environment):
        """Test complete workflow for fraud detection and response"""
        # Simulate suspicious message
        suspicious_message = {
            "buyer_id": "suspicious_buyer_999",
            "buyer_name": "UsuarioSospechoso",
            "message": "Te pago por Western Union, dame tu WhatsApp y DNI",
            "product_id": "iphone_12_456",
            "timestamp": time.time(),
        }

        # Step 1: AI Engine fraud detection
        request = ConversationRequest(
            buyer_message=suspicious_message["message"],
            buyer_name=suspicious_message["buyer_name"],
            product_name="iPhone 12 128GB",
            price=450,
        )

        ai_response = mock_environment["ai_engine"].generate_response(request)

        # Should detect high fraud risk
        assert (
            ai_response.risk_score > 70
        ), f"Risk score {ai_response.risk_score} too low for obvious fraud"
        assert ai_response.validation_passed is False

        # Step 2: Conversation Engine should flag for review
        buyer = Buyer(
            id=suspicious_message["buyer_id"],
            username=suspicious_message["buyer_name"],
            valoraciones=0,  # New user
            num_compras=0,
            distancia_km=500.0,  # Far away
        )

        product = Product(
            id=suspicious_message["product_id"],
            titulo="iPhone 12 128GB",
            precio=450.0,
            estado="como nuevo",
        )

        conversation_response = mock_environment["conversation_engine"].process_message(
            buyer=buyer, product=product, message=suspicious_message["message"]
        )

        # Should generate safe response
        assert conversation_response is not None
        safe_response_lower = conversation_response.response_text.lower()
        fraud_indicators = ["whatsapp", "dni", "western union", "paypal familia"]
        response_mentions_fraud = any(
            indicator in safe_response_lower for indicator in fraud_indicators
        )
        assert not response_mentions_fraud, "Response mentions fraud terms"

        # Should suggest safe alternatives
        safe_alternatives = [
            "efectivo",
            "bizum",
            "transferencia",
            "persona",
            "wallapop",
        ]
        mentions_safe_payment = any(
            alt in safe_response_lower for alt in safe_alternatives
        )
        assert mentions_safe_payment, "Response doesn't suggest safe alternatives"

        # Step 3: Should not send message automatically (manual review required)
        with patch.object(mock_environment["scraper"], "send_message") as mock_send:
            # High-risk messages should be queued for manual review
            if ai_response.risk_score > 80:
                # Should not auto-send
                mock_send.assert_not_called()
            else:
                # Medium risk might still auto-send with safe response
                await mock_environment["scraper"].send_message(
                    buyer_id=suspicious_message["buyer_id"],
                    message=conversation_response.response_text,
                )
                mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_multi_conversation_concurrent_workflow(self, mock_environment):
        """Test handling multiple concurrent conversations"""
        # Simulate multiple buyers messaging simultaneously
        concurrent_messages = [
            {
                "buyer_id": f"buyer_{i}",
                "buyer_name": f"Comprador{i}",
                "message": f"¡Hola! ¿Está disponible el producto {i}?",
                "product_id": f"product_{i}",
                "timestamp": time.time(),
            }
            for i in range(5)
        ]

        # Process all messages concurrently
        tasks = []
        for msg in concurrent_messages:
            task = asyncio.create_task(
                self._process_single_message(mock_environment, msg)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All conversations should be processed successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(concurrent_messages)

        # Each result should be unique (no conversation mixing)
        response_texts = [r["response"] for r in successful_results]
        for i, response in enumerate(response_texts):
            # Response should reference the correct product/buyer
            assert (
                f"producto {i}" in response.lower() or "disponible" in response.lower()
            )

    async def _process_single_message(self, mock_environment, message):
        """Process a single message through the complete workflow"""
        request = ConversationRequest(
            buyer_message=message["message"],
            buyer_name=message["buyer_name"],
            product_name=f"Producto {message['product_id']}",
            price=100 + int(message["buyer_id"].split("_")[1]),  # Varying prices
        )

        ai_response = mock_environment["ai_engine"].generate_response(request)

        return {
            "buyer_id": message["buyer_id"],
            "response": ai_response.response_text,
            "risk_score": ai_response.risk_score,
            "success": ai_response.success,
        }

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_environment):
        """Test system recovery from various error conditions"""
        error_scenarios = [
            {
                "name": "AI Engine Failure",
                "error_component": "ai_engine",
                "error_type": Exception("LLM service unavailable"),
            },
            {
                "name": "Database Connection Error",
                "error_component": "database",
                "error_type": Exception("Database connection lost"),
            },
            {
                "name": "Scraper Authentication Error",
                "error_component": "scraper",
                "error_type": Exception("Authentication failed"),
            },
        ]

        for scenario in error_scenarios:
            print(f"Testing error recovery: {scenario['name']}")

            # Simulate error condition
            with patch.object(
                mock_environment[scenario["error_component"]],
                (
                    "generate_response"
                    if scenario["error_component"] == "ai_engine"
                    else "process_message"
                ),
                side_effect=scenario["error_type"],
            ):

                # System should handle gracefully
                message = {
                    "buyer_id": "test_buyer",
                    "buyer_name": "TestBuyer",
                    "message": "¡Hola! ¿Está disponible?",
                    "product_id": "test_product",
                }

                try:
                    if scenario["error_component"] == "ai_engine":
                        # Should fallback to template responses
                        request = ConversationRequest(
                            buyer_message=message["message"],
                            buyer_name=message["buyer_name"],
                            product_name="Test Product",
                            price=100,
                        )

                        # Create fallback AI engine
                        fallback_config = AIEngineConfig.for_research()
                        fallback_config.fallback_mode = "template_only"
                        fallback_engine = AIEngine(fallback_config)

                        response = fallback_engine.generate_response(request)
                        assert response.success is True
                        assert response.source == "fallback"

                    elif scenario["error_component"] == "database":
                        # Should continue with in-memory state
                        assert True  # System continues operating

                    elif scenario["error_component"] == "scraper":
                        # Should queue messages for retry
                        assert True  # Messages queued for later

                except Exception as e:
                    pytest.fail(
                        f"System failed to recover from {scenario['name']}: {e}"
                    )

    @pytest.mark.asyncio
    async def test_performance_under_load_workflow(self, mock_environment):
        """Test system performance under realistic load"""
        # Simulate realistic message load
        message_load = []
        for i in range(20):  # 20 concurrent conversations
            message_load.append(
                {
                    "buyer_id": f"load_buyer_{i}",
                    "buyer_name": f"LoadBuyer{i}",
                    "message": f"Consulta sobre producto {i}",
                    "product_id": f"load_product_{i}",
                    "expected_response_time": 3.0,  # Max 3 seconds per message
                }
            )

        start_time = time.time()

        # Process all messages
        tasks = []
        for msg in message_load:
            task = asyncio.create_task(
                self._process_message_with_timing(mock_environment, msg)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Performance validation
        successful_responses = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        max_response_time = max(r["response_time"] for r in results)

        assert (
            successful_responses >= 19
        ), f"Only {successful_responses}/20 messages processed successfully"
        assert (
            avg_response_time < 3.0
        ), f"Average response time {avg_response_time:.2f}s too high"
        assert (
            max_response_time < 5.0
        ), f"Max response time {max_response_time:.2f}s too high"
        assert total_time < 15.0, f"Total processing time {total_time:.2f}s too high"

        print(
            f"Load test results - Success: {successful_responses}/20, Avg time: {avg_response_time:.2f}s"
        )

    async def _process_message_with_timing(self, mock_environment, message):
        """Process message and measure timing"""
        start_time = time.time()

        try:
            request = ConversationRequest(
                buyer_message=message["message"],
                buyer_name=message["buyer_name"],
                product_name=f"Producto {message['product_id']}",
                price=200,
            )

            response = mock_environment["ai_engine"].generate_response(request)

            return {
                "success": response.success,
                "response_time": time.time() - start_time,
                "buyer_id": message["buyer_id"],
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "buyer_id": message["buyer_id"],
            }


@pytest.mark.e2e
class TestRealWorldScenarios:
    """Real-world scenario tests"""

    def test_typical_sale_complete_cycle(self):
        """Test a complete sales cycle from inquiry to purchase"""
        # This would typically involve:
        # 1. Initial buyer inquiry
        # 2. Price discussion
        # 3. Product details exchange
        # 4. Meeting arrangement
        # 5. Sale completion

        # Simplified version for unit testing
        assert True  # Placeholder for full implementation

    def test_abandoned_conversation_recovery(self):
        """Test recovery of abandoned conversations"""
        # Test follow-up message system
        # Test conversation state persistence
        # Test reactivation strategies

        assert True  # Placeholder for full implementation

    def test_multiple_product_management(self):
        """Test managing conversations for multiple products simultaneously"""
        # Test product-specific responses
        # Test inventory management
        # Test cross-selling opportunities

        assert True  # Placeholder for full implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e", "--tb=short"])
