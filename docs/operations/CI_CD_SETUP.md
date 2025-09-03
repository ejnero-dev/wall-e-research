# CI/CD Pipeline Setup Guide

## Overview
This document describes the comprehensive CI/CD pipeline setup for the Wallapop Automation Bot project using GitHub Actions.

## Pipeline Features

### 🔍 Code Quality Checks
- **Black**: Code formatting enforcement (88 character line length)
- **Flake8**: Linting with custom rules and import order checking
- **MyPy**: Type checking (lenient configuration for gradual adoption)
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking

### 🧪 Testing Strategy
- **Multi-version testing**: Python 3.11 and 3.12
- **Service dependencies**: PostgreSQL 15 and Redis 7 for integration tests
- **Parallel execution**: Using pytest-xdist for faster test execution
- **Coverage reporting**: Integrated with Codecov for coverage tracking
- **Browser automation**: Playwright with Chromium for web scraping tests

### 🚀 Build & Deployment
- **Docker build testing**: Validates Docker configuration if present
- **Dependency caching**: Optimized pip cache for faster builds
- **Artifact collection**: Security reports and test results
- **Branch protection**: Runs on main/master pushes and pull requests

## File Structure
```
.github/
├── workflows/
│   └── ci.yml                 # Main CI/CD pipeline
├── ISSUE_TEMPLATE/
│   ├── bug_report.md          # Bug report template
│   ├── feature_request.md     # Feature request template
│   └── config.yml             # Issue template configuration
└── pull_request_template.md   # PR template

# Configuration files
.flake8                        # Flake8 linting configuration
.gitignore                     # Git ignore patterns
.pre-commit-config.yaml        # Pre-commit hooks
pyproject.toml                 # Tool configurations (Black, isort, MyPy, etc.)
requirements-dev.txt           # Development dependencies
```

## Pipeline Jobs

### 1. Code Quality (`lint-and-format`)
- Runs code formatting checks
- Performs linting and security scanning
- Uploads security reports as artifacts
- Fast feedback for code quality issues

### 2. Testing (`test`)
- Matrix strategy for Python 3.11 and 3.12
- Sets up PostgreSQL and Redis services
- Installs system and Python dependencies
- Runs unit and integration tests separately
- Generates coverage reports
- Uploads coverage to Codecov

### 3. Docker Build (`docker-build`)
- Tests Docker build process
- Only runs on pull requests
- Validates containerization setup

### 4. Security Scan (`security-scan`)
- Scans dependencies for vulnerabilities
- Generates security reports
- Runs independently for faster feedback

### 5. Dependency Review (`dependency-review`)
- Reviews dependency changes in PRs
- Identifies potential security issues
- Prevents vulnerable dependencies

## Local Development Setup

### Quick Start
```bash
# Run the setup script
python scripts/setup_dev.py

# Or manually:
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
python -m spacy download es_core_news_sm
playwright install chromium
```

### Pre-commit Hooks
The project includes comprehensive pre-commit hooks that run automatically:
- File formatting and cleanup
- Import sorting with isort
- Code formatting with Black
- Linting with Flake8
- Security checking with Bandit
- Type checking with MyPy
- Syntax upgrades with pyupgrade
- Unused import removal
- Spell checking

### Running Tests Locally
```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Parallel execution
pytest -n auto
```

### Code Quality Checks
```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Environment Variables

### Testing Environment
The CI pipeline sets these environment variables for testing:
```yaml
DATABASE_URL: postgresql://test_user:test_password@localhost:5432/wallapop_test
REDIS_URL: redis://localhost:6379/0
TESTING: true
```

### Required Secrets
For full functionality, add these secrets to your GitHub repository:
- `CODECOV_TOKEN`: For coverage reporting (optional)

## Performance Optimizations

### Caching Strategy
- **Pip cache**: Cached by Python version and requirements file hashes
- **Playwright browsers**: Cached to avoid repeated downloads
- **Pre-commit**: Cached to speed up hook execution

### Parallel Execution
- Tests run in parallel using pytest-xdist
- Multiple Python versions tested concurrently
- Independent job execution for faster feedback

### Service Health Checks
- PostgreSQL and Redis include health checks
- Ensures services are ready before tests start
- Prevents flaky test failures

## Monitoring & Reporting

### Artifacts
- Security reports (Bandit, Safety)
- Test coverage reports
- Build logs and test results

### Status Badges
The README includes status badges for:
- CI/CD pipeline status
- Code coverage
- Code style (Black)
- Security scanning (Bandit)
- Python version support

## Best Practices

### Branch Protection
Configure branch protection rules:
- Require status checks to pass
- Require up-to-date branches
- Require code review
- Restrict force pushes

### Pull Request Workflow
1. Create feature branch
2. Make changes with frequent commits
3. Run pre-commit hooks locally
4. Push and create pull request
5. CI pipeline runs automatically
6. Address any failures
7. Request code review
8. Merge after approval

### Security Considerations
- Dependency vulnerability scanning
- Security linting with Bandit
- No secrets in code or configuration
- Regular security updates via Dependabot

## Troubleshooting

### Common Issues

#### Failed Tests
- Check service availability (PostgreSQL, Redis)
- Verify environment variables
- Check for test isolation issues

#### Linting Failures
- Run `black src/ tests/` to fix formatting
- Address Flake8 warnings manually
- Update type hints for MyPy issues

#### Security Warnings
- Review Bandit findings carefully
- Use `# nosec` comments for false positives
- Update vulnerable dependencies

#### Performance Issues
- Check cache hit rates
- Optimize test execution order
- Review parallel execution settings

### Getting Help
- Check the issue templates for bug reports
- Review existing issues and discussions
- Follow the contribution guidelines
- Use the pull request template for changes

## Future Enhancements

### Planned Improvements
- Automated dependency updates with Dependabot
- Performance regression testing
- Automated deployment to staging
- Integration with monitoring systems
- Advanced security scanning (SAST/DAST)

### Metrics Collection
- Build time tracking
- Test execution performance
- Coverage trend analysis
- Security vulnerability trends