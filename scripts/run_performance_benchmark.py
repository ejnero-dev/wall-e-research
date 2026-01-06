#!/usr/bin/env python3
"""
Performance Benchmark Runner for Wall-E AI Engine
Easy-to-use script for running comprehensive performance tests
"""

import sys
import os
import asyncio
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ai_engine.performance_tests import PerformanceTestSuite
from ai_engine.config import AIEngineConfig


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("performance_benchmark.log"),
        ],
    )


async def run_quick_benchmark() -> None:
    """Run a quick benchmark for basic validation"""

    print("🚀 Running Quick AI Engine Performance Benchmark")
    print("=" * 60)

    # Use research config for quick test
    config = AIEngineConfig.for_research()
    test_suite = PerformanceTestSuite(config)

    try:
        # Setup engine
        await test_suite.setup_engine()

        # Run quick tests
        print("Testing single requests...")
        single_result = await test_suite.benchmark_single_requests(20)

        print("Testing concurrent requests...")
        concurrent_result = await test_suite.benchmark_concurrent_requests(15, 5)

        # Generate quick report
        results = {
            "single_requests": single_result,
            "concurrent_requests": concurrent_result,
        }

        report = test_suite.generate_performance_report(results)
        print("\n" + report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_benchmark_{timestamp}.json"
        test_suite.save_results_json(results, filename)
        print(f"\n📄 Results saved to: {filename}")

    finally:
        await test_suite.teardown_engine()


async def run_full_benchmark() -> None:
    """Run comprehensive benchmark suite"""

    print("🚀 Running Full AI Engine Performance Benchmark Suite")
    print("=" * 60)

    # Use production config for comprehensive test
    config = AIEngineConfig.for_production()
    test_suite = PerformanceTestSuite(config)

    try:
        results = await test_suite.run_full_benchmark_suite()

        # Generate comprehensive report
        report = test_suite.generate_performance_report(results)
        print("\n" + report)

        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"full_benchmark_{timestamp}.json"
        test_suite.save_results_json(results, filename)

        # Also save report as text
        report_filename = f"benchmark_report_{timestamp}.txt"
        with open(report_filename, "w") as f:
            f.write(report)

        print(f"\n📄 Results saved to: {filename}")
        print(f"📄 Report saved to: {report_filename}")

    finally:
        await test_suite.teardown_engine()


async def run_memory_stress_test() -> None:
    """Run memory stress test to validate memory management"""

    print("🧠 Running Memory Stress Test")
    print("=" * 60)

    config = AIEngineConfig.for_research()
    # Increase memory threshold for stress testing
    config.memory_threshold_mb = int(config.memory_threshold_mb * 0.9)
    config.gc_threshold = 25  # More frequent GC

    test_suite = PerformanceTestSuite(config)

    try:
        await test_suite.setup_engine()

        print("Running memory stress test (500 requests)...")
        memory_result = await test_suite.benchmark_memory_usage(500)

        print("Running sustained load for memory analysis...")
        sustained_result = await test_suite.benchmark_sustained_load(
            180, 8
        )  # 3 min at 8 RPS

        results = {"memory_stress": memory_result, "sustained_memory": sustained_result}

        # Generate memory-focused report
        report = test_suite.generate_performance_report(results)
        print("\n" + report)

        # Additional memory analysis
        print("\n🧠 MEMORY ANALYSIS:")
        print("-" * 30)

        if memory_result.metadata:
            initial_memory = memory_result.metadata.get("initial_memory_mb", 0)
            memory_growth = memory_result.metadata.get("memory_growth_mb", 0)
            avg_memory = memory_result.metadata.get("avg_memory_mb", 0)

            print(f"Initial Memory: {initial_memory:.1f} MB")
            print(f"Final Memory: {memory_result.memory_usage_mb:.1f} MB")
            print(f"Memory Growth: {memory_growth:.1f} MB")
            print(f"Average Memory: {avg_memory:.1f} MB")
            print(f"Peak Memory: {memory_result.peak_memory_mb:.1f} MB")

            # Memory efficiency assessment
            memory_efficiency = (
                (memory_growth / memory_result.total_requests)
                if memory_result.total_requests > 0
                else 0
            )
            print(f"Memory per Request: {memory_efficiency:.3f} MB/request")

            if memory_growth < 50:  # Less than 50MB growth
                print("✅ Memory management is efficient")
            elif memory_growth < 100:
                print("⚠️  Memory growth is moderate")
            else:
                print("❌ Memory growth is concerning")

        # Save memory test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_stress_test_{timestamp}.json"
        test_suite.save_results_json(results, filename)
        print(f"\n📄 Memory test results saved to: {filename}")

    finally:
        await test_suite.teardown_engine()


async def run_concurrent_stress_test(max_concurrency: int = 20) -> None:
    """Run concurrent stress test to validate concurrent handling"""

    print(f"⚡ Running Concurrent Stress Test (up to {max_concurrency} concurrent)")
    print("=" * 60)

    config = AIEngineConfig.for_research()
    # Optimize for high concurrency
    config.max_concurrent_requests = max_concurrency
    config.thread_pool_size = max_concurrency * 2
    config.connection_pool_size = min(max_concurrency, 10)

    test_suite = PerformanceTestSuite(config)

    try:
        await test_suite.setup_engine()

        results = {}

        # Test increasing concurrency levels
        concurrency_levels = [1, 5, 10, 15, max_concurrency]

        for concurrency in concurrency_levels:
            if concurrency > max_concurrency:
                continue

            print(f"Testing concurrency level: {concurrency}")

            result = await test_suite.benchmark_concurrent_requests(
                num_requests=concurrency * 10, concurrency=concurrency
            )

            results[f"concurrent_{concurrency}"] = result

            # Brief pause between tests
            await asyncio.sleep(2)

        # Generate concurrency report
        print("\n⚡ CONCURRENCY ANALYSIS:")
        print("-" * 40)

        for concurrency in concurrency_levels:
            if f"concurrent_{concurrency}" in results:
                result = results[f"concurrent_{concurrency}"]
                throughput = result.requests_per_second
                avg_time = result.average_response_time
                success_rate = result.success_rate

                print(
                    f"Concurrency {concurrency:2d}: {throughput:5.1f} RPS, "
                    f"{avg_time:5.3f}s avg, {success_rate:5.1%} success"
                )

        # Find optimal concurrency
        best_throughput = 0
        optimal_concurrency = 1

        for concurrency in concurrency_levels:
            if f"concurrent_{concurrency}" in results:
                result = results[f"concurrent_{concurrency}"]
                if (
                    result.success_rate > 0.95
                    and result.requests_per_second > best_throughput
                ):
                    best_throughput = result.requests_per_second
                    optimal_concurrency = concurrency

        print(
            f"\n🎯 Optimal Concurrency: {optimal_concurrency} (max sustainable throughput)"
        )

        # Save concurrent test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"concurrent_stress_test_{timestamp}.json"
        test_suite.save_results_json(results, filename)
        print(f"\n📄 Concurrent test results saved to: {filename}")

    finally:
        await test_suite.teardown_engine()


def main():
    """Main function with command line interface"""

    parser = argparse.ArgumentParser(
        description="Wall-E AI Engine Performance Benchmark Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_benchmark.py --quick           # Quick validation test
  python run_performance_benchmark.py --full            # Comprehensive test suite
  python run_performance_benchmark.py --memory          # Memory stress test
  python run_performance_benchmark.py --concurrent 15   # Concurrent stress test
  python run_performance_benchmark.py --all             # Run all tests
        """,
    )

    # Test selection
    parser.add_argument(
        "--quick", action="store_true", help="Run quick benchmark for basic validation"
    )
    parser.add_argument(
        "--full", action="store_true", help="Run comprehensive benchmark suite"
    )
    parser.add_argument("--memory", action="store_true", help="Run memory stress test")
    parser.add_argument(
        "--concurrent",
        type=int,
        metavar="MAX",
        help="Run concurrent stress test with max concurrency",
    )
    parser.add_argument("--all", action="store_true", help="Run all benchmark tests")

    # Configuration
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".", help="Output directory for results"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Change to output directory
    if args.output_dir != ".":
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)

    # Run selected tests
    async def run_tests():
        try:
            if args.quick or (
                not any([args.full, args.memory, args.concurrent, args.all])
            ):
                await run_quick_benchmark()

            if args.full or args.all:
                print("\n" + "=" * 80 + "\n")
                await run_full_benchmark()

            if args.memory or args.all:
                print("\n" + "=" * 80 + "\n")
                await run_memory_stress_test()

            if args.concurrent or args.all:
                concurrency = args.concurrent if args.concurrent else 15
                print("\n" + "=" * 80 + "\n")
                await run_concurrent_stress_test(concurrency)

            print("\n🎉 All benchmarks completed successfully!")

        except KeyboardInterrupt:
            print("\n❌ Benchmark interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Benchmark failed with error: {e}")
            logging.exception("Benchmark failed")
            sys.exit(1)

    # Run async main
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
