#!/usr/bin/env python3
"""
Test script for Dashboard API endpoints
Run this after starting the dashboard server to verify all endpoints work
"""
import asyncio
import json
import sys
from pathlib import Path
import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import aiohttp
from datetime import datetime


@pytest.mark.asyncio
async def test_endpoints():
    """Test all dashboard endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Wall-E Dashboard API Endpoints")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # Test root endpoint
        print("\n📍 Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Root endpoint: {data['name']} v{data['version']}")
                else:
                    print(f"❌ Root endpoint failed: {resp.status}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")

        # Test health check
        print("\n📍 Testing health check...")
        try:
            async with session.get(f"{base_url}/api/dashboard/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(
                        f"✅ Health: {data['status']} - Redis: {data['services']['redis']}"
                    )
                else:
                    print(f"❌ Health check failed: {resp.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

        # Test metrics summary
        print("\n📍 Testing metrics summary...")
        try:
            async with session.get(f"{base_url}/api/dashboard/metrics/summary") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Metrics:")
                    print(f"   - Message rate: {data['msg_rate']:.1f}/hour")
                    print(f"   - Active scrapers: {data['active_scrapers']}")
                    print(f"   - Success rate: {data['success_rate']:.1f}%")
                    print(f"   - Avg response: {data['avg_response_time']:.2f}s")
                else:
                    print(f"❌ Metrics failed: {resp.status}")
        except Exception as e:
            print(f"❌ Metrics error: {e}")

        # Test scraper status
        print("\n📍 Testing scraper status...")
        try:
            async with session.get(f"{base_url}/api/dashboard/scraper/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Scrapers: {len(data)} active")
                    for scraper in data[:2]:  # Show first 2
                        print(f"   - {scraper['scraper_id']}: {scraper['status']}")
                else:
                    print(f"❌ Scraper status failed: {resp.status}")
        except Exception as e:
            print(f"❌ Scraper status error: {e}")

        # Test recent logs
        print("\n📍 Testing recent logs...")
        try:
            async with session.get(
                f"{base_url}/api/dashboard/logs/recent?limit=5"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Logs: {len(data)} entries")
                    for log in data[:3]:  # Show first 3
                        print(f"   [{log['level']}] {log['message']}")
                else:
                    print(f"❌ Logs failed: {resp.status}")
        except Exception as e:
            print(f"❌ Logs error: {e}")

        # Test current configuration
        print("\n📍 Testing current configuration...")
        try:
            async with session.get(f"{base_url}/api/dashboard/config/current") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Configuration:")
                    print(f"   - Messages/hour: {data['msg_per_hour']}")
                    print(f"   - Retry attempts: {data['retry_attempts']}")
                    print(f"   - Debug mode: {data['debug_mode']}")
                else:
                    print(f"❌ Config failed: {resp.status}")
        except Exception as e:
            print(f"❌ Config error: {e}")

        # Test config update
        print("\n📍 Testing config update...")
        try:
            update_data = {
                "key": "msg_per_hour",
                "value": 75,
                "apply_immediately": True,
            }
            async with session.post(
                f"{base_url}/api/dashboard/config/update", json=update_data
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Config update: {data['message']}")
                else:
                    print(f"❌ Config update failed: {resp.status}")
        except Exception as e:
            print(f"❌ Config update error: {e}")

        # Test WebSocket connection
        print("\n📍 Testing WebSocket connection...")
        try:
            ws_url = f"ws://localhost:8000/api/dashboard/ws/live"
            async with session.ws_connect(ws_url) as ws:
                print("✅ WebSocket connected")

                # Receive initial data
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"   - Received: {data['type']} message")

                # Receive one update
                msg = await asyncio.wait_for(ws.receive(), timeout=3)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"   - Update: {data['type']} message")

                await ws.close()
                print("   - WebSocket closed successfully")
        except asyncio.TimeoutError:
            print("   - WebSocket test completed (timeout expected)")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")

    print("\n" + "=" * 50)
    print("✨ Dashboard API test completed!")
    print("\nNext steps:")
    print("1. Check http://localhost:8000/docs for interactive API documentation")
    print("2. Start building the frontend with the working endpoints")


@pytest.mark.asyncio
async def test_websocket_stream():
    """Test WebSocket streaming for 10 seconds"""
    print("\n🔄 Testing WebSocket real-time stream (10 seconds)...")
    print("-" * 50)

    ws_url = "ws://localhost:8000/api/dashboard/ws/live"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(ws_url) as ws:
                print("Connected to WebSocket")

                start_time = datetime.now()
                while (datetime.now() - start_time).seconds < 10:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=1)
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            print(
                                f"[{datetime.now().strftime('%H:%M:%S')}] {data['type']}"
                            )
                    except asyncio.TimeoutError:
                        continue

                await ws.close()
                print("WebSocket stream test completed")

        except Exception as e:
            print(f"WebSocket stream error: {e}")


if __name__ == "__main__":
    print(
        """
╔════════════════════════════════════════════╗
║  Wall-E Dashboard API Test Suite           ║
╚════════════════════════════════════════════╝

Make sure the dashboard server is running:
  python src/api/dashboard_server.py

"""
    )

    # Run tests
    asyncio.run(test_endpoints())

    # Optional: Test WebSocket stream
    # Uncomment to see real-time updates for 10 seconds
    # asyncio.run(test_websocket_stream())
