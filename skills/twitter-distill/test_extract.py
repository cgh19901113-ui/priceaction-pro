"""Debug symbol extraction"""
import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

username = "Hoyooyoo"
user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")

NAME_TO_SYMBOL = {
    '贵州茅台': '600519.ss', '茅台': '600519.ss', '五粮液': '000858.sz', '泸州老窖': '000568.sz',
    '山西汾酒': '600809.ss', '古井贡酒': '000596.sz', '洋河股份': '002304.sz',
    '中国中免': '601888.ss', '重庆啤酒': '600132.ss', '青岛啤酒': '600600.ss',
    '宁德时代': '300750.sz', '宁德': '300750.sz', '比亚迪': '002594.sz', '亿纬锂能': '300014.sz',
    '赣锋锂业': '002460.sz', '天齐锂业': '002466.sz', '华友钴业': '603799.ss',
    '隆基绿能': '601012.ss', '通威股份': '600438.ss', '阳光电源': '300274.sz',
    '三花智控': '002050.sz', '卧龙电驱': '600580.ss', '山子高科': '000981.sz',
    '中国平安': '601318.ss', '平安': '601318.ss', '招商银行': '600036.ss', '招商': '600036.ss',
    '中信证券': '600030.ss', '中信': '600030.ss', '东方财富': '300059.sz', '东财': '300059.sz',
    '宁波银行': '002142.sz', '兴业银行': '601166.ss',
    '恒瑞医药': '600276.ss', '药明康德': '603259.ss', '泰格医药': '300347.sz',
    '片仔癀': '600436.ss', '云南白药': '000538.sz',
    '万科 A': '000002.sz', '万科': '000002.sz', '保利发展': '600048.ss', '保利': '600048.ss',
    '格力电器': '000651.sz', '格力': '000651.sz', '美的集团': '000333.sz', '美的': '000333.sz',
    '海康威视': '002415.sz', '海康': '002415.sz', '立讯精密': '002475.sz',
    '中芯国际': '688981.ss', '韦尔股份': '603501.ss', '卓胜微': '300782.sz',
    '腾讯控股': '00700.hk', '腾讯': '00700.hk', '美团': '03690.hk', '小米集团': '01810.hk', '小米': '01810.hk',
    '阿里巴巴': '09988.hk', '阿里': '09988.hk', '京东': '09618.hk', '拼多多': 'PDD',
    '网易': '09999.hk', '百度': 'BIDU', '快手': '01024.hk', '哔哩哔哩': 'BILI',
    '融创中国': '01918.hk', '融创': '01918.hk', '恒大': '03333.hk', '碧桂园': '02007.hk',
    '华虹半导体': '01347.hk', '中芯国际': '00981.hk',
    '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA', '微软': 'MSFT',
    '亚马逊': 'AMZN', '谷歌': 'GOOGL', 'Meta': 'META', '脸书': 'META',
    '沪深 300': '000300.ss', '上证 50': '000016.ss', '中证 500': '000905.ss',
    '创业板': '399006.sz', '科创 50': '000688.ss', '恒生指数': '0HSI.hk',
}

def extract_symbols(text: str):
    symbols = [sym for name, sym in NAME_TO_SYMBOL.items() if name in text]
    for pattern in [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{6})', r'(\d{5}\.hk)', r'(\$[A-Z]{1,5})']:
        for match in re.findall(pattern, text):
            if match.isdigit() and len(match) == 6:
                symbols.append(f"{match}.ss" if match.startswith('6') else f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    return list(set(symbols))

print(f"[Debug] Testing symbol extraction for @{username}")
print("="*70)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        viewport={'width': 1280, 'height': 800},
    )
    
    page = browser.new_page()
    page.goto(f"https://x.com/{username}", timeout=60000)
    time.sleep(5)
    
    # Scroll to load content
    for _ in range(10):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1.5)
    
    tweets = page.query_selector_all('article[data-testid="tweet"]')
    print(f"\nFound {len(tweets)} tweet articles\n")
    
    stock_tweet_count = 0
    
    for i, el in enumerate(tweets[:30], 1):
        try:
            content_el = el.query_selector('[data-testid="tweetText"]')
            if not content_el:
                continue
            
            content = content_el.inner_text()
            if len(content) < 10:
                continue
            
            symbols = extract_symbols(content)
            
            print(f"[{i:2d}] Symbols: {symbols if symbols else 'None'}")
            print(f"     Content: {content[:100]}...")
            
            if symbols:
                stock_tweet_count += 1
                print(f"     >>> STOCK TWEET! <<<")
            print()
            
        except Exception as e:
            print(f"[{i:2d}] Error: {e}\n")
    
    print(f"\n{'='*70}")
    print(f"Total tweets checked: {min(30, len(tweets))}")
    print(f"Stock tweets: {stock_tweet_count}")
    print(f"{'='*70}")
    
    browser.close()

print("\n[Done]")
