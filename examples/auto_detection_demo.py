#!/usr/bin/env python3
"""
Wall-E Auto-Detection System Demo
Simple demonstration of automatic product detection capabilities
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auto_detection import DetectionManager
from auto_detection.notifications import notification_manager, NotificationChannel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_auto_detection():
    """Demonstrate auto-detection system functionality"""
    
    print("🤖 Wall-E Auto-Detection System Demo")
    print("=" * 50)
    
    # Initialize detection manager
    print("📡 Initializing Detection Manager...")
    manager = DetectionManager(dashboard_api_url="http://localhost:8000/api/dashboard")
    
    # Configure notifications for demo
    notification_manager.configure({
        "console": {"enabled": True},
        "file": {"enabled": True, "log_file": "logs/demo_notifications.log"},
        "websocket": {"enabled": False}  # Disable WebSocket for demo
    })
    
    # Subscribe to notifications
    def on_notification(notification):
        print(f"📢 Notification: {notification['title']}")
        print(f"   Message: {notification['message']}")
        print(f"   Type: {notification['type']}")
        print()
    
    notification_manager.subscribe(NotificationChannel.CONSOLE, on_notification)
    
    # Configure detection manager
    print("⚙️  Configuring Detection Manager...")
    manager.update_config({
        "scan_interval_minutes": 1,  # Fast for demo (1 minute)
        "auto_respond_new_products": True,
        "ai_personality": "professional",
        "enable_notifications": True
    })
    
    # Disable auto-add for demo (we'll just detect, not add to dashboard)
    manager.set_auto_add_enabled(False)
    manager.set_notification_enabled(True)
    
    print("✅ Configuration complete!")
    print()
    
    # Get initial status
    print("📊 Initial Status:")
    status = manager.get_status()
    print(f"   Detection Manager Running: {status['detection_manager']['is_running']}")
    print(f"   Scanner Status: {status['scanner']['status']}")
    print(f"   Known Products: {status['scanner']['known_products_count']}")
    print()
    
    # Demonstrate manual scan (this will fail without authentication, but shows the flow)
    print("🔍 Attempting Manual Scan (demo mode)...")
    try:
        scan_result = await manager.manual_scan()
        
        if scan_result.get("success"):
            print(f"✅ Scan successful!")
            print(f"   Duration: {scan_result.get('duration_seconds', 0):.1f}s")
            print(f"   Total products: {scan_result.get('total_products', 0)}")
            print(f"   New products: {scan_result.get('new_products', 0)}")
            print(f"   Changed products: {scan_result.get('changed_products', 0)}")
        else:
            print(f"ℹ️  Scan failed (expected without authentication): {scan_result.get('error', 'Unknown error')}")
            print("   This is normal in demo mode - authentication is required for real scanning")
    
    except Exception as e:
        print(f"ℹ️  Scan failed (expected): {e}")
        print("   This is normal in demo mode - authentication is required for real scanning")
    
    print()
    
    # Show available API endpoints
    print("🌐 Available API Endpoints:")
    endpoints = [
        "GET  /api/dashboard/auto-detection/status",
        "POST /api/dashboard/auto-detection/start", 
        "POST /api/dashboard/auto-detection/stop",
        "POST /api/dashboard/auto-detection/scan",
        "GET  /api/dashboard/auto-detection/config",
        "PUT  /api/dashboard/auto-detection/config",
        "GET  /api/dashboard/auto-detection/statistics",
        "GET  /api/dashboard/auto-detection/detected-products"
    ]
    
    for endpoint in endpoints:
        print(f"   • {endpoint}")
    
    print()
    
    # Show statistics
    print("📈 Statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        if key != "uptime_start":
            print(f"   {key}: {value}")
    
    print()
    
    # Demonstrate notification system
    print("🔔 Testing Notification System...")
    
    # Send test notifications
    await notification_manager.notify_new_product({
        "title": "Demo iPhone 15",
        "price": 800,
        "url": "https://wallapop.com/item/demo-iphone-123"
    })
    
    await asyncio.sleep(1)
    
    await notification_manager.notify_product_changed({
        "title": "Demo MacBook", 
        "price": 1200,
        "url": "https://wallapop.com/item/demo-macbook-456"
    }, ["price: €1500 → €1200"])
    
    await asyncio.sleep(1)
    
    print("✅ Demo notifications sent!")
    print()
    
    print("🎯 Next Steps:")
    print("   1. Configure authentication in Wallapop scraper")
    print("   2. Start the detection service: python scripts/start_auto_detection.py")
    print("   3. Or integrate with dashboard: POST /api/dashboard/auto-detection/start")
    print("   4. Monitor logs in: logs/auto_detection.log")
    print("   5. View detected products in dashboard")
    print()
    
    print("🎉 Demo Complete!")
    print("   The auto-detection system is ready for production use.")
    print("   See docs/AUTO_DETECTION_SYSTEM.md for full documentation.")


async def main():
    """Main demo entry point"""
    try:
        await demo_auto_detection()
        return 0
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)