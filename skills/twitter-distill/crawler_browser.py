"""
Twitter 网页爬虫 - 浏览器自动化版本

使用 Playwright 登录 Twitter 并批量收集历史推文
支持：登录、滚动加载、数据导出

安装：pip install playwright
初始化：playwright install
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[Error] Playwright not installed. Run: pip install playwright && playwright install")

# 目标博主列表
BLOGGERS = [
    "Hoyooyoo",
    "KillaXBT",
    "Will_Yang_",
    "yekoikoi",
    "0xtongcan",
    "WallStreet0Name",
    "CycleStudies",
    "Mingarithm",
    "Jingxin147741",
    "PAVLeader",
]

# A 股/港股/美股代码映射
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
    '特斯拉': 'TSLA',
    '苹果': 'AAPL',
    '英伟达': 'NVDA',
    '微软': 'MSFT',
    '腾讯': '00700.hk',
    '美团': '03690.hk',
    '小米': '01810.hk',
}

def extract_symbols(text: str) -> List[str]:
    """从文本中提取股票代码"""
    import re
    symbols = []
    
    # 查找股票名
    for name, symbol in NAME_TO_SYMBOL.items():
        if name in text:
            symbols.append(symbol)
    
    # 查找代码模式
    patterns = [
        r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{6})',
        r'(\d{5}\.hk)', r'(\$[A-Z]{1,5})', r'([A-Z]{1,5})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.isdigit() and len(match) == 6:
                if match.startswith('6'):
                    symbols.append(f"{match}.ss")
                else:
                    symbols.append(f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    """分析情感"""
    text_lower = text.lower()
    bullish = ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy', '做多', '看涨']
    bearish = ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell', '做空', '看跌']
    
    bull_score = sum(1 for kw in bullish if kw in text_lower)
    bear_score = sum(1 for kw in bearish if kw in text_lower)
    
    if bull_score > bear_score:
        return "bullish"
    elif bear_score > bull_score:
        return "bearish"
    return "neutral"

def collect_tweets_browser(username: str, limit: int = 1000, output_dir: str = "data/twitter") -> List[Dict]:
    """
    使用浏览器收集推文
    
    Args:
        username: Twitter 用户名
        limit: 目标收集数量
        output_dir: 输出目录
    """
    if not HAS_PLAYWRIGHT:
        print("[Error] Playwright not available")
        return []
    
    print(f"\n{'='*60}")
    print(f"[Collect] @{username} - Target: {limit} tweets")
    print(f"{'='*60}")
    
    tweets = []
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    
    # 读取已有数据（去重）
    existing_ids = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    existing_ids.add(data.get('tweet_id'))
                except:
                    pass
        print(f"[Info] Found {len(existing_ids)} existing tweets")
    
    with sync_playwright() as p:
        # 启动浏览器（使用持久化上下文，保持登录状态）
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器，方便手动登录
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 使用持久化上下文
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # 访问 Twitter
        print(f"[Navigate] Going to Twitter...")
        page.goto(f"https://x.com/{username}/with_replies", timeout=60000)
        
        # 等待页面加载
        print("[Info] Waiting 10 seconds for page load and checking login...")
        time.sleep(10)
        
        # 检查是否需要登录
        try:
            login_input = page.query_selector('input[autocomplete="username"]')
            if login_input:
                print("[Login] *** PLEASE LOG IN MANUALLY NOW ***")
                print("[Info] Script will wait up to 5 minutes for login...")
                print("[Info] After login, scrolling will start automatically")
                
                # 等待登录（最长 5 分钟）
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=300000)
                    time.sleep(3)  # 登录后等待内容加载
                    print("[OK] Login detected!")
                except PlaywrightTimeout:
                    print("[Error] Login timeout - please run again and log in faster")
                    browser.close()
                    return []
        except Exception as e:
            print(f"[Info] Login check: {e}")
        
        # 滚动收集推文
        print(f"[Scroll] Starting to collect tweets...")
        print(f"[Info] Press Ctrl+C to stop early")
        
        last_count = 0
        scroll_pause = 2  # 滚动间隔（秒）
        no_new_count = 0
        
        scroll_count = 0
        while len(tweets) < limit:
            scroll_count += 1
            
            # 提取推文
            tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
            
            print(f"  [Scroll {scroll_count}] Found {len(tweet_elements)} tweet elements")
            
            new_count = 0
            for el in tweet_elements:
                try:
                    # 提取内容
                    content_el = el.query_selector('[data-testid="tweetText"]')
                    if not content_el:
                        continue
                    
                    content = content_el.inner_text()
                    
                    # 跳过空内容
                    if not content or len(content) < 5:
                        continue
                    
                    # 提取时间
                    time_el = el.query_selector('time')
                    timestamp = time_el.get_attribute('datetime') if time_el else datetime.now().isoformat()
                    
                    # 提取 ID
                    tweet_id = None
                    link = el.query_selector('a[href*="/status/"]')
                    if link:
                        href = link.get_attribute('href')
                        if '/status/' in href:
                            tweet_id = href.split('/status/')[-1].split('?')[0]
                    
                    if not tweet_id:
                        tweet_id = f"{username}_{int(time.time())}_{new_count}"
                    
                    # 跳过已存在的
                    if tweet_id in existing_ids:
                        continue
                    
                    # 只保留含股票的推文
                    symbols = extract_symbols(content)
                    if symbols:
                        tweet_data = {
                            "tweet_id": tweet_id,
                            "timestamp": timestamp[:10] if timestamp else datetime.now().isoformat()[:10],
                            "username": username,
                            "content": content,
                            "symbols": symbols,
                            "sentiment": analyze_sentiment(content),
                        }
                        tweets.append(tweet_data)
                        existing_ids.add(tweet_id)
                        new_count += 1
                    
                except Exception as e:
                    continue
            
            print(f"  [Progress] Total: {len(tweets)}, New this scroll: {new_count}")
            
            # 检查是否有新内容
            if new_count == 0:
                no_new_count += 1
                if no_new_count >= 5:
                    print("[Info] No new stock tweets after 5 scrolls, stopping...")
                    break
            else:
                no_new_count = 0
            
            # 滚动到页面底部
            print(f"  [Scroll] Scrolling down...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(scroll_pause)
            
            # 达到目标数量
            if len(tweets) >= limit:
                print(f"[OK] Reached target: {len(tweets)} stock tweets")
                break
        
        print(f"[Done] Final count: {len(tweets)} stock tweets from @{username}")
        
        browser.close()
    
    # 保存数据
    if tweets:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'a', encoding='utf-8') as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        print(f"[Save] Saved {len(tweets)} tweets to {output_file}")
    
    return tweets

def export_all_for_backtest(input_dir: str = "data/twitter", output_file: str = "strategy/twitter_recommendations.json"):
    """导出所有数据为回测格式"""
    recommendations = []
    
    if not os.path.exists(input_dir):
        print(f"[Error] Directory not found: {input_dir}")
        return
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.jsonl'):
            continue
        
        filepath = os.path.join(input_dir, filename)
        print(f"[Process] {filename}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    tweet = json.loads(line)
                    for symbol in tweet.get('symbols', []):
                        recommendations.append({
                            "symbol": symbol,
                            "date": tweet.get('timestamp', '')[:10],
                            "blogger": f"@{tweet.get('username', 'Unknown')}",
                            "note": tweet.get('content', '')[:150],
                            "sentiment": tweet.get('sentiment', 'neutral'),
                            "tweet_id": tweet.get('tweet_id'),
                        })
                except:
                    continue
    
    # 去重 + 排序
    seen = set()
    unique_recs = []
    for rec in recommendations:
        key = f"{rec['symbol']}_{rec['date']}_{rec['tweet_id']}"
        if key not in seen:
            seen.add(key)
            unique_recs.append(rec)
    
    unique_recs.sort(key=lambda x: x['date'], reverse=True)
    
    # 保存
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_recs, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Export] {len(unique_recs)} recommendations saved to {output_file}")
    
    # 统计
    bloggers = {}
    for rec in unique_recs:
        b = rec['blogger']
        bloggers[b] = bloggers.get(b, 0) + 1
    
    print("\n[Stats] By blogger:")
    for b, count in sorted(bloggers.items(), key=lambda x: -x[1]):
        print(f"  {b}: {count}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter 网页爬虫')
    parser.add_argument('--user', type=str, help='单个用户名')
    parser.add_argument('--all', action='store_true', help='收集所有博主')
    parser.add_argument('--limit', type=int, default=1000, help='每个博主目标数量')
    parser.add_argument('--export', action='store_true', help='导出为回测格式')
    
    args = parser.parse_args()
    
    if not HAS_PLAYWRIGHT:
        print("\n[Setup Required]")
        print("1. pip install playwright")
        print("2. playwright install")
        print("3. Run this script again")
        return
    
    if args.all:
        for username in BLOGGERS:
            tweets = collect_tweets_browser(username, limit=args.limit)
            time.sleep(3)  # 间隔
        
        if args.export:
            export_all_for_backtest()
    
    elif args.user:
        tweets = collect_tweets_browser(args.user, limit=args.limit)
        
        if args.export:
            export_all_for_backtest()
    
    elif args.export:
        export_all_for_backtest()
    
    else:
        print("Usage:")
        print("  python crawler_browser.py --user Hoyooyoo --limit 1000")
        print("  python crawler_browser.py --all --limit 500")
        print("  python crawler_browser.py --export")

if __name__ == "__main__":
    main()
