"""Debug - see what's on the page"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

print(f"[Debug] Loading @{username} profile")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    print("[1/3] Loading page...")
    page.goto(f"https://x.com/{username}/with_replies", timeout=60000)
    time.sleep(8)  # Wait longer
    
    print("[2/3] Taking full page screenshot...")
    page.screenshot(path="debug_page.png", full_page=True)
    print("[OK] debug_page.png saved")
    
    # Check what selectors exist
    print("\n[3/3] Checking page content...")
    
    # Check for various elements
    checks = [
        ('Login input', 'input[autocomplete="username"]'),
        ('Tweet articles', 'article[data-testid="tweet"]'),
        ('Tweet text', '[data-testid="tweetText"]'),
        ('Timeline', '[data-testid="primaryColumn"]'),
        ('Error message', '[data-testid="error"]'),
    ]
    
    for name, selector in checks:
        el = page.query_selector(selector)
        status = "[FOUND]" if el else "[NOT FOUND]"
        print(f"  {status} {name}: {selector}")
    
    # Get page title
    title = page.title()
    print(f"\nPage title: {title}")
    
    # Get URL
    url = page.url
    print(f"Current URL: {url}")
    
    page.close()
    browser.close()

print("\n[Debug] Done! Check debug_page.png")
