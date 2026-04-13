"""Debug - main profile with more scrolling"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.dirname(__file__) + "/browser_profile"

print(f"[Debug] Testing @{username} main profile")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    # Main profile (not with_replies)
    url = f"https://x.com/{username}"
    print(f"\n[1/4] Loading: {url}")
    page.goto(url, timeout=60000)
    time.sleep(5)
    
    print("[2/4] Aggressive scrolling...")
    total_tweets = 0
    last_count = 0
    
    for scroll in range(30):  # Up to 30 scrolls
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1.5)  # Wait for content to load
        
        tweets = page.query_selector_all('article[data-testid="tweet"]')
        total_tweets = len(tweets)
        
        if scroll % 5 == 0:
            print(f"  Scroll {scroll+1}/30: {total_tweets} tweets")
        
        # Check if we stopped getting new content
        if total_tweets == last_count and scroll > 10:
            print(f"  [No new content after scroll {scroll}]")
            break
        
        last_count = total_tweets
    
    print(f"\n[3/4] Final count: {total_tweets} tweets")
    
    if total_tweets > 0:
        print("[4/4] Sample content:")
        for i, el in enumerate(tweets[:5], 1):
            try:
                content_el = el.query_selector('[data-testid="tweetText"]')
                if content_el:
                    content = content_el.inner_text()
                    # Show first 60 chars
                    preview = content[:60].replace('\n', ' ')
                    print(f"  [{i}] {preview}...")
            except Exception as e:
                print(f"  [{i}] [Error: {e}]")
    
    page.screenshot(path="debug_main_profile.png", full_page=True)
    print(f"\n[OK] Screenshot saved")
    
    page.close()
    browser.close()

print("\n[Debug] Done!")
