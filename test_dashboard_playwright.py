#!/usr/bin/env python3
"""
Test dashboard functionality with Playwright
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_dashboard():
    """Test basic dashboard functionality"""
    
    async with async_playwright() as p:
        print("🎭 Iniciando Playwright...")
        
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\n🔍 Testing Backend API...")
            
            # Test backend health endpoint
            response = await page.request.get("http://localhost:8000/api/dashboard/health")
            if response.ok:
                health_data = await response.json()
                print(f"✅ Backend Health: {health_data['status']}")
                print(f"   Services: {', '.join(health_data['services'].keys())}")
            else:
                print(f"❌ Backend Health Check failed: {response.status}")
                return False
            
            print("\n🎨 Testing Frontend...")
            
            # Navigate to frontend
            print("   Loading frontend at http://localhost:8080...")
            await page.goto("http://localhost:8080", wait_until="networkidle")
            
            # Check if page loaded
            title = await page.title()
            print(f"   Page title: {title}")
            
            # Wait for React app to load
            await page.wait_for_selector("[data-testid], .container, main, #root", timeout=10000)
            
            # Take screenshot for verification
            await page.screenshot(path="debug/screenshots/dashboard_test.png")
            print("   Screenshot saved to debug/screenshots/dashboard_test.png")
            
            # Check for key dashboard elements
            print("\n🧪 Checking Dashboard Components...")
            
            # Look for common dashboard elements
            selectors_to_check = [
                'h1, h2, .dashboard-title, [data-testid="dashboard-title"]',
                'button, .btn, [role="button"]',
                '.card, .dashboard-card, [data-testid*="card"]',
                'nav, .navigation, [data-testid="navigation"]'
            ]
            
            components_found = 0
            for selector in selectors_to_check:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        components_found += 1
                        print(f"   ✅ Found: {selector}")
                except:
                    print(f"   ⚠️  Not found: {selector}")
            
            print(f"\n📊 Dashboard Components Found: {components_found}/{len(selectors_to_check)}")
            
            # Test API endpoints
            print("\n🔌 Testing API Endpoints...")
            
            endpoints_to_test = [
                "/api/dashboard/health",
                "/api/dashboard/stats", 
                "/api/dashboard/products",
                "/api/dashboard/conversations"
            ]
            
            api_results = {}
            for endpoint in endpoints_to_test:
                try:
                    response = await page.request.get(f"http://localhost:8000{endpoint}")
                    api_results[endpoint] = {
                        "status": response.status,
                        "ok": response.ok
                    }
                    status_icon = "✅" if response.ok else "❌"
                    print(f"   {status_icon} {endpoint}: {response.status}")
                except Exception as e:
                    print(f"   ❌ {endpoint}: Error - {str(e)}")
                    api_results[endpoint] = {"status": "error", "ok": False}
            
            # Summary
            print("\n📋 Test Summary:")
            print(f"   Frontend Loaded: ✅")
            print(f"   Backend Health: ✅")
            print(f"   Components Found: {components_found}/{len(selectors_to_check)}")
            
            working_endpoints = sum(1 for r in api_results.values() if r.get("ok", False))
            print(f"   API Endpoints Working: {working_endpoints}/{len(endpoints_to_test)}")
            
            overall_success = (
                components_found >= 2 and 
                working_endpoints >= 2
            )
            
            if overall_success:
                print("\n🎉 Dashboard test completed successfully!")
                return True
            else:
                print("\n⚠️  Dashboard test completed with warnings")
                return False
                
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_dashboard())
    exit(0 if success else 1)