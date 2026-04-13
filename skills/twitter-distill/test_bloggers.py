"""Test multiple bloggers to find ones with stock mentions"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

# Test these bloggers
test_users = ["Hoyooyoo", "KillaXBT", "Will_Yang_"]

NAME_TO_SYMBOL = {
    '贵州茅台': '600519.ss', '茅台': '600519.ss', '宁德时代': '300750.sz', '宁德': '300750.sz',
    '比亚迪': '002594.sz', '五粮液': '000858.sz', '中国中免': '601888.ss', '重庆啤酒': '600132.ss',
    '三花智控': '002050.sz', '卧龙电驱': '600580.ss', '山子高科': '000981.sz',
    '华虹半导体': '01347.hk', '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA',
    '腾讯': '00700.hk', '美团': '03690.hk', '小米': '01810.hk', '阿里巴巴': 'BABA',
    '拼多多': 'PDD', '京东': 'JD', '百度': 'BIDU', '网易': 'NTES',
    '恒大': '03333.hk', '融创': '01918.hk', '万科': '000002.sz', '保利': '600048.ss',
    '平安': '601318.ss', '招商': '600036.ss', '中信': '600030.ss', '茅台': '600519.ss',
    '沪深 300': '000300.ss', '上证': '000001.ss', '创业板': '399006.sz',
}

import re
def extract_symbols(text: str):
    symbols = [sym for name, sym in NAME_TO_SYMBOL.items() if name in text]
    for pattern in [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{6})', r'(\d{5}\.hk)', r'(\$[A-Z]{1,5})']:
        for match in re.findall(pattern, text):
            if match.isdigit() and len(match) == 6:
                symbols.append(f"{match}.ss" if match.startswith('6') else f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    return list(set(symbols))

user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

print("="*70)
print("Testing bloggers for stock mentions")
print("="*70)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    for username in test_users:
        print(f"\n{'='*70}")
        print(f"@{username}")
        print('='*70)
        
        page = browser.new_page()
        page.goto(f"https://x.com/{username}", timeout=60000)
        time.sleep(5)
        
        all_tweets = []
        stock_tweets = []
        
        for scroll in range(15):
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1.5)
            
            tweets = page.query_selector_all('article[data-testid="tweet"]')
            
            for el in tweets:
                try:
                    content_el = el.query_selector('[data-testid="tweetText"]')
                    if content_el:
                        content = content_el.inner_text()
                        if content and len(content) > 10:
                            link = el.query_selector('a[href*="/status/"]')
                            tid = link.get_attribute('href').split('/status/')[-1].split('?')[0] if link else "unknown"
                            
                            if tid not in [t[0] for t in all_tweets]:
                                all_tweets.append((tid, content))
                                symbols = extract_symbols(content)
                                if symbols:
                                    stock_tweets.append((tid, content, symbols))
                except:
                    pass
        
        print(f"\nTotal tweets: {len(all_tweets)}")
        print(f"Stock tweets: {len(stock_tweets)}")
        
        if stock_tweets:
            print(f"\nStock mentions found:")
            for tid, content, symbols in stock_tweets[:5]:
                preview = content[:80].replace('\n', ' ')
                print(f"  {symbols}: {preview}...")
        
        page.close()
    
    browser.close()

print("\n[Done]")
