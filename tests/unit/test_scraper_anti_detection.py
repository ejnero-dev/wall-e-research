#!/usr/bin/env python3
"""
Unit tests for Scraper Anti-Detection module
Tests evasion techniques, fingerprinting protection, and human behavior simulation
"""

import pytest
import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scraper.anti_detection import (
    AntiDetectionManager,
    UserAgentRotator,
    FingerprintMasker,
    HumanBehaviorSimulator,
    ProxyManager,
    SessionRotator,
)


class TestAntiDetectionManager:
    """Test suite for AntiDetectionManager class"""

    @pytest.fixture
    def anti_detection(self):
        """Create AntiDetectionManager instance for testing"""
        config = {
            "user_agents_file": "config/user_agents.txt",
            "rotation_interval": 3600,
            "human_delays": {"min": 1, "max": 3},
            "fingerprint_randomization": True,
        }
        return AntiDetectionManager(config)

    def test_initialization(self, anti_detection):
        """Test anti-detection manager initialization"""
        assert anti_detection is not None
        assert hasattr(anti_detection, "user_agent_rotator")
        assert hasattr(anti_detection, "fingerprint_masker")
        assert hasattr(anti_detection, "behavior_simulator")

    def test_session_setup(self, anti_detection):
        """Test browser session setup with anti-detection measures"""
        mock_page = Mock()
        mock_context = Mock()

        with patch("playwright.async_api.async_playwright") as mock_playwright:
            result = anti_detection.setup_session(mock_page, mock_context)

            assert result is True
            # Should have called various anti-detection methods
            assert mock_page.set_extra_http_headers.called
            assert mock_page.add_init_script.called

    def test_fingerprint_randomization(self, anti_detection):
        """Test browser fingerprint randomization"""
        fingerprint = anti_detection.fingerprint_masker.generate_fingerprint()

        assert "userAgent" in fingerprint
        assert "viewport" in fingerprint
        assert "platform" in fingerprint
        assert "languages" in fingerprint
        assert "timezone" in fingerprint

        # Generate another fingerprint - should be different
        fingerprint2 = anti_detection.fingerprint_masker.generate_fingerprint()
        assert fingerprint != fingerprint2

    def test_human_delay_generation(self, anti_detection):
        """Test human-like delay generation"""
        delay1 = anti_detection.behavior_simulator.get_human_delay()
        delay2 = anti_detection.behavior_simulator.get_human_delay()

        # Delays should be within reasonable range
        assert 0.5 <= delay1 <= 5.0
        assert 0.5 <= delay2 <= 5.0

        # Delays should be different (random)
        assert delay1 != delay2

    def test_typing_simulation(self, anti_detection):
        """Test human-like typing simulation"""
        text = "Hello World"
        typing_delays = anti_detection.behavior_simulator.get_typing_delays(text)

        assert len(typing_delays) == len(text)
        # Each character should have a delay
        for delay in typing_delays:
            assert 0.05 <= delay <= 0.3


class TestUserAgentRotator:
    """Test suite for UserAgentRotator class"""

    @pytest.fixture
    def rotator(self):
        """Create UserAgentRotator instance for testing"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
        return UserAgentRotator(user_agents, rotation_interval=3600)

    def test_user_agent_selection(self, rotator):
        """Test user agent selection and rotation"""
        ua1 = rotator.get_current_user_agent()
        ua2 = rotator.get_random_user_agent()

        assert ua1 is not None
        assert ua2 is not None
        assert len(ua1) > 0
        assert len(ua2) > 0

    def test_user_agent_rotation(self, rotator):
        """Test automatic user agent rotation"""
        ua1 = rotator.get_current_user_agent()

        # Force rotation by mocking time
        with patch("time.time", return_value=rotator.last_rotation + 3700):
            rotator.rotate_if_needed()
            ua2 = rotator.get_current_user_agent()

            # Should have rotated
            assert ua1 != ua2

    def test_user_agent_validation(self, rotator):
        """Test user agent format validation"""
        ua = rotator.get_current_user_agent()

        # Should be a valid user agent string
        assert "Mozilla" in ua
        assert "AppleWebKit" in ua or "Gecko" in ua

        # Should not contain suspicious patterns
        assert "bot" not in ua.lower()
        assert "crawler" not in ua.lower()
        assert "spider" not in ua.lower()


class TestFingerprintMasker:
    """Test suite for FingerprintMasker class"""

    @pytest.fixture
    def masker(self):
        """Create FingerprintMasker instance for testing"""
        return FingerprintMasker(randomize_canvas=True, randomize_webgl=True)

    def test_canvas_fingerprint_masking(self, masker):
        """Test canvas fingerprint randomization"""
        script = masker.get_canvas_masking_script()

        assert "HTMLCanvasElement.prototype.toDataURL" in script
        assert "getImageData" in script
        # Should inject noise into canvas operations

    def test_webgl_fingerprint_masking(self, masker):
        """Test WebGL fingerprint randomization"""
        script = masker.get_webgl_masking_script()

        assert "WebGLRenderingContext.prototype.getParameter" in script
        assert "WEBGL_debug_renderer_info" in script
        # Should spoof WebGL parameters

    def test_timezone_randomization(self, masker):
        """Test timezone randomization"""
        timezone1 = masker.get_random_timezone()
        timezone2 = masker.get_random_timezone()

        assert timezone1 is not None
        assert timezone2 is not None
        # Should be valid timezone strings
        assert "/" in timezone1  # Format: Continent/City
        assert "/" in timezone2

    def test_language_randomization(self, masker):
        """Test browser language randomization"""
        languages = masker.get_random_languages()

        assert isinstance(languages, list)
        assert len(languages) >= 1
        # Should be valid language codes
        for lang in languages:
            assert len(lang) >= 2
            assert "-" in lang or len(lang) == 2

    def test_viewport_randomization(self, masker):
        """Test viewport size randomization"""
        viewport1 = masker.get_random_viewport()
        viewport2 = masker.get_random_viewport()

        assert "width" in viewport1 and "height" in viewport1
        assert "width" in viewport2 and "height" in viewport2

        # Should be realistic viewport sizes
        assert 800 <= viewport1["width"] <= 2560
        assert 600 <= viewport1["height"] <= 1440

        # Should be different
        assert viewport1 != viewport2


class TestHumanBehaviorSimulator:
    """Test suite for HumanBehaviorSimulator class"""

    @pytest.fixture
    def simulator(self):
        """Create HumanBehaviorSimulator instance for testing"""
        config = {
            "min_delay": 1.0,
            "max_delay": 3.0,
            "typing_speed_wpm": 60,
            "mouse_movement_enabled": True,
        }
        return HumanBehaviorSimulator(config)

    def test_reading_delay_calculation(self, simulator):
        """Test reading delay calculation based on content"""
        short_text = "Hello"
        long_text = "This is a much longer text that should take more time to read."

        short_delay = simulator.calculate_reading_delay(short_text)
        long_delay = simulator.calculate_reading_delay(long_text)

        assert short_delay < long_delay
        assert short_delay > 0
        assert long_delay > 0

    def test_scroll_behavior_simulation(self, simulator):
        """Test human-like scrolling behavior"""
        scroll_actions = simulator.generate_scroll_behavior(page_height=2000)

        assert isinstance(scroll_actions, list)
        assert len(scroll_actions) > 0

        for action in scroll_actions:
            assert "pixels" in action
            assert "delay" in action
            assert action["pixels"] > 0
            assert action["delay"] > 0

    def test_mouse_movement_simulation(self, simulator):
        """Test random mouse movement generation"""
        movements = simulator.generate_mouse_movements(duration=5.0)

        assert isinstance(movements, list)

        for movement in movements:
            assert "x" in movement and "y" in movement
            assert "timestamp" in movement
            assert 0 <= movement["x"] <= 1920  # Assuming max screen width
            assert 0 <= movement["y"] <= 1080  # Assuming max screen height

    def test_focus_simulation(self, simulator):
        """Test window focus/blur simulation"""
        focus_events = simulator.generate_focus_events(session_duration=300)

        assert isinstance(focus_events, list)

        for event in focus_events:
            assert event["type"] in ["focus", "blur"]
            assert "timestamp" in event
            assert event["timestamp"] >= 0

    def test_idle_time_simulation(self, simulator):
        """Test realistic idle time generation"""
        idle_time1 = simulator.get_idle_time()
        idle_time2 = simulator.get_idle_time()

        assert idle_time1 > 0
        assert idle_time2 > 0
        assert idle_time1 != idle_time2  # Should be random


class TestProxyManager:
    """Test suite for ProxyManager class"""

    @pytest.fixture
    def proxy_manager(self):
        """Create ProxyManager instance for testing"""
        proxy_list = [
            {"host": "1.2.3.4", "port": 8080, "type": "http"},
            {"host": "5.6.7.8", "port": 3128, "type": "https"},
            {"host": "9.10.11.12", "port": 1080, "type": "socks5"},
        ]
        return ProxyManager(proxy_list, rotation_interval=300)

    def test_proxy_selection(self, proxy_manager):
        """Test proxy selection and rotation"""
        proxy1 = proxy_manager.get_current_proxy()
        proxy2 = proxy_manager.get_random_proxy()

        assert proxy1 is not None
        assert proxy2 is not None
        assert "host" in proxy1 and "port" in proxy1

    def test_proxy_health_checking(self, proxy_manager):
        """Test proxy health checking"""
        proxy = {"host": "1.2.3.4", "port": 8080, "type": "http"}

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response

            is_healthy = asyncio.run(proxy_manager.check_proxy_health(proxy))
            assert is_healthy is True

    def test_proxy_rotation(self, proxy_manager):
        """Test automatic proxy rotation"""
        proxy1 = proxy_manager.get_current_proxy()

        # Force rotation
        proxy_manager.force_rotation()
        proxy2 = proxy_manager.get_current_proxy()

        # Should have rotated to different proxy
        assert proxy1 != proxy2

    def test_proxy_blacklisting(self, proxy_manager):
        """Test proxy blacklisting for failed proxies"""
        proxy = {"host": "1.2.3.4", "port": 8080, "type": "http"}

        proxy_manager.blacklist_proxy(proxy)

        # Should not return blacklisted proxy
        available_proxies = proxy_manager.get_available_proxies()
        assert proxy not in available_proxies


class TestSessionRotator:
    """Test suite for SessionRotator class"""

    @pytest.fixture
    def session_rotator(self):
        """Create SessionRotator instance for testing"""
        return SessionRotator(session_timeout=1800, max_requests_per_session=100)

    def test_session_creation(self, session_rotator):
        """Test browser session creation and management"""
        session_id = session_rotator.create_session()

        assert session_id is not None
        assert session_id in session_rotator.active_sessions

        session_info = session_rotator.get_session_info(session_id)
        assert session_info is not None
        assert "created_at" in session_info
        assert "request_count" in session_info

    def test_session_timeout_handling(self, session_rotator):
        """Test automatic session timeout and cleanup"""
        session_id = session_rotator.create_session()

        # Mock expired session
        session_rotator.active_sessions[session_id][
            "created_at"
        ] = datetime.now() - timedelta(hours=1)

        is_valid = session_rotator.is_session_valid(session_id)
        assert is_valid is False

        # Should clean up expired session
        session_rotator.cleanup_expired_sessions()
        assert session_id not in session_rotator.active_sessions

    def test_request_count_tracking(self, session_rotator):
        """Test request count tracking per session"""
        session_id = session_rotator.create_session()

        # Simulate requests
        for i in range(5):
            session_rotator.increment_request_count(session_id)

        session_info = session_rotator.get_session_info(session_id)
        assert session_info["request_count"] == 5

    def test_session_rotation_trigger(self, session_rotator):
        """Test automatic session rotation based on limits"""
        session_id = session_rotator.create_session()

        # Exceed request limit
        for i in range(101):
            session_rotator.increment_request_count(session_id)

        should_rotate = session_rotator.should_rotate_session(session_id)
        assert should_rotate is True


@pytest.mark.integration
class TestAntiDetectionIntegration:
    """Integration tests for anti-detection system"""

    def test_full_anti_detection_pipeline(self):
        """Test complete anti-detection pipeline"""
        config = {
            "user_agents_file": None,  # Use default
            "rotation_interval": 300,
            "human_delays": {"min": 0.1, "max": 0.5},  # Faster for tests
            "fingerprint_randomization": True,
        }

        anti_detection = AntiDetectionManager(config)

        # Test session setup
        mock_page = Mock()
        mock_context = Mock()

        success = anti_detection.setup_session(mock_page, mock_context)
        assert success is True

        # Verify anti-detection measures were applied
        assert mock_page.set_extra_http_headers.called
        assert mock_page.add_init_script.called

    def test_detection_evasion_techniques(self):
        """Test various detection evasion techniques"""
        config = {"fingerprint_randomization": True}
        anti_detection = AntiDetectionManager(config)

        # Test multiple fingerprint generations
        fingerprints = []
        for i in range(5):
            fp = anti_detection.fingerprint_masker.generate_fingerprint()
            fingerprints.append(fp)

        # All fingerprints should be unique
        unique_fingerprints = set(str(fp) for fp in fingerprints)
        assert len(unique_fingerprints) == len(fingerprints)

    def test_stealth_mode_activation(self):
        """Test stealth mode with maximum evasion"""
        config = {
            "stealth_mode": True,
            "fingerprint_randomization": True,
            "proxy_rotation": True,
            "user_agent_rotation": True,
            "canvas_masking": True,
            "webgl_masking": True,
        }

        anti_detection = AntiDetectionManager(config)

        # Should have all evasion techniques enabled
        assert anti_detection.fingerprint_masker.randomize_canvas is True
        assert anti_detection.fingerprint_masker.randomize_webgl is True
        assert anti_detection.user_agent_rotator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
