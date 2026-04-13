"""Debug - see all tweet content"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

print(f"[Debug] Showing all tweets from @{username}")
print("="*60)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    page.goto(f"https://x.com/{username}", timeout=60000)
    time.sleep(5)
    
    print("\nScrolling and collecting all tweets...")
    all_tweets = []
    
    for scroll in range(20):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1.5)
        
        tweets = page.query_selector_all('article[data-testid="tweet"]')
        
        for el in tweets:
            try:
                content_el = el.query_selector('[data-testid="tweetText"]')
                if content_el:
                    content = content_el.inner_text()
                    if content and len(content) > 10:
                        # Get tweet ID
                        link = el.query_selector('a[href*="/status/"]')
                        tid = link.get_attribute('href').split('/status/')[-1].split('?')[0] if link else "unknown"
                        
                        if tid not in [t[0] for t in all_tweets]:
                            all_tweets.append((tid, content))
            except:
                pass
        
        if scroll % 5 == 0:
            print(f"  Scroll {scroll+1}: {len(all_tweets)} unique tweets")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_tweets)} unique tweets")
    print(f"{'='*60}\n")
    
    # Show first 10 tweets
    for i, (tid, content) in enumerate(all_tweets[:15], 1):
        preview = content[:120].replace('\n', ' ')
        print(f"[{i:2d}] {preview}...")
        print(f"     ID: {tid}\n")
    
    browser.close()

print("[Debug] Done!")
