"""Test updated collector - single blogger"""
import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(__file__))

username = "Hoyooyoo"
target = 100
user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")
output_dir = "data/twitter"

print(f"\n[Test] Collecting from @{username}")
print(f"Target: {target} stock tweets")
print("="*60)

# Stock name mapping
NAME_TO_SYMBOL = {
    '贵州茅台': '600519.ss', '茅台': '600519.ss', '宁德时代': '300750.sz', '宁德': '300750.sz',
    '比亚迪': '002594.sz', '五粮液': '000858.sz', '中国中免': '601888.ss', '重庆啤酒': '600132.ss',
    '三花智控': '002050.sz', '卧龙电驱': '600580.ss', '山子高科': '000981.sz',
    '华虹半导体': '01347.hk', '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA',
    '腾讯': '00700.hk', '美团': '03690.hk', '小米': '01810.hk',
}

def extract_symbols(text: str):
    import re
    symbols = [sym for name, sym in NAME_TO_SYMBOL.items() if name in text]
    for pattern in [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{6})', r'(\d{5}\.hk)', r'(\$[A-Z]{1,5})']:
        for match in re.findall(pattern, text):
            if match.isdigit() and len(match) == 6:
                symbols.append(f"{match}.ss" if match.startswith('6') else f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    t = text.lower()
    bull = sum(1 for kw in ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy'] if kw in t)
    bear = sum(1 for kw in ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell'] if kw in t)
    return "bullish" if bull > bear else ("bearish" if bear > bull else "neutral")

os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"{username}.jsonl")

# Load existing
existing_ids = set()
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                existing_ids.add(json.loads(line).get('tweet_id'))
            except:
                pass

print(f"Existing tweets: {len(existing_ids)}")

tweets = []
max_scrolls = 50

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    
    try:
        print(f"\n[1/4] Loading profile...")
        page.goto(f"https://x.com/{username}", timeout=60000)
        time.sleep(5)
        
        # Check login
        if page.query_selector('input[autocomplete="username"]'):
            print("[ERROR] Not logged in!")
            sys.exit(1)
        
        print(f"[2/4] Scrolling and collecting...")
        scroll_count = 0
        last_height = 0
        no_new = 0
        
        while len(tweets) < target and scroll_count < max_scrolls:
            scroll_count += 1
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1.5)
            
            current_tweets = page.query_selector_all('article[data-testid="tweet"]')
            
            for el in current_tweets:
                try:
                    content_el = el.query_selector('[data-testid="tweetText"]')
                    if not content_el:
                        continue
                    content = content_el.inner_text()
                    if len(content) < 10:
                        continue
                    
                    time_el = el.query_selector('time')
                    ts = time_el.get_attribute('datetime')[:10] if time_el else datetime.now().isoformat()[:10]
                    
                    link = el.query_selector('a[href*="/status/"]')
                    tid = link.get_attribute('href').split('/status/')[-1].split('?')[0] if link else f"{username}_{int(time.time())}"
                    
                    if tid in existing_ids:
                        continue
                    
                    symbols = extract_symbols(content)
                    if symbols:
                        tweets.append({
                            "tweet_id": tid, "timestamp": ts, "username": username,
                            "content": content, "symbols": symbols, "sentiment": analyze_sentiment(content),
                        })
                        existing_ids.add(tid)
                        print(f"  [Found] {symbols}: {content[:50]}...")
                except:
                    continue
            
            if scroll_count % 10 == 0:
                print(f"  [{scroll_count}/{max_scrolls}] Stock tweets: {len(tweets)} (visible: {len(current_tweets)})")
            
            h = page.evaluate("document.documentElement.scrollHeight")
            if h == last_height:
                no_new += 1
                if no_new >= 5:
                    print(f"  [End] Reached bottom")
                    break
            else:
                no_new = 0
            last_height = h
        
        print(f"\n[3/4] Saving {len(tweets)} tweets...")
        new_count = 0
        with open(output_file, 'a', encoding='utf-8') as f:
            for t in tweets:
                if t['tweet_id'] not in existing_ids:
                    f.write(json.dumps(t, ensure_ascii=False) + '\n')
                    new_count += 1
        
        print(f"[OK] Saved {new_count} new tweets")
        
        print(f"\n[4/4] Summary:")
        print(f"  Total stock tweets: {len(tweets)}")
        print(f"  New tweets: {new_count}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        page.close()
        browser.close()

print("\n[Test] Done!")
