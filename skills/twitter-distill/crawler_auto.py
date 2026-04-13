"""
Twitter 数据收集器 - 全自动版本

使用持久化登录会话 + 自动滚动 + 批量收集
首次需要手动登录一次，之后完全自动化

安装：pip install playwright
初始化：playwright install chromium
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 目标博主列表（10 位）
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
    '微软': 'MSFT', '腾讯': '00700.hk', '美团': '03690.hk', '小米': '01810.hk',
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
    bull = sum(1 for kw in ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy', '做多', '看涨'] if kw in text_lower)
    bear = sum(1 for kw in ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell', '做空', '看跌'] if kw in text_lower)
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
    return new_count, output_file

def load_existing_ids(username: str, output_dir: str = "data/twitter"):
    """加载已有推文 ID"""
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    existing.add(data.get('tweet_id'))
                except:
                    pass
    return existing

def collect_blogger(browser, username: str, target_count: int = 1000, max_scrolls: int = 200) -> List[Dict]:
    """
    收集单个博主的推文
    
    Args:
        browser: Playwright browser instance
        username: Twitter 用户名
        target_count: 目标收集数量
        max_scrolls: 最大滚动次数
    """
    print(f"\n{'='*70}")
    print(f"[Collect] @{username} - Target: {target_count} stock tweets")
    print(f"{'='*70}")
    
    tweets = []
    existing_ids = load_existing_ids(username)
    print(f"[Info] Existing tweets: {len(existing_ids)}")
    
    page = browser.new_page()
    
    try:
        # 访问博主页面
        url = f"https://x.com/{username}/with_replies"
        print(f"[Navigate] {url}")
        page.goto(url, timeout=60000)
        time.sleep(5)
        
        # 检查是否已登录
        login_input = page.query_selector('input[autocomplete="username"]')
        if login_input:
            print(f"[ERROR] @{username}: Not logged in! Please run setup_login.py first")
            return []
        
        # 等待推文加载
        print("[Wait] Waiting for tweets to load...")
        try:
            page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
            time.sleep(3)
        except PlaywrightTimeout:
            print(f"[ERROR] @{username}: No tweets found")
            return []
        
        # 自动滚动收集
        scroll_count = 0
        no_new_count = 0
        last_height = 0
        
        while len(tweets) < target_count and scroll_count < max_scrolls:
            scroll_count += 1
            
            # 提取推文
            tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
            new_this_scroll = 0
            
            for el in tweet_elements:
                try:
                    content_el = el.query_selector('[data-testid="tweetText"]')
                    if not content_el:
                        continue
                    
                    content = content_el.inner_text()
                    if not content or len(content) < 10:
                        continue
                    
                    # 提取时间
                    time_el = el.query_selector('time')
                    timestamp = time_el.get_attribute('datetime') if time_el else datetime.now().isoformat()
                    
                    # 提取 ID
                    link = el.query_selector('a[href*="/status/"]')
                    tweet_id = link.get_attribute('href').split('/status/')[-1].split('?')[0] if link else f"{username}_{int(time.time())}_{new_this_scroll}"
                    
                    # 跳过已有
                    if tweet_id in existing_ids:
                        continue
                    
                    # 只保留含股票的
                    symbols = extract_symbols(content)
                    if symbols:
                        tweets.append({
                            "tweet_id": tweet_id,
                            "timestamp": timestamp[:10],
                            "username": username,
                            "content": content,
                            "symbols": symbols,
                            "sentiment": analyze_sentiment(content),
                        })
                        existing_ids.add(tweet_id)
                        new_this_scroll += 1
                
                except Exception as e:
                    continue
            
            # 进度
            if scroll_count % 10 == 0 or new_this_scroll > 0:
                print(f"  [Scroll {scroll_count:3d}] Total: {len(tweets):4d} | New: {new_this_scroll:2d}")
            
            # 检查是否到底
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == last_height:
                no_new_count += 1
                if no_new_count >= 10:
                    print(f"[Info] Reached end of tweets after {scroll_count} scrolls")
                    break
            else:
                no_new_count = 0
            last_height = current_height
            
            # 滚动
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)  # 等待加载
        
        print(f"[Done] @{username}: {len(tweets)} stock tweets collected in {scroll_count} scrolls")
        
    except Exception as e:
        print(f"[ERROR] @{username}: {e}")
    
    finally:
        page.close()
    
    # 保存
    if tweets:
        new_count, output_file = save_tweets(tweets, username)
        print(f"[Save] {new_count} new tweets saved to {output_file}")
    
    return tweets

def collect_all_bloggers():
    """批量收集所有博主"""
    print("\n" + "="*70)
    print("Twitter 数据收集器 - 全自动版本")
    print("="*70)
    print(f"目标博主：{len(BLOGGERS)} 位")
    print(f"目标数量：1000 条/博主")
    print(f"预计总量：{len(BLOGGERS) * 1000}+ 条")
    print("="*70)
    
    # 检查登录状态
    print("\n[Check] 检查登录状态...")
    
    with sync_playwright() as p:
        # 使用持久化上下文
        user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,  # 无头模式，完全自动化
            viewport={'width': 1280, 'height': 800},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 验证登录
        print("[Verify] 验证 Twitter 登录状态...")
        page = browser.new_page()
        page.goto("https://x.com/home", timeout=60000)
        time.sleep(5)
        
        # 检查是否需要登录
        if page.query_selector('input[autocomplete="username"]'):
            print("\n" + "!"*70)
            print("[ERROR] 未登录 Twitter!")
            print("!"*70)
            print("\n首次使用需要手动登录一次，请运行:")
            print("  python setup_login.py")
            print("\n或者手动登录后，Cookie 会保存，之后可全自动运行")
            print("!"*70)
            page.close()
            browser.close()
            return False
        
        page.close()
        print("[OK] 已登录 Twitter，开始收集...\n")
        
        # 收集所有博主
        total_tweets = 0
        results = {}
        
        for i, username in enumerate(BLOGGERS, 1):
            print(f"\n[{i}/{len(BLOGGERS)}] 处理：@{username}")
            tweets = collect_blogger(browser, username, target_count=1000, max_scrolls=200)
            results[username] = len(tweets)
            total_tweets += len(tweets)
            
            # 保存进度
            save_progress(results)
            
            # 间隔（避免被封）
            if i < len(BLOGGERS):
                print(f"[Wait] 等待 5 秒...")
                time.sleep(5)
        
        browser.close()
    
    # 汇总
    print("\n" + "="*70)
    print("收集完成！汇总:")
    print("="*70)
    for username, count in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  @{username:20s} {count:4d} 条")
    print("-"*70)
    print(f"  总计：{total_tweets} 条")
    print("="*70)
    
    return True

def save_progress(results: Dict):
    """保存进度"""
    progress_file = os.path.join(os.path.dirname(__file__), "progress.json")
    data = {
        "last_updated": datetime.now().isoformat(),
        "results": results
    }
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_for_backtest(input_dir: str = "data/twitter", output_file: str = "strategy/twitter_recommendations.json"):
    """导出为回测格式"""
    print("\n[Export] 导出回测数据...")
    
    recommendations = []
    
    if not os.path.exists(input_dir):
        print(f"[Error] Directory not found: {input_dir}")
        return
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.jsonl'):
            continue
        
        filepath = os.path.join(input_dir, filename)
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
    
    print(f"[OK] {len(unique_recs)} recommendations saved to {output_file}")
    
    # 统计
    bloggers = {}
    for rec in unique_recs:
        b = rec['blogger']
        bloggers[b] = bloggers.get(b, 0) + 1
    
    print("\n[Stats] By blogger:")
    for b, count in sorted(bloggers.items(), key=lambda x: -x[1]):
        print(f"  {b}: {count}")
    
    return unique_recs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Twitter 全自动爬虫')
    parser.add_argument('--export', action='store_true', help='仅导出')
    args = parser.parse_args()
    
    if args.export:
        export_for_backtest()
    else:
        success = collect_all_bloggers()
        if success:
            print("\n[Auto] 自动导出回测数据...")
            export_for_backtest()
