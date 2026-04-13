"""Debug - try scrolling and waiting"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.dirname(__file__) + "/browser_profile"

print(f"[Debug] Loading @{username}")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    print("[1/5] Loading page...")
    page.goto(f"https://x.com/{username}/with_replies", timeout=60000)
    time.sleep(5)
    
    print("[2/5] Waiting for network idle...")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
        print("[OK] Network idle")
    except:
        print("[SKIP] Network idle timeout")
    
    print("[3/5] Scrolling down...")
    for i in range(5):
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)
        print(f"  Scroll {i+1}/5")
    
    print("[4/5] Checking for tweets again...")
    tweets = page.query_selector_all('article[data-testid="tweet"]')
    print(f"[RESULT] Found {len(tweets)} tweets")
    
    if tweets:
        print("\n[Sample content]")
        for i, el in enumerate(tweets[:3], 1):
            try:
                content_el = el.query_selector('[data-testid="tweetText"]')
                if content_el:
                    content = content_el.inner_text()[:80]
                    print(f"  [{i}] {content}...")
            except:
                pass
    
    print("[5/5] Screenshot...")
    page.screenshot(path="debug_scroll.png", full_page=True)
    print("[OK] debug_scroll.png saved")
    
    page.close()
    browser.close()

print("\n[Debug] Done!")
