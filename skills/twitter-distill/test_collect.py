"""Test collector - single blogger"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(__file__))

username = "Hoyooyoo"
user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

print(f"\n[Test] Collecting from @{username}")
print("="*60)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    print(f"[1/4] Loading profile...")
    page.goto(f"https://x.com/{username}/with_replies", timeout=60000)
    time.sleep(5)
    
    print(f"[2/4] Waiting for tweets...")
    try:
        page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
        print("[OK] Tweets found")
    except Exception as e:
        print(f"[ERROR] No tweets: {e}")
        page.close()
        browser.close()
        sys.exit(1)
    
    print(f"[3/4] Extracting first 5 tweets...")
    tweets = page.query_selector_all('article[data-testid="tweet"]')
    print(f"[OK] Found {len(tweets)} tweet articles")
    
    for i, el in enumerate(tweets[:5], 1):
        try:
            content_el = el.query_selector('[data-testid="tweetText"]')
            if content_el:
                content = content_el.inner_text()[:100]
                print(f"  [{i}] {content}...")
            else:
                print(f"  [{i}] [No text content]")
        except Exception as e:
            print(f"  [{i}] [Error: {e}]")
    
    print(f"\n[4/4] Taking screenshot...")
    page.screenshot(path="test_collection.png")
    print("[OK] Screenshot saved")
    
    page.close()
    browser.close()

print("\n[Test] Done!")
