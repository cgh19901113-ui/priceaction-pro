"""
Twitter 数据收集器 - 交互式版本

启动浏览器，手动登录并导航到博主页面
然后自动提取当前页面的所有推文

用法：
1. 运行脚本，浏览器打开
2. 手动登录 Twitter
3. 导航到目标博主页面（如 https://x.com/Hoyooyoo/with_replies）
4. 手动向下滚动加载历史推文
5. 按 Ctrl+C 停止，数据会自动保存
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright

# 股票映射
NAME_TO_SYMBOL = {
    '贵州茅台': '600519.ss', '茅台': '600519.ss',
    '宁德时代': '300750.sz', '宁德': '300750.sz',
    '比亚迪': '002594.sz',
    '五粮液': '000858.sz',
    '中国中免': '601888.ss',
    '重庆啤酒': '600132.ss',
    '三花智控': '002050.sz',
    '卧龙电驱': '600580.ss',
    '山子高科': '000981.sz',
    '华虹半导体': '01347.hk',
    '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA',
    '腾讯': '00700.hk', '美团': '03690.hk', '小米': '01810.hk',
}

def extract_symbols(text: str) -> List[str]:
    import re
    symbols = []
    for name, symbol in NAME_TO_SYMBOL.items():
        if name in text:
            symbols.append(symbol)
    patterns = [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{6})', r'(\d{5}\.hk)', r'(\$[A-Z]{1,5})']
    for pattern in patterns:
        for match in re.findall(pattern, text):
            if match.isdigit() and len(match) == 6:
                symbols.append(f"{match}.ss" if match.startswith('6') else f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    bull = sum(1 for kw in ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy'] if kw in text_lower)
    bear = sum(1 for kw in ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell'] if kw in text_lower)
    return "bullish" if bull > bear else ("bearish" if bear > bull else "neutral")

def save_tweets(tweets: List[Dict], username: str, output_dir: str = "data/twitter"):
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    existing.add(json.loads(line).get('tweet_id'))
                except:
                    pass
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        for t in tweets:
            if t['tweet_id'] not in existing:
                f.write(json.dumps(t, ensure_ascii=False) + '\n')
                new_count += 1
    print(f"\n[Save] {new_count} new tweets saved to {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Twitter 交互式爬虫')
    parser.add_argument('--user', type=str, default='Hoyooyoo', help='用户名')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("Twitter 数据收集器 - 交互式版本")
    print("="*70)
    print(f"\n目标博主：@{args.user}")
    print("\n使用说明:")
    print("1. 浏览器会自动打开")
    print("2. 登录 Twitter (如果未登录)")
    print(f"3. 导航到：https://x.com/{args.user}/with_replies")
    print("4. 手动向下滚动加载历史推文 (滚动越多次，收集越多)")
    print("5. 按 Ctrl+C 停止收集，数据会自动保存")
    print("\n提示：可以打开多个标签页分别收集不同博主")
    print("="*70)
    input("\n按 Enter 启动浏览器...")
    
    tweets = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        # 打开 Twitter
        page.goto(f"https://x.com/{args.user}/with_replies", timeout=60000)
        
        print(f"\n[OK] 浏览器已打开，请开始操作...")
        print(f"[Tip] 在浏览器中滚动加载推文，然后回到这里按 Ctrl+C 停止")
        
        start_time = time.time()
        last_count = 0
        
        try:
            while True:
                # 每 5 秒提取一次
                time.sleep(5)
                
                tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                
                new_tweets = 0
                for el in tweet_elements:
                    try:
                        content_el = el.query_selector('[data-testid="tweetText"]')
                        if not content_el:
                            continue
                        
                        content = content_el.inner_text()
                        if not content or len(content) < 5:
                            continue
                        
                        time_el = el.query_selector('time')
                        timestamp = time_el.get_attribute('datetime') if time_el else datetime.now().isoformat()
                        
                        link = el.query_selector('a[href*="/status/"]')
                        tweet_id = link.get_attribute('href').split('/status/')[-1].split('?')[0] if link else f"{args.user}_{int(time.time())}"
                        
                        symbols = extract_symbols(content)
                        if symbols:
                            tweets.append({
                                "tweet_id": tweet_id,
                                "timestamp": timestamp[:10],
                                "username": args.user,
                                "content": content,
                                "symbols": symbols,
                                "sentiment": analyze_sentiment(content),
                            })
                            new_tweets += 1
                    except:
                        continue
                
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] 当前收集：{len(tweets)} 条含股票的推文 (本页共{len(tweet_elements)}条推文)")
                
        except KeyboardInterrupt:
            print(f"\n\n[Stop] 用户中断，正在保存数据...")
        
        browser.close()
    
    # 保存
    if tweets:
        save_tweets(tweets, args.user)
        
        # 显示统计
        bloggers = {}
        for t in tweets:
            bloggers[t['username']] = bloggers.get(t['username'], 0) + 1
        
        print("\n[统计] 按博主:")
        for b, c in sorted(bloggers.items(), key=lambda x: -x[1]):
            print(f"  @{b}: {c} 条")
        
        print("\n[下一步]")
        print("1. 继续收集其他博主：python crawler_interactive.py --user KillaXBT")
        print("2. 导出回测数据：python crawler_browser.py --export")
        print("3. 运行回测：python strategy/backtest_twitter.py")
    else:
        print("\n[Warn] 没有收集到数据")

if __name__ == "__main__":
    main()
