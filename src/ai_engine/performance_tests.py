"""
Performance Test Suite for AI Engine
Comprehensive performance testing and benchmarking for production readiness
"""

import asyncio
import time
import logging
import statistics
import gc
import psutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .config import AIEngineConfig
from .ai_engine import AIEngine, ConversationRequest, ConversationResponse
from .performance_monitor import PerformanceMonitor


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""

    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    average_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95_response_time: float
    requests_per_second: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_rate: float
    cache_hit_rate: Optional[float] = None
    concurrent_requests: int = 1
    metadata: Dict[str, Any] = None


class PerformanceTestSuite:
    """Comprehensive performance test suite"""

    def __init__(self, config: Optional[AIEngineConfig] = None):
        self.config = config or AIEngineConfig.for_research()
        self.logger = logging.getLogger(__name__)
        self.ai_engine = None
        self.test_requests = []

        # Test data
        self._setup_test_data()

    def _setup_test_data(self):
        """Setup test conversation requests"""

        test_messages = [
            "¡Hola! ¿Está disponible este producto?",
            "¿Cuál es el precio final?",
            "¿Aceptas 80 euros?",
            "¿Dónde podemos quedar para recogerlo?",
            "¿Está en buen estado?",
            "¿Tienes más fotos?",
            "¿Por qué lo vendes?",
            "¿Incluye accesorios?",
            "¿Funciona perfectamente?",
            "¿Hasta cuándo lo tienes disponible?",
            "¿Hay algún defecto?",
            "¿Es el precio negociable?",
            "¿Puedo verlo antes de comprarlo?",
            "¿Aceptas intercambio?",
            "¿Tienes garantía?",
        ]

        products = [
            ("iPhone 12", 400, "muy buen estado"),
            ("MacBook Pro", 1200, "como nuevo"),
            ("PlayStation 5", 500, "buen estado"),
            ("Nintendo Switch", 250, "usado"),
            ("iPad Air", 350, "muy buen estado"),
        ]

        buyers = [
            ("Carlos", {"rating": 4.5, "purchases": 12}),
            ("María", {"rating": 4.8, "purchases": 25}),
            ("Luis", {"rating": 3.9, "purchases": 3}),
            ("Ana", {"rating": 5.0, "purchases": 45}),
            ("Jorge", {"rating": 4.2, "purchases": 8}),
        ]

        # Generate test requests
        for message in test_messages:
            for product_name, price, condition in products:
                for buyer_name, buyer_profile in buyers:
                    request = ConversationRequest(
                        buyer_message=message,
                        buyer_name=buyer_name,
                        product_name=product_name,
                        price=price,
                        condition=condition,
                        buyer_profile=buyer_profile,
                        conversation_history=[],
                        personality="profesional_cordial",
                    )
                    self.test_requests.append(request)

        self.logger.info(f"Generated {len(self.test_requests)} test requests")

    async def setup_engine(self):
        """Setup AI Engine for testing"""
        self.logger.info("Setting up AI Engine for performance testing...")

        # Use optimized config for testing
        test_config = AIEngineConfig.for_hardware()
        test_config.debug_mode = False
        test_config.enable_profiling = True
        test_config.log_level = "WARNING"  # Reduce logging overhead

        self.ai_engine = AIEngine(test_config)

        # Wait for initialization
        await asyncio.sleep(2)

        # Test engine is ready
        health_test = await self.ai_engine.test_engine_async()
        if not health_test.get("llm_available", False):
            self.logger.warning("LLM not available, tests will use fallback only")

        self.logger.info("AI Engine setup complete")

    async def teardown_engine(self):
        """Teardown AI Engine"""
        if self.ai_engine:
            self.ai_engine.shutdown()
            self.ai_engine = None

        # Force garbage collection
        gc.collect()

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        process = psutil.Process()

        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
        }

    async def benchmark_single_requests(
        self, num_requests: int = 100
    ) -> BenchmarkResult:
        """Benchmark single sequential requests"""

        self.logger.info(f"Starting single request benchmark ({num_requests} requests)")

        # Select test requests
        test_subset = self.test_requests[:num_requests]

        # Track metrics
        response_times = []
        successful = 0
        failed = 0
        start_metrics = self._get_system_metrics()
        peak_memory = start_metrics["memory_mb"]

        start_time = time.time()

        for i, request in enumerate(test_subset):
            try:
                request_start = time.time()
                response = await self.ai_engine.generate_response_async(request)
                request_time = time.time() - request_start

                response_times.append(request_time)

                if response.success:
                    successful += 1
                else:
                    failed += 1

                # Track peak memory
                current_memory = self._get_system_metrics()["memory_mb"]
                peak_memory = max(peak_memory, current_memory)

                # Log progress
                if (i + 1) % 10 == 0:
                    self.logger.debug(f"Completed {i + 1}/{num_requests} requests")

            except Exception as e:
                self.logger.error(f"Request failed: {e}")
                failed += 1

        total_time = time.time() - start_time
        end_metrics = self._get_system_metrics()

        # Calculate statistics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        p95_response_time = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) >= 20
            else max_response_time
        )

        # Get cache hit rate if available
        cache_hit_rate = None
        if (
            hasattr(self.ai_engine, "response_generator")
            and hasattr(self.ai_engine.response_generator, "llm_manager")
            and hasattr(self.ai_engine.response_generator.llm_manager, "metrics")
        ):

            cache_hit_rate = (
                self.ai_engine.response_generator.llm_manager.metrics.cache_hit_rate
            )

        return BenchmarkResult(
            test_name="single_requests",
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95_response_time=p95_response_time,
            requests_per_second=num_requests / total_time,
            memory_usage_mb=end_metrics["memory_mb"],
            peak_memory_mb=peak_memory,
            cpu_usage_percent=end_metrics["cpu_percent"],
            success_rate=successful / num_requests,
            error_rate=failed / num_requests,
            cache_hit_rate=cache_hit_rate,
            concurrent_requests=1,
        )

    async def benchmark_concurrent_requests(
        self, num_requests: int = 50, concurrency: int = 10
    ) -> BenchmarkResult:
        """Benchmark concurrent requests"""

        self.logger.info(
            f"Starting concurrent request benchmark ({num_requests} requests, {concurrency} concurrent)"
        )

        # Select test requests
        test_subset = self.test_requests[:num_requests]

        # Track metrics
        response_times = []
        successful = 0
        failed = 0
        start_metrics = self._get_system_metrics()
        peak_memory = start_metrics["memory_mb"]

        start_time = time.time()

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def process_request(request: ConversationRequest) -> Tuple[bool, float]:
            async with semaphore:
                try:
                    request_start = time.time()
                    response = await self.ai_engine.generate_response_async(request)
                    request_time = time.time() - request_start

                    # Track peak memory
                    current_memory = self._get_system_metrics()["memory_mb"]
                    nonlocal peak_memory
                    peak_memory = max(peak_memory, current_memory)

                    return response.success, request_time

                except Exception as e:
                    self.logger.error(f"Concurrent request failed: {e}")
                    return False, 0.0

        # Execute all requests concurrently
        tasks = [process_request(request) for request in test_subset]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                success, response_time = result
                response_times.append(response_time)
                if success:
                    successful += 1
                else:
                    failed += 1

        total_time = time.time() - start_time
        end_metrics = self._get_system_metrics()

        # Calculate statistics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        p95_response_time = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) >= 20
            else max_response_time
        )

        # Get cache hit rate
        cache_hit_rate = None
        if (
            hasattr(self.ai_engine, "response_generator")
            and hasattr(self.ai_engine.response_generator, "llm_manager")
            and hasattr(self.ai_engine.response_generator.llm_manager, "metrics")
        ):

            cache_hit_rate = (
                self.ai_engine.response_generator.llm_manager.metrics.cache_hit_rate
            )

        return BenchmarkResult(
            test_name="concurrent_requests",
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95_response_time=p95_response_time,
            requests_per_second=num_requests / total_time,
            memory_usage_mb=end_metrics["memory_mb"],
            peak_memory_mb=peak_memory,
            cpu_usage_percent=end_metrics["cpu_percent"],
            success_rate=successful / num_requests,
            error_rate=failed / num_requests,
            cache_hit_rate=cache_hit_rate,
            concurrent_requests=concurrency,
        )

    async def benchmark_sustained_load(
        self, duration_seconds: int = 300, target_rps: int = 5
    ) -> BenchmarkResult:
        """Benchmark sustained load over time"""

        self.logger.info(
            f"Starting sustained load benchmark ({duration_seconds}s at {target_rps} RPS)"
        )

        # Calculate request interval
        request_interval = 1.0 / target_rps

        # Track metrics
        response_times = []
        successful = 0
        failed = 0
        start_metrics = self._get_system_metrics()
        peak_memory = start_metrics["memory_mb"]

        start_time = time.time()
        end_time = start_time + duration_seconds

        request_count = 0

        while time.time() < end_time:
            try:
                # Select random request
                request = self.test_requests[request_count % len(self.test_requests)]

                request_start = time.time()
                response = await self.ai_engine.generate_response_async(request)
                request_time = time.time() - request_start

                response_times.append(request_time)
                request_count += 1

                if response.success:
                    successful += 1
                else:
                    failed += 1

                # Track peak memory
                current_memory = self._get_system_metrics()["memory_mb"]
                peak_memory = max(peak_memory, current_memory)

                # Log progress
                if request_count % 50 == 0:
                    elapsed = time.time() - start_time
                    current_rps = request_count / elapsed
                    self.logger.debug(
                        f"Sustained load: {request_count} requests, {current_rps:.1f} RPS"
                    )

                # Wait for next request
                next_request_time = start_time + (request_count * request_interval)
                sleep_time = next_request_time - time.time()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Sustained load request failed: {e}")
                failed += 1
                request_count += 1

        total_time = time.time() - start_time
        end_metrics = self._get_system_metrics()

        # Calculate statistics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        p95_response_time = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) >= 20
            else max_response_time
        )

        # Get cache hit rate
        cache_hit_rate = None
        if (
            hasattr(self.ai_engine, "response_generator")
            and hasattr(self.ai_engine.response_generator, "llm_manager")
            and hasattr(self.ai_engine.response_generator.llm_manager, "metrics")
        ):

            cache_hit_rate = (
                self.ai_engine.response_generator.llm_manager.metrics.cache_hit_rate
            )

        return BenchmarkResult(
            test_name="sustained_load",
            total_requests=request_count,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95_response_time=p95_response_time,
            requests_per_second=request_count / total_time,
            memory_usage_mb=end_metrics["memory_mb"],
            peak_memory_mb=peak_memory,
            cpu_usage_percent=end_metrics["cpu_percent"],
            success_rate=successful / request_count,
            error_rate=failed / request_count,
            cache_hit_rate=cache_hit_rate,
            concurrent_requests=1,
            metadata={"target_rps": target_rps, "duration_seconds": duration_seconds},
        )

    async def benchmark_memory_usage(self, num_requests: int = 200) -> BenchmarkResult:
        """Benchmark memory usage patterns"""

        self.logger.info(f"Starting memory usage benchmark ({num_requests} requests)")

        # Track memory over time
        memory_samples = []
        _ = gc.get_count()  # Initial GC count (used for reference)

        # Force initial GC
        gc.collect()
        initial_memory = self._get_system_metrics()["memory_mb"]

        start_time = time.time()

        for i in range(num_requests):
            request = self.test_requests[i % len(self.test_requests)]

            try:
                await self.ai_engine.generate_response_async(request)

                # Sample memory every 10 requests
                if i % 10 == 0:
                    memory_samples.append(self._get_system_metrics()["memory_mb"])

                # Force GC every 50 requests to test cleanup
                if i % 50 == 0:
                    gc.collect()

            except Exception as e:
                self.logger.error(f"Memory test request failed: {e}")

        final_gc_collections = gc.get_count()
        final_memory = self._get_system_metrics()["memory_mb"]
        total_time = time.time() - start_time

        # Calculate memory statistics
        peak_memory = max(memory_samples) if memory_samples else final_memory
        avg_memory = statistics.mean(memory_samples) if memory_samples else final_memory
        memory_growth = final_memory - initial_memory

        return BenchmarkResult(
            test_name="memory_usage",
            total_requests=num_requests,
            successful_requests=num_requests,  # Simplified for memory test
            failed_requests=0,
            total_time=total_time,
            average_response_time=total_time / num_requests,
            min_response_time=0,
            max_response_time=0,
            percentile_95_response_time=0,
            requests_per_second=num_requests / total_time,
            memory_usage_mb=final_memory,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=0,
            success_rate=1.0,
            error_rate=0.0,
            concurrent_requests=1,
            metadata={
                "initial_memory_mb": initial_memory,
                "memory_growth_mb": memory_growth,
                "avg_memory_mb": avg_memory,
                "gc_collections": final_gc_collections,
            },
        )

    async def run_full_benchmark_suite(self) -> Dict[str, BenchmarkResult]:
        """Run complete benchmark suite"""

        self.logger.info("Starting full performance benchmark suite")

        results = {}

        try:
            # Setup engine
            await self.setup_engine()

            # Test 1: Single requests
            self.logger.info("Running single request benchmark...")
            results["single_requests"] = await self.benchmark_single_requests(100)

            # Small delay between tests
            await asyncio.sleep(5)

            # Test 2: Concurrent requests
            self.logger.info("Running concurrent request benchmark...")
            results["concurrent_requests"] = await self.benchmark_concurrent_requests(
                50, 10
            )

            await asyncio.sleep(5)

            # Test 3: Memory usage
            self.logger.info("Running memory usage benchmark...")
            results["memory_usage"] = await self.benchmark_memory_usage(200)

            await asyncio.sleep(5)

            # Test 4: Sustained load (shorter for testing)
            self.logger.info("Running sustained load benchmark...")
            results["sustained_load"] = await self.benchmark_sustained_load(
                120, 3
            )  # 2 minutes at 3 RPS

        finally:
            # Teardown
            await self.teardown_engine()

        self.logger.info("Full benchmark suite completed")
        return results

    def generate_performance_report(  # noqa: C901
        self, results: Dict[str, BenchmarkResult]
    ) -> str:
        """Generate comprehensive performance report"""

        report = ["=" * 80]
        report.append("AI ENGINE PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 80)
        report.append("")

        # System info
        system_info = self.config.get_system_info()
        report.append("SYSTEM INFORMATION:")
        report.append(f"Platform: {system_info['platform']}")
        report.append(f"CPU Cores: {system_info['cpu_count']}")
        report.append(f"Total RAM: {system_info['memory_total_gb']:.1f} GB")
        report.append(f"Available RAM: {system_info['memory_available_gb']:.1f} GB")
        report.append("")

        # Configuration
        report.append("AI ENGINE CONFIGURATION:")
        report.append(f"Model: {self.config.model_name}")
        report.append(f"Max Concurrent Requests: {self.config.max_concurrent_requests}")
        report.append(f"Thread Pool Size: {self.config.thread_pool_size}")
        report.append(f"Memory Threshold: {self.config.memory_threshold_mb} MB")
        report.append(f"Caching Enabled: {self.config.enable_caching}")
        report.append("")

        # Performance targets
        report.append("PERFORMANCE TARGETS:")
        report.append("✓ Response Time: <3 seconds end-to-end")
        report.append("✓ Concurrent Requests: 10+ simultaneous")
        report.append("✓ Memory Usage: <80% of available RAM")
        report.append("✓ Throughput: 20+ responses per minute")
        report.append("✓ Availability: 99.9% uptime")
        report.append("")

        # Results for each test
        for test_name, result in results.items():
            report.append(f"BENCHMARK: {result.test_name.upper()}")
            report.append("-" * 40)

            # Basic metrics
            report.append(f"Total Requests: {result.total_requests}")
            report.append(
                f"Successful: {result.successful_requests} ({result.success_rate:.1%})"
            )
            report.append(f"Failed: {result.failed_requests} ({result.error_rate:.1%})")
            report.append(f"Total Time: {result.total_time:.2f}s")

            # Performance metrics
            report.append(f"Average Response Time: {result.average_response_time:.3f}s")
            report.append(f"Min Response Time: {result.min_response_time:.3f}s")
            report.append(f"Max Response Time: {result.max_response_time:.3f}s")
            report.append(f"95th Percentile: {result.percentile_95_response_time:.3f}s")

            # Throughput
            report.append(f"Requests/Second: {result.requests_per_second:.2f}")
            report.append(f"Requests/Minute: {result.requests_per_second * 60:.1f}")

            # Resource usage
            report.append(f"Memory Usage: {result.memory_usage_mb:.1f} MB")
            report.append(f"Peak Memory: {result.peak_memory_mb:.1f} MB")
            report.append(f"CPU Usage: {result.cpu_usage_percent:.1f}%")

            # Cache performance
            if result.cache_hit_rate is not None:
                report.append(f"Cache Hit Rate: {result.cache_hit_rate:.1%}")

            # Concurrency
            if result.concurrent_requests > 1:
                report.append(f"Concurrent Requests: {result.concurrent_requests}")

            # Performance assessment
            report.append("")
            report.append("PERFORMANCE ASSESSMENT:")

            # Response time assessment
            if result.average_response_time <= 3.0:
                report.append("✓ Response time target met")
            else:
                report.append("✗ Response time target exceeded")

            # Throughput assessment
            if result.requests_per_second * 60 >= 20:
                report.append("✓ Throughput target met")
            else:
                report.append("✗ Throughput target not met")

            # Success rate assessment
            if result.success_rate >= 0.999:
                report.append("✓ Availability target met")
            else:
                report.append("✗ Availability target not met")

            # Memory assessment
            memory_percent = (
                result.peak_memory_mb / (system_info["memory_total_gb"] * 1024)
            ) * 100
            if memory_percent <= 80:
                report.append("✓ Memory usage target met")
            else:
                report.append("✗ Memory usage target exceeded")

            report.append("")

        # Overall assessment
        report.append("OVERALL PERFORMANCE SUMMARY:")
        report.append("-" * 40)

        avg_response_time = statistics.mean(
            [r.average_response_time for r in results.values()]
        )
        avg_throughput = statistics.mean(
            [r.requests_per_second * 60 for r in results.values()]
        )
        avg_success_rate = statistics.mean([r.success_rate for r in results.values()])
        peak_memory_mb = max([r.peak_memory_mb for r in results.values()])

        report.append(f"Average Response Time: {avg_response_time:.3f}s")
        report.append(f"Average Throughput: {avg_throughput:.1f} requests/minute")
        report.append(f"Average Success Rate: {avg_success_rate:.1%}")
        report.append(f"Peak Memory Usage: {peak_memory_mb:.1f} MB")

        # Production readiness assessment
        report.append("")
        report.append("PRODUCTION READINESS:")

        production_ready = True

        if avg_response_time > 3.0:
            report.append("⚠ Response time may be too slow for production")
            production_ready = False

        if avg_throughput < 20:
            report.append("⚠ Throughput may be insufficient for production load")
            production_ready = False

        if avg_success_rate < 0.999:
            report.append("⚠ Success rate may not meet availability requirements")
            production_ready = False

        memory_percent = (
            peak_memory_mb / (system_info["memory_total_gb"] * 1024)
        ) * 100
        if memory_percent > 80:
            report.append("⚠ Memory usage may be too high for production")
            production_ready = False

        if production_ready:
            report.append("✅ AI Engine is READY for production deployment")
        else:
            report.append(
                "❌ AI Engine needs optimization before production deployment"
            )

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_results_json(self, results: Dict[str, BenchmarkResult], filename: str):
        """Save benchmark results to JSON file"""

        json_data = {
            "timestamp": time.time(),
            "system_info": self.config.get_system_info(),
            "config": {
                "model_name": self.config.model_name,
                "max_concurrent_requests": self.config.max_concurrent_requests,
                "thread_pool_size": self.config.thread_pool_size,
                "memory_threshold_mb": self.config.memory_threshold_mb,
                "enable_caching": self.config.enable_caching,
            },
            "results": {},
        }

        # Convert results to JSON-serializable format
        for test_name, result in results.items():
            json_data["results"][test_name] = {
                "test_name": result.test_name,
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "total_time": result.total_time,
                "average_response_time": result.average_response_time,
                "min_response_time": result.min_response_time,
                "max_response_time": result.max_response_time,
                "percentile_95_response_time": result.percentile_95_response_time,
                "requests_per_second": result.requests_per_second,
                "memory_usage_mb": result.memory_usage_mb,
                "peak_memory_mb": result.peak_memory_mb,
                "cpu_usage_percent": result.cpu_usage_percent,
                "success_rate": result.success_rate,
                "error_rate": result.error_rate,
                "cache_hit_rate": result.cache_hit_rate,
                "concurrent_requests": result.concurrent_requests,
                "metadata": result.metadata,
            }

        with open(filename, "w") as f:
            json.dump(json_data, f, indent=2)

        self.logger.info(f"Benchmark results saved to {filename}")


# CLI interface for running benchmarks
async def main():
    """Main function for running benchmarks from command line"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Engine Performance Benchmark Suite"
    )
    parser.add_argument(
        "--test",
        choices=["single", "concurrent", "sustained", "memory", "all"],
        default="all",
        help="Test type to run",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Number of requests for single/memory tests",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Concurrency level for concurrent test",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Duration in seconds for sustained test",
    )
    parser.add_argument(
        "--rps",
        type=int,
        default=5,
        help="Target requests per second for sustained test",
    )
    parser.add_argument("--output", type=str, help="Output file for JSON results")
    parser.add_argument(
        "--config",
        choices=["research", "production", "development"],
        default="research",
        help="Configuration preset",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Select configuration
    if args.config == "research":
        config = AIEngineConfig.for_research()
    elif args.config == "production":
        config = AIEngineConfig.for_production()
    else:
        config = AIEngineConfig.for_development()

    # Create test suite
    test_suite = PerformanceTestSuite(config)

    try:
        # Setup engine
        await test_suite.setup_engine()

        results = {}

        # Run selected tests
        if args.test == "single" or args.test == "all":
            results["single_requests"] = await test_suite.benchmark_single_requests(
                args.requests
            )

        if args.test == "concurrent" or args.test == "all":
            results["concurrent_requests"] = (
                await test_suite.benchmark_concurrent_requests(
                    args.requests, args.concurrency
                )
            )

        if args.test == "sustained" or args.test == "all":
            results["sustained_load"] = await test_suite.benchmark_sustained_load(
                args.duration, args.rps
            )

        if args.test == "memory" or args.test == "all":
            results["memory_usage"] = await test_suite.benchmark_memory_usage(
                args.requests
            )

        # Generate report
        report = test_suite.generate_performance_report(results)
        print(report)

        # Save JSON results if requested
        if args.output:
            test_suite.save_results_json(results, args.output)

    finally:
        await test_suite.teardown_engine()


if __name__ == "__main__":
    asyncio.run(main())
