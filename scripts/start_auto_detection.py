#!/usr/bin/env python3
"""
Auto-Detection Service Launcher for Wall-E
Starts the automatic product detection system as a background service
"""
import asyncio
import signal
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auto_detection import DetectionManager
from scraper.session_manager import AuthMethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/auto_detection.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class AutoDetectionService:
    """Service wrapper for auto-detection system"""

    def __init__(self, config_file: str = None):
        self.detection_manager = None
        self.is_running = False
        self.config_file = config_file

        # Service configuration
        self.config = {
            "scan_interval_minutes": 10,
            "auto_add_enabled": True,
            "notification_enabled": True,
            "dashboard_url": "http://localhost:8000/api/dashboard",
            "auth_method": "auto",
            "max_retries": 3,
            "retry_delay_minutes": 5,
        }

        # Load config if provided
        if config_file:
            self._load_config(config_file)

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("AutoDetectionService initialized")

    def _load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            import json

            with open(config_file, "r") as f:
                file_config = json.load(f)

            self.config.update(file_config)
            logger.info(f"Configuration loaded from {config_file}")

        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False

    async def start(self) -> bool:
        """Start the auto-detection service"""
        logger.info("Starting Auto-Detection Service")

        try:
            # Initialize detection manager
            auth_method = AuthMethod.AUTO
            if self.config["auth_method"] == "cookies":
                auth_method = AuthMethod.COOKIES
            elif self.config["auth_method"] == "credentials":
                auth_method = AuthMethod.CREDENTIALS

            self.detection_manager = DetectionManager(
                dashboard_api_url=self.config["dashboard_url"]
            )

            # Configure detection manager
            self.detection_manager.update_config(
                {
                    "scan_interval_minutes": self.config["scan_interval_minutes"],
                    "auto_respond_new_products": True,
                    "ai_personality": "professional",
                    "response_delay_min": 15,
                    "response_delay_max": 60,
                }
            )

            self.detection_manager.set_auto_add_enabled(self.config["auto_add_enabled"])
            self.detection_manager.set_notification_enabled(
                self.config["notification_enabled"]
            )

            # Start detection manager with retries
            retries = 0
            while retries < self.config["max_retries"]:
                try:
                    success = await self.detection_manager.start()

                    if success:
                        logger.info("Auto-detection system started successfully")
                        self.is_running = True
                        return True
                    else:
                        retries += 1
                        logger.warning(
                            f"Failed to start detection manager (attempt {retries}/{self.config['max_retries']})"
                        )

                        if retries < self.config["max_retries"]:
                            await asyncio.sleep(self.config["retry_delay_minutes"] * 60)

                except Exception as e:
                    retries += 1
                    logger.error(
                        f"Error starting detection manager (attempt {retries}/{self.config['max_retries']}): {e}"
                    )

                    if retries < self.config["max_retries"]:
                        await asyncio.sleep(self.config["retry_delay_minutes"] * 60)

            logger.error(f"Failed to start after {self.config['max_retries']} attempts")
            return False

        except Exception as e:
            logger.error(f"Critical error starting service: {e}")
            return False

    async def stop(self):
        """Stop the auto-detection service"""
        logger.info("Stopping Auto-Detection Service")
        self.is_running = False

        if self.detection_manager:
            try:
                await self.detection_manager.stop()
                logger.info("Detection manager stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping detection manager: {e}")

    async def run(self):
        """Main service loop"""
        if not await self.start():
            logger.error("Failed to start service")
            return 1

        logger.info("Auto-Detection Service running...")

        # Service monitoring loop
        last_health_check = datetime.now()
        health_check_interval = 300  # 5 minutes

        try:
            while self.is_running:
                current_time = datetime.now()

                # Periodic health check
                if (current_time - last_health_check).seconds >= health_check_interval:
                    await self._health_check()
                    last_health_check = current_time

                # Sleep briefly to avoid busy loop
                await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"Error in service loop: {e}")
        finally:
            await self.stop()

        logger.info("Auto-Detection Service stopped")
        return 0

    async def _health_check(self):
        """Perform health check and restart if needed"""
        try:
            if not self.detection_manager or not self.detection_manager.is_running:
                logger.warning("Detection manager not running, attempting restart...")

                if self.detection_manager:
                    await self.detection_manager.stop()

                # Reinitialize and restart
                await asyncio.sleep(30)  # Wait before restart

                success = await self.start()
                if not success:
                    logger.error("Failed to restart detection manager")
                    self.is_running = False
                else:
                    logger.info("Detection manager restarted successfully")

            else:
                # Get status for logging
                status = self.detection_manager.get_status()
                logger.info(
                    f"Health check passed - Status: {status['detection_manager']['is_running']}"
                )

        except Exception as e:
            logger.error(f"Error in health check: {e}")

    def get_status(self):
        """Get service status"""
        if not self.detection_manager:
            return {"service": "stopped", "detection_manager": "not_initialized"}

        return {
            "service": "running" if self.is_running else "stopped",
            "detection_manager": self.detection_manager.get_status(),
            "config": self.config,
        }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Wall-E Auto-Detection Service")
    parser.add_argument(
        "--config", type=str, help="Configuration file path", default=None
    )
    parser.add_argument(
        "--scan-interval",
        type=int,
        help="Scan interval in minutes (default: 10)",
        default=10,
    )
    parser.add_argument(
        "--dashboard-url",
        type=str,
        help="Dashboard API URL",
        default="http://localhost:8000/api/dashboard",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually adding products to dashboard",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create service
    service = AutoDetectionService(args.config)

    # Override config with command line arguments
    if args.scan_interval:
        service.config["scan_interval_minutes"] = args.scan_interval

    if args.dashboard_url:
        service.config["dashboard_url"] = args.dashboard_url

    if args.dry_run:
        service.config["auto_add_enabled"] = False
        logger.info("Running in dry-run mode (products will not be added to dashboard)")

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    logger.info("=" * 50)
    logger.info("Wall-E Auto-Detection Service Starting")
    logger.info(f"Scan interval: {service.config['scan_interval_minutes']} minutes")
    logger.info(f"Dashboard URL: {service.config['dashboard_url']}")
    logger.info(f"Auto-add enabled: {service.config['auto_add_enabled']}")
    logger.info("=" * 50)

    # Run service
    exit_code = await service.run()

    logger.info("=" * 50)
    logger.info("Wall-E Auto-Detection Service Finished")
    logger.info("=" * 50)

    return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
