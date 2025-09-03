#!/usr/bin/env python3
"""
Unit tests for Dashboard API endpoints (mock tests)
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.dashboard_routes import get_mock_metrics, get_mock_logs


@pytest.mark.asyncio
async def test_get_mock_metrics():
    """Test mock metrics generation"""
    metrics = await get_mock_metrics()
    
    assert metrics.msg_rate > 0
    assert metrics.active_scrapers >= 0
    assert metrics.success_rate >= 0
    assert metrics.avg_response_time > 0
    assert metrics.total_messages_today >= 0
    assert metrics.total_errors_today >= 0
    assert metrics.timestamp is not None


@pytest.mark.asyncio
async def test_get_mock_logs():
    """Test mock logs generation"""
    logs = await get_mock_logs(limit=10)
    
    assert len(logs) == 10
    assert all(log.id for log in logs)
    assert all(log.timestamp for log in logs)
    assert all(log.level in ['info', 'warning', 'error', 'debug'] for log in logs)
    assert all(log.message for log in logs)
    assert all(log.source for log in logs)


def test_dashboard_routes_import():
    """Test that dashboard routes can be imported"""
    from api.dashboard_routes import router, connection_manager
    
    assert router is not None
    assert connection_manager is not None
    assert connection_manager.get_connection_count() == 0


def test_pydantic_models():
    """Test that Pydantic models work correctly"""
    from api.dashboard_routes import MetricsSummary, LogEntry, ConfigUpdate
    
    # Test MetricsSummary
    metrics = MetricsSummary(
        msg_rate=50.0,
        active_scrapers=2,
        success_rate=95.5,
        avg_response_time=2.1,
        total_messages_today=150,
        total_errors_today=5,
        timestamp="2025-01-01T00:00:00Z"
    )
    assert metrics.msg_rate == 50.0
    assert metrics.active_scrapers == 2
    
    # Test LogEntry
    log = LogEntry(
        id="test123",
        timestamp="2025-01-01T00:00:00Z",
        level="info",
        message="Test message",
        source="test"
    )
    assert log.id == "test123"
    assert log.level == "info"
    
    # Test ConfigUpdate
    config_update = ConfigUpdate(
        key="msg_per_hour",
        value=100
    )
    assert config_update.key == "msg_per_hour"
    assert config_update.value == 100
    assert config_update.apply_immediately is True