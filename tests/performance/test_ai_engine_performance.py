#!/usr/bin/env python3
"""
Performance tests for AI Engine module
Tests response time, concurrent handling, and memory usage under load
"""

import pytest

# Mark all tests in this file as performance tests for AI Engine
pytestmark = [
    pytest.mark.performance,
    pytest.mark.ai_engine,
    pytest.mark.slow,
    pytest.mark.memory_intensive,
]
import asyncio
import time
import psutil
import sys
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai_engine import AIEngine, AIEngineConfig
from ai_engine.ai_engine import ConversationRequest, ConversationResponse


class TestAIEnginePerformance:
    """Performance test suite for AI Engine"""

    @pytest.fixture(scope="class")
    def ai_engine(self):
        """Create AI Engine instance for performance testing"""
        config = AIEngineConfig.for_research()
        config.fallback_mode = "template_only"  # Faster for performance tests
        return AIEngine(config)

    @pytest.fixture
    def sample_request(self):
        """Create sample conversation request"""
        return ConversationRequest(
            buyer_message="¡Hola! ¿Está disponible el iPhone?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
            conversation_history=[],
            personality="profesional_cordial",
        )

    def measure_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def test_single_request_response_time(self, ai_engine, sample_request):
        """Test single request response time - Target: <3s"""
        start_time = time.time()

        response = ai_engine.generate_response(sample_request)

        response_time = time.time() - start_time

        assert response.success is True
        assert (
            response_time < 3.0
        ), f"Response time {response_time:.2f}s exceeds 3s target"

        print(f"Single request response time: {response_time:.3f}s")

    def test_consecutive_requests_performance(self, ai_engine, sample_request):
        """Test consecutive requests performance - Target: consistent timing"""
        num_requests = 10
        response_times = []

        for i in range(num_requests):
            start_time = time.time()
            response = ai_engine.generate_response(sample_request)
            response_time = time.time() - start_time

            assert response.success is True
            response_times.append(response_time)

        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0

        assert (
            avg_time < 3.0
        ), f"Average response time {avg_time:.2f}s exceeds 3s target"
        assert std_dev < 1.0, f"Response time variance too high: {std_dev:.2f}s"

        print(f"Consecutive requests - Avg: {avg_time:.3f}s, StdDev: {std_dev:.3f}s")

    def test_concurrent_requests_performance(self, ai_engine):
        """Test concurrent request handling - Target: 10+ concurrent"""
        num_concurrent = 10
        requests = []

        # Create different requests to avoid caching
        for i in range(num_concurrent):
            request = ConversationRequest(
                buyer_message=f"¡Hola! ¿Está disponible el producto {i}?",
                buyer_name=f"TestBuyer{i}",
                product_name=f"iPhone 12 - {i}",
                price=400 + i,
                conversation_history=[],
                personality="profesional_cordial",
            )
            requests.append(request)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [
                executor.submit(ai_engine.generate_response, req) for req in requests
            ]

            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        total_time = time.time() - start_time

        # All requests should succeed
        successful_requests = sum(1 for r in results if r.success)
        assert (
            successful_requests == num_concurrent
        ), f"Only {successful_requests}/{num_concurrent} requests succeeded"

        # Should complete in reasonable time (not much longer than single request)
        assert (
            total_time < 10.0
        ), f"Concurrent requests took {total_time:.2f}s (too long)"

        avg_time_per_request = total_time / num_concurrent
        print(
            f"Concurrent requests - Total: {total_time:.3f}s, Avg per request: {avg_time_per_request:.3f}s"
        )

    def test_memory_usage_under_load(self, ai_engine, sample_request):
        """Test memory usage during sustained load - Target: <80% system RAM"""
        initial_memory = self.measure_memory_usage()
        max_memory = initial_memory

        # Run sustained load for memory testing
        num_requests = 50

        for i in range(num_requests):
            response = ai_engine.generate_response(sample_request)
            assert response.success is True

            current_memory = self.measure_memory_usage()
            max_memory = max(max_memory, current_memory)

            # Check for memory leaks (gradual increase)
            if i % 10 == 0:
                memory_increase = current_memory - initial_memory
                assert (
                    memory_increase < 100
                ), f"Potential memory leak: {memory_increase:.1f}MB increase"

        # Check total system memory usage
        system_memory = psutil.virtual_memory()
        memory_usage_percent = (max_memory * 1024 * 1024) / system_memory.total * 100

        assert (
            memory_usage_percent < 80
        ), f"Memory usage {memory_usage_percent:.1f}% exceeds 80% target"

        print(
            f"Memory usage - Peak: {max_memory:.1f}MB, System: {memory_usage_percent:.1f}%"
        )

    def test_response_quality_under_load(self, ai_engine):
        """Test that response quality doesn't degrade under load"""
        num_requests = 20
        quality_scores = []

        for i in range(num_requests):
            request = ConversationRequest(
                buyer_message="¿Cuánto vale el iPhone?",
                buyer_name=f"TestBuyer{i}",
                product_name="iPhone 12",
                price=400,
                conversation_history=[],
                personality="profesional_cordial",
            )

            response = ai_engine.generate_response(request)
            assert response.success is True

            # Basic quality checks
            quality_score = 0
            if len(response.response_text) > 10:  # Reasonable length
                quality_score += 1
            if response.confidence > 0.5:  # Good confidence
                quality_score += 1
            if response.risk_score < 30:  # Low risk
                quality_score += 1
            if (
                "€" in response.response_text
                or "precio" in response.response_text.lower()
            ):  # Relevant content
                quality_score += 1

            quality_scores.append(quality_score)

        avg_quality = statistics.mean(quality_scores)
        assert (
            avg_quality >= 3.0
        ), f"Average quality score {avg_quality:.1f} below threshold"

        print(f"Response quality under load - Average score: {avg_quality:.1f}/4.0")

    def test_error_recovery_performance(self, ai_engine):
        """Test error recovery and fallback performance"""
        # Simulate various error conditions
        error_scenarios = [
            {"type": "network_timeout", "delay": 5.0},
            {"type": "invalid_input", "message": ""},
            {"type": "high_load", "concurrent": 20},
        ]

        recovery_times = []

        for scenario in error_scenarios:
            start_time = time.time()

            if scenario["type"] == "network_timeout":
                # Simulate network timeout with fallback
                with patch.object(
                    ai_engine, "_call_llm_api", side_effect=Exception("Network timeout")
                ):
                    request = ConversationRequest(
                        buyer_message="¡Hola! ¿Está disponible?",
                        buyer_name="TestBuyer",
                        product_name="iPhone 12",
                        price=400,
                    )
                    response = ai_engine.generate_response(request)

                    # Should fallback successfully
                    assert response.success is True
                    assert response.source == "fallback"

            elif scenario["type"] == "invalid_input":
                # Test with invalid input
                try:
                    request = ConversationRequest(
                        buyer_message="",  # Empty message
                        buyer_name="TestBuyer",
                        product_name="iPhone 12",
                        price=400,
                    )
                    response = ai_engine.generate_response(request)
                    # Should handle gracefully
                    assert response is not None
                except Exception as e:
                    # Should not crash
                    assert "validation" in str(e).lower()

            recovery_time = time.time() - start_time
            recovery_times.append(recovery_time)

            # Recovery should be fast
            assert recovery_time < 5.0, f"Error recovery too slow: {recovery_time:.2f}s"

        avg_recovery_time = statistics.mean(recovery_times)
        print(f"Error recovery - Average time: {avg_recovery_time:.3f}s")

    def test_cache_performance(self, ai_engine):
        """Test caching effectiveness for performance"""
        # Test with repeated similar requests
        base_request = ConversationRequest(
            buyer_message="¡Hola! ¿Está disponible?",
            buyer_name="TestBuyer",
            product_name="iPhone 12",
            price=400,
        )

        # First request (no cache)
        start_time = time.time()
        response1 = ai_engine.generate_response(base_request)
        first_request_time = time.time() - start_time

        # Second identical request (should use cache if available)
        start_time = time.time()
        response2 = ai_engine.generate_response(base_request)
        second_request_time = time.time() - start_time

        assert response1.success is True
        assert response2.success is True

        # If caching is enabled, second request should be faster
        if hasattr(ai_engine, "cache_enabled") and ai_engine.cache_enabled:
            assert (
                second_request_time <= first_request_time
            ), "Caching not improving performance"
            print(
                f"Cache performance - First: {first_request_time:.3f}s, Second: {second_request_time:.3f}s"
            )
        else:
            print(
                f"No caching - First: {first_request_time:.3f}s, Second: {second_request_time:.3f}s"
            )

    @pytest.mark.slow
    def test_sustained_load_performance(self, ai_engine):
        """Test sustained load over time - Target: stable performance"""
        duration_minutes = 2  # Shorter for CI/CD
        requests_per_minute = 30
        total_requests = duration_minutes * requests_per_minute

        response_times = []
        success_count = 0
        start_time = time.time()

        for i in range(total_requests):
            request = ConversationRequest(
                buyer_message=f"Consulta número {i}",
                buyer_name=f"Buyer{i}",
                product_name="iPhone 12",
                price=400,
                conversation_history=[],
            )

            request_start = time.time()
            response = ai_engine.generate_response(request)
            request_time = time.time() - request_start

            response_times.append(request_time)

            if response.success:
                success_count += 1

            # Maintain request rate
            elapsed = time.time() - start_time
            expected_elapsed = (i + 1) / requests_per_minute * 60
            if elapsed < expected_elapsed:
                time.sleep(expected_elapsed - elapsed)

        _ = time.time() - start_time  # total_time used for reference
        success_rate = success_count / total_requests
        avg_response_time = statistics.mean(response_times)

        # Performance should remain stable
        assert (
            success_rate >= 0.95
        ), f"Success rate {success_rate:.2%} below 95% threshold"
        assert (
            avg_response_time < 5.0
        ), f"Average response time {avg_response_time:.2f}s too high"

        print(
            f"Sustained load - Success rate: {success_rate:.2%}, Avg time: {avg_response_time:.3f}s"
        )


@pytest.mark.performance
class TestSystemResourceUsage:
    """System-level performance tests"""

    def test_cpu_usage_monitoring(self):
        """Monitor CPU usage during AI Engine operations"""
        config = AIEngineConfig.for_research()
        config.fallback_mode = "template_only"
        ai_engine = AIEngine(config)

        # Monitor CPU usage
        cpu_percentages = []

        def monitor_cpu():
            for _ in range(10):
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_percentages.append(cpu_percent)

        # Start CPU monitoring in background
        import threading

        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Generate load
        for i in range(10):
            request = ConversationRequest(
                buyer_message=f"Mensaje {i}",
                buyer_name=f"Buyer{i}",
                product_name="Test Product",
                price=100,
            )
            response = ai_engine.generate_response(request)
            assert response.success is True

        monitor_thread.join()

        avg_cpu = statistics.mean(cpu_percentages)
        max_cpu = max(cpu_percentages)

        # CPU usage should be reasonable
        assert avg_cpu < 80, f"Average CPU usage {avg_cpu:.1f}% too high"
        assert max_cpu < 95, f"Peak CPU usage {max_cpu:.1f}% too high"

        print(f"CPU usage - Average: {avg_cpu:.1f}%, Peak: {max_cpu:.1f}%")

    def test_disk_io_monitoring(self):
        """Monitor disk I/O during operations"""
        initial_io = psutil.disk_io_counters()

        config = AIEngineConfig.for_research()
        ai_engine = AIEngine(config)

        # Generate some load
        for i in range(20):
            request = ConversationRequest(
                buyer_message=f"Test message {i}",
                buyer_name=f"Buyer{i}",
                product_name="Test Product",
                price=100,
            )
            response = ai_engine.generate_response(request)
            assert response.success is True

        final_io = psutil.disk_io_counters()

        # Calculate I/O usage
        read_bytes = final_io.read_bytes - initial_io.read_bytes
        write_bytes = final_io.write_bytes - initial_io.write_bytes

        # I/O should be reasonable
        read_mb = read_bytes / 1024 / 1024
        write_mb = write_bytes / 1024 / 1024

        assert read_mb < 100, f"Disk read {read_mb:.1f}MB too high"
        assert write_mb < 50, f"Disk write {write_mb:.1f}MB too high"

        print(f"Disk I/O - Read: {read_mb:.1f}MB, Write: {write_mb:.1f}MB")


if __name__ == "__main__":
    # Run with performance markers
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
