"""Debug - try different URLs"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.dirname(__file__) + "/browser_profile"

urls_to_try = [
    f"https://x.com/{username}",
    f"https://x.com/{username}/with_replies",
    f"https://x.com/{username}/media",
    f"https://x.com/{username}/likes",
]

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    for url in urls_to_try:
        print(f"\n{'='*60}")
        print(f"Trying: {url}")
        print('='*60)
        
        page.goto(url, timeout=60000)
        time.sleep(5)
        
        # Scroll a bit
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)
        
        tweets = page.query_selector_all('article[data-testid="tweet"]')
        print(f"Tweets found: {len(tweets)}")
        
        if tweets:
            print(f"[SUCCESS] {url} has tweets!")
            for i, el in enumerate(tweets[:2], 1):
                try:
                    content_el = el.query_selector('[data-testid="tweetText"]')
                    if content_el:
                        content = content_el.inner_text()[:60]
                        print(f"  [{i}] {content}...")
                except:
                    pass
            break
    
    page.screenshot(path="debug_urls.png", full_page=True)
    print(f"\nScreenshot saved: debug_urls.png")
    
    page.close()
    browser.close()

print("\n[Debug] Done!")
