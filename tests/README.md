# Wall-E Test Suite Documentation

## Overview

The Wall-E test suite provides comprehensive testing coverage for all system components, ensuring reliability, performance, and maintainability. The test architecture follows industry best practices with clear separation between test categories.

## Test Structure

```
tests/
├── unit/                    # Unit tests - Fast, isolated component testing
│   ├── test_ai_engine_basic.py         # AI Engine core functionality
│   ├── test_conversation_engine.py     # Conversation management
│   ├── test_dashboard_api.py           # Dashboard API endpoints
│   ├── test_config_system.py           # Configuration management
│   ├── test_price_analyzer.py          # Price analysis algorithms
│   └── test_scraper_anti_detection.py  # Anti-detection mechanisms
├── integration/             # Integration tests - Component interactions
│   ├── test_ai_engine_integration.py   # AI Engine with other systems
│   ├── test_bot_ai_integration.py      # Bot orchestration
│   ├── test_happy_path.py              # Standard user workflows
│   ├── test_research_integration.py    # Research mode testing
│   └── test_scraper.py                 # Scraper system integration
├── performance/             # Performance tests - Speed & load benchmarks
│   └── test_ai_engine_performance.py   # AI response time & concurrency
├── e2e/                     # End-to-end tests - Complete workflows
│   └── test_complete_workflow.py       # Full conversation cycles
├── fixtures/                # Test data and mock objects
│   └── test_responses.json             # Mock conversation responses
└── conftest.py             # Global test configuration and fixtures
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (<1 second per test)
- **Dependencies**: Minimal, heavily mocked
- **Coverage Target**: >90% for critical components
- **Run Command**: `make test-unit`

### Integration Tests  
- **Purpose**: Test component interactions and data flow
- **Speed**: Medium (1-10 seconds per test)
- **Dependencies**: Multiple components, some real services
- **Coverage Target**: >80% of integration points
- **Run Command**: `make test-integration`

### Performance Tests
- **Purpose**: Validate response times and resource usage
- **Speed**: Slow (10+ seconds per test)
- **Dependencies**: Real or realistic mock services
- **Targets**: 
  - AI Engine response: <3 seconds
  - Concurrent conversations: 10+
  - Memory usage: <80% system RAM
- **Run Command**: `make test-performance`

### End-to-End Tests
- **Purpose**: Validate complete user workflows
- **Speed**: Slow (30+ seconds per test)
- **Dependencies**: Full system integration
- **Coverage**: Critical business processes
- **Run Command**: `make test-e2e`

## Test Markers

### Category Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.e2e` - End-to-end tests

### Component Markers
- `@pytest.mark.ai_engine` - AI Engine tests
- `@pytest.mark.price_analyzer` - Price analysis tests
- `@pytest.mark.scraper` - Web scraping tests
- `@pytest.mark.conversation_engine` - Conversation tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.api` - API endpoint tests

### Characteristic Markers
- `@pytest.mark.slow` - Slow-running tests (>5s)
- `@pytest.mark.fast` - Fast tests (<1s)
- `@pytest.mark.memory_intensive` - High memory usage
- `@pytest.mark.network` - Requires network access

### Environment Markers
- `@pytest.mark.requires_ollama` - Needs Ollama LLM server
- `@pytest.mark.requires_redis` - Needs Redis server
- `@pytest.mark.requires_postgres` - Needs PostgreSQL
- `@pytest.mark.requires_playwright` - Needs browser automation

## Running Tests

### Quick Start
```bash
# Install test dependencies
make install-deps

# Run basic test suite
make test-unit

# Run all tests
make test-all
```

### Specific Test Categories
```bash
# Unit tests only (fastest)
make test-unit

# Integration tests
make test-integration  

# Performance benchmarks
make test-performance

# End-to-end workflows
make test-e2e

# Complete test suite with coverage
make test-coverage
```

### Targeted Testing
```bash
# Test specific component
make test-component COMPONENT=ai_engine

# Test with specific markers
pytest -m "unit and ai_engine"
pytest -m "integration and not slow"
pytest -m "performance"

# Test specific file
pytest tests/unit/test_ai_engine_basic.py -v

# Test specific function
pytest tests/unit/test_ai_engine_basic.py::test_imports -v
```

### CI/CD Testing
```bash
# CI-optimized test run
make ci-test

# Performance benchmarks for CI
make ci-performance

# Parallel execution
make test-parallel
```

## Performance Targets

### AI Engine
- **Single Request**: <3 seconds response time
- **Concurrent Requests**: Handle 10+ simultaneous conversations
- **Memory Usage**: <100MB per conversation thread
- **Success Rate**: >95% under normal load

### Scraper System
- **Page Load Time**: <5 seconds average
- **Anti-Detection**: >90% evasion success rate
- **Session Duration**: >30 minutes average
- **Error Recovery**: <10 seconds for retry cycles

### Price Analyzer
- **Analysis Time**: <2 seconds for market analysis
- **Data Accuracy**: >85% confidence score
- **Cache Hit Rate**: >70% for repeated queries
- **API Response**: <1 second for cached results

### Database Operations
- **Query Response**: <100ms for standard queries
- **Connection Pool**: Handle 50+ concurrent connections
- **Cache Performance**: <10ms for Redis operations
- **Backup Time**: <5 minutes for daily backup

## Coverage Requirements

### Critical Components (>90% coverage required)
- AI Engine core functionality
- Fraud detection algorithms  
- Price analysis calculations
- Anti-detection mechanisms
- Database operations

### Important Components (>80% coverage required)
- Conversation state management
- API endpoints
- Configuration management
- Error handling
- Session management

### Supporting Components (>70% coverage required)
- Utility functions
- Logging systems
- Monitoring integrations
- Dashboard components

## Test Data Management

### Fixtures
- **Location**: `tests/fixtures/`
- **Purpose**: Reusable test data and mock objects
- **Format**: JSON files for structured data
- **Updates**: Version-controlled with schema validation

### Mock Services
- **AI Engine**: Template-based responses for fast testing
- **Database**: In-memory SQLite for unit tests
- **External APIs**: HTTP mocking with realistic responses
- **Browser**: Playwright mock pages for scraper tests

## Debugging Tests

### Verbose Output
```bash
# Run with detailed output
pytest -v -s tests/unit/test_ai_engine_basic.py

# Show test durations
pytest --durations=10 tests/

# Show coverage gaps
pytest --cov=src --cov-report=html tests/
```

### Debug Specific Issues
```bash
# Run failing test only
pytest --lf tests/

# Stop on first failure
pytest -x tests/

# Enter debugger on failure  
pytest --pdb tests/

# Show local variables
pytest --tb=long tests/
```

## Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: make install-deps
      - name: Run tests
        run: make ci-test
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Quality Gates
- **Unit Tests**: Must pass 100%
- **Integration Tests**: Must pass >95%
- **Coverage**: Must maintain >80% overall
- **Performance**: Must meet response time targets
- **Security**: No high-severity issues

## Best Practices

### Writing Tests
1. **Descriptive Names**: Test names should explain the scenario
2. **AAA Pattern**: Arrange, Act, Assert structure
3. **Single Responsibility**: One concept per test
4. **Independent Tests**: No dependencies between tests
5. **Realistic Data**: Use representative test data

### Test Organization
1. **Logical Grouping**: Group related tests in classes
2. **Proper Markers**: Tag tests with appropriate markers
3. **Clear Documentation**: Comment complex test scenarios
4. **Fixture Reuse**: Leverage fixtures for common setup
5. **Mock Strategically**: Mock external dependencies only

### Performance Considerations
1. **Parallel Execution**: Use pytest-xdist for speed
2. **Test Selection**: Run relevant tests for changes
3. **Cache Results**: Cache expensive setup operations
4. **Resource Cleanup**: Properly clean up test resources
5. **Realistic Timing**: Use appropriate timeouts

## Troubleshooting

### Common Issues

#### Tests Failing in CI but Passing Locally
- Check environment differences (Python version, dependencies)
- Verify test isolation (no shared state)
- Review timing-sensitive tests
- Ensure proper cleanup between tests

#### Slow Test Execution
- Profile test execution with `--durations=0`
- Identify and optimize slow tests
- Use parallel execution (`make test-parallel`)
- Mock expensive external calls

#### Coverage Gaps
- Run `pytest --cov=src --cov-report=html tests/`
- Review `htmlcov/index.html` for uncovered lines
- Add tests for critical uncovered code
- Update coverage thresholds as needed

#### Memory Issues
- Use `pytest --memray` for memory profiling
- Check for memory leaks in long-running tests
- Optimize fixture cleanup
- Limit concurrent test execution

## Contributing

### Adding New Tests
1. Choose appropriate test category (unit/integration/performance/e2e)
2. Follow existing naming conventions
3. Add proper markers and documentation
4. Ensure tests are isolated and deterministic
5. Update this README if adding new test patterns

### Modifying Existing Tests
1. Maintain backward compatibility when possible
2. Update related documentation
3. Verify impact on coverage metrics
4. Test changes in CI environment

### Performance Tests
1. Set realistic performance targets
2. Use consistent test environments
3. Document performance assumptions  
4. Include both success and failure scenarios
5. Monitor performance trends over time

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Coverage](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Wall-E Architecture Documentation](../docs/development/ARCHITECTURE_OVERVIEW.md)