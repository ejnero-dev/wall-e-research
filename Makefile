# Wall-E Testing Makefile
# Professional CI/CD-ready test runners
# =====================================

.PHONY: help test test-unit test-integration test-performance test-e2e test-all test-coverage clean install-deps lint format check-deps

# Default target
help:
	@echo "🤖 Wall-E Test Suite Commands"
	@echo "=============================="
	@echo ""
	@echo "Test Commands:"
	@echo "  make test-unit         Run unit tests (fast, isolated components)"
	@echo "  make test-integration  Run integration tests (component interactions)"
	@echo "  make test-performance  Run performance benchmarks"
	@echo "  make test-e2e          Run end-to-end workflow tests"
	@echo "  make test-all          Run complete test suite"
	@echo "  make test-coverage     Run tests with detailed coverage report"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install-deps      Install test dependencies"
	@echo "  make lint              Run linting checks"
	@echo "  make format            Format code with black"
	@echo "  make check-deps        Check dependency compatibility"
	@echo "  make clean             Clean test artifacts"
	@echo ""
	@echo "CI/CD Commands:"
	@echo "  make ci-test           Run CI/CD test pipeline"
	@echo "  make ci-performance    Run performance benchmarks for CI"
	@echo ""

# Test dependency installation
install-deps:
	@echo "📦 Installing test dependencies..."
	pip install -r requirements-dev.txt
	pip install pytest pytest-asyncio pytest-cov pytest-xdist pytest-mock psutil
	@echo "✅ Test dependencies installed"

# Unit Tests - Fast, isolated component testing
test-unit:
	@echo "🧪 Running Unit Tests..."
	@echo "========================"
	pytest tests/unit/ \
		-v \
		--tb=short \
		--durations=10 \
		-m "not slow" \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:htmlcov/unit \
		--junit-xml=test-results/unit-results.xml
	@echo "✅ Unit tests completed"

# Integration Tests - Component interaction testing  
test-integration:
	@echo "🔗 Running Integration Tests..."
	@echo "==============================="
	pytest tests/integration/ \
		-v \
		--tb=short \
		--durations=10 \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:htmlcov/integration \
		--junit-xml=test-results/integration-results.xml
	@echo "✅ Integration tests completed"

# Performance Tests - Speed and load testing
test-performance:
	@echo "⚡ Running Performance Tests..."
	@echo "==============================="
	pytest tests/performance/ \
		-v \
		--tb=short \
		--durations=0 \
		-m performance \
		--junit-xml=test-results/performance-results.xml \
		--disable-warnings
	@echo "✅ Performance tests completed"

# End-to-End Tests - Complete workflow testing
test-e2e:
	@echo "🎯 Running End-to-End Tests..."
	@echo "=============================="
	pytest tests/e2e/ \
		-v \
		--tb=short \
		--durations=0 \
		-m e2e \
		--junit-xml=test-results/e2e-results.xml
	@echo "✅ End-to-end tests completed"

# Complete Test Suite
test-all: clean
	@echo "🚀 Running Complete Test Suite..."
	@echo "=================================="
	@mkdir -p test-results htmlcov
	pytest tests/ \
		-v \
		--tb=short \
		--durations=20 \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:htmlcov/complete \
		--cov-report=xml:test-results/coverage.xml \
		--junit-xml=test-results/complete-results.xml \
		--maxfail=5
	@echo ""
	@echo "📊 Test Summary:"
	@echo "=================="
	@echo "Coverage report: htmlcov/complete/index.html"
	@echo "JUnit results: test-results/complete-results.xml"
	@echo "✅ Complete test suite finished"

# Detailed Coverage Analysis
test-coverage:
	@echo "📈 Running Coverage Analysis..."
	@echo "==============================="
	@mkdir -p test-results htmlcov
	pytest tests/ \
		--cov=src \
		--cov-report=html:htmlcov/detailed \
		--cov-report=xml:test-results/coverage-detailed.xml \
		--cov-report=term-missing \
		--cov-fail-under=80 \
		--cov-branch
	@echo "📊 Coverage report: htmlcov/detailed/index.html"
	@echo "✅ Coverage analysis completed"

# Parallel Testing (faster execution)
test-parallel:
	@echo "⚡ Running Tests in Parallel..."
	@echo "==============================="
	pytest tests/ \
		-n auto \
		-v \
		--tb=short \
		--durations=10 \
		--cov=src \
		--cov-report=term-missing
	@echo "✅ Parallel tests completed"

# Quick Test (essential tests only)
test-quick:
	@echo "🏃 Running Quick Tests..."
	@echo "========================"
	pytest tests/unit/test_conversation_engine.py \
		tests/unit/test_ai_engine_basic.py \
		tests/integration/test_happy_path.py \
		-v \
		--tb=short \
		-m "not slow"
	@echo "✅ Quick tests completed"

# CI/CD Pipeline Tests
ci-test:
	@echo "🔄 Running CI/CD Test Pipeline..."
	@echo "=================================="
	@mkdir -p test-results htmlcov
	# Run tests with CI-specific settings
	pytest tests/ \
		--tb=line \
		--strict-markers \
		--strict-config \
		--cov=src \
		--cov-report=xml:test-results/coverage.xml \
		--cov-report=term \
		--junit-xml=test-results/junit.xml \
		--cov-fail-under=75 \
		-m "not slow" \
		--maxfail=3 \
		--disable-warnings
	@echo "✅ CI/CD tests completed"

# CI Performance Benchmarks (shorter for CI)
ci-performance:
	@echo "📊 Running CI Performance Benchmarks..."
	@echo "======================================="
	pytest tests/performance/test_ai_engine_performance.py::TestAIEnginePerformance::test_single_request_response_time \
		tests/performance/test_ai_engine_performance.py::TestAIEnginePerformance::test_concurrent_requests_performance \
		-v \
		--tb=short \
		--disable-warnings
	@echo "✅ CI performance benchmarks completed"

# Code Quality Checks
lint:
	@echo "🔍 Running Code Quality Checks..."
	@echo "================================="
	flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__,*.pyc
	pylint src/ --disable=C0114,C0115,C0116 --fail-under=8.0
	@echo "✅ Linting completed"

# Code Formatting
format:
	@echo "✨ Formatting Code..."
	@echo "===================="
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile black
	@echo "✅ Code formatting completed"

# Dependency Compatibility Check
check-deps:
	@echo "🔧 Checking Dependencies..."
	@echo "==========================="
	pip-audit --desc
	pip check
	@echo "✅ Dependency check completed"

# Security Testing
test-security:
	@echo "🛡️ Running Security Tests..."
	@echo "============================="
	bandit -r src/ -f json -o test-results/security-report.json
	safety check --json --output test-results/safety-report.json
	@echo "🔒 Security scan completed"
	@echo "Reports: test-results/security-report.json, test-results/safety-report.json"

# Memory Profiling
test-memory:
	@echo "💾 Running Memory Profiling..."
	@echo "=============================="
	pytest tests/performance/test_ai_engine_performance.py::TestAIEnginePerformance::test_memory_usage_under_load \
		--memray \
		-v
	@echo "✅ Memory profiling completed"

# Database Tests (requires test DB)
test-database:
	@echo "🗄️ Running Database Tests..."
	@echo "============================"
	pytest tests/unit/ tests/integration/ \
		-m database \
		-v \
		--tb=short
	@echo "✅ Database tests completed"

# Stress Testing
test-stress:
	@echo "💪 Running Stress Tests..."
	@echo "=========================="
	pytest tests/performance/ \
		-m "stress or slow" \
		-v \
		--tb=short \
		--durations=0
	@echo "✅ Stress tests completed"

# Clean Test Artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf test-results/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Watch Mode (requires pytest-watch)
test-watch:
	@echo "👀 Starting test watch mode..."
	@echo "Press Ctrl+C to stop"
	ptw tests/ -- --tb=short -q

# Test Specific Component
test-component:
	@if [ -z "$(COMPONENT)" ]; then \
		echo "❌ Usage: make test-component COMPONENT=<component_name>"; \
		echo "Examples:"; \
		echo "  make test-component COMPONENT=ai_engine"; \
		echo "  make test-component COMPONENT=price_analyzer"; \
		exit 1; \
	fi
	@echo "🧪 Testing $(COMPONENT) component..."
	pytest tests/ -k "$(COMPONENT)" -v --tb=short
	@echo "✅ Component $(COMPONENT) tests completed"

# Generate Test Report
test-report: test-all
	@echo "📋 Generating Test Report..."
	@echo "============================"
	@mkdir -p test-results
	@echo "# Wall-E Test Report" > test-results/report.md
	@echo "Generated on: $$(date)" >> test-results/report.md
	@echo "" >> test-results/report.md
	@echo "## Test Coverage" >> test-results/report.md
	@echo "See: htmlcov/complete/index.html" >> test-results/report.md
	@echo "" >> test-results/report.md
	@echo "## Test Results" >> test-results/report.md
	@echo "- Unit Tests: tests/unit/" >> test-results/report.md
	@echo "- Integration Tests: tests/integration/" >> test-results/report.md
	@echo "- Performance Tests: tests/performance/" >> test-results/report.md
	@echo "- E2E Tests: tests/e2e/" >> test-results/report.md
	@echo "✅ Test report generated: test-results/report.md"

# Setup Test Environment
setup-test-env:
	@echo "⚙️ Setting up test environment..."
	@echo "================================="
	@mkdir -p test-results htmlcov logs
	@touch test-results/.gitkeep
	@touch htmlcov/.gitkeep
	@echo "✅ Test environment ready"

# Docker Test Environment
test-docker:
	@echo "🐳 Running tests in Docker..."
	@echo "============================="
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo "✅ Docker tests completed"

# Benchmark Comparison
benchmark:
	@echo "📊 Running Performance Benchmarks..."
	@echo "===================================="
	pytest tests/performance/ \
		--benchmark-only \
		--benchmark-sort=mean \
		--benchmark-json=test-results/benchmark.json
	@echo "📈 Benchmark results: test-results/benchmark.json"

# Test with different Python versions (requires pyenv)
test-python-versions:
	@echo "🐍 Testing with multiple Python versions..."
	@echo "==========================================="
	@for version in 3.9 3.10 3.11; do \
		echo "Testing with Python $$version..."; \
		pyenv local $$version && pytest tests/unit/ -x; \
	done
	@echo "✅ Multi-version testing completed"