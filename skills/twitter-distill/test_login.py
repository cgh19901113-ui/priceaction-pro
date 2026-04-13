"""Quick login check - simplified"""
import os
import sys
from playwright.sync_api import sync_playwright

user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

print(f"[Test] Profile dir: {user_data_dir}")
print(f"[Test] Exists: {os.path.exists(user_data_dir)}")

if os.path.exists(user_data_dir):
    files = os.listdir(user_data_dir)
    print(f"[Test] Files: {len(files)} items")
    if 'Cookies' in files or 'cookies' in files:
        print("[Test] [OK] Cookies file found")
    else:
        print("[Test] [SKIP] No cookies file")

print("\n[Test] Launching browser (headless)...")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            viewport={'width': 1280, 'height': 800},
        )
        
        print("[Test] Browser launched!")
        print("[Test] Opening a simple page first...")
        
        page = browser.new_page()
        
        # Try a simple page first
        print("[Test] Loading example.com...")
        page.goto("https://example.com", timeout=30000)
        print(f"[Test] Title: {page.title()}")
        
        # Now try Twitter
        print("\n[Test] Loading Twitter...")
        page.goto("https://x.com", timeout=60000)
        page.wait_for_timeout(5000)  # Just wait 5 seconds
        
        # Screenshot for debugging
        screenshot = "test_screenshot.png"
        page.screenshot(path=screenshot)
        print(f"[Test] Screenshot saved: {screenshot}")
        
        # Check for login form
        login_input = page.query_selector('input[autocomplete="username"]')
        
        if login_input:
            print("\n[RESULT] NOT LOGGED IN!")
        else:
            print("\n[RESULT] LOGGED IN! [OK]")
        
        page.close()
        browser.close()
        
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n[Test] Done")
