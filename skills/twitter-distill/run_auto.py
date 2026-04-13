"""
Twitter 数据收集器 - 完全无头自动版

使用无头浏览器 + 自动滚动 + 智能检测
无需人工干预，自动完成所有博主收集
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 目标博主（10 位）
BLOGGERS = [
    "Hoyooyoo", "KillaXBT", "Will_Yang_", "yekoikoi", "0xtongcan",
    "WallStreet0Name", "CycleStudies", "Mingarithm", "Jingxin147741", "PAVLeader",
]

# 股票映射 - 扩展版
NAME_TO_SYMBOL = {
    # A 股 - 白酒/消费
    '贵州茅台': '600519.ss', '茅台': '600519.ss', '五粮液': '000858.sz', '泸州老窖': '000568.sz',
    '山西汾酒': '600809.ss', '古井贡酒': '000596.sz', '洋河股份': '002304.sz',
    '中国中免': '601888.ss', '重庆啤酒': '600132.ss', '青岛啤酒': '600600.ss',
    # A 股 - 新能源/科技
    '宁德时代': '300750.sz', '宁德': '300750.sz', '比亚迪': '002594.sz', '亿纬锂能': '300014.sz',
    '赣锋锂业': '002460.sz', '天齐锂业': '002466.sz', '华友钴业': '603799.ss',
    '隆基绿能': '601012.ss', '通威股份': '600438.ss', '阳光电源': '300274.sz',
    '三花智控': '002050.sz', '卧龙电驱': '600580.ss', '山子高科': '000981.sz',
    # A 股 - 金融
    '中国平安': '601318.ss', '平安': '601318.ss', '招商银行': '600036.ss', '招商': '600036.ss',
    '中信证券': '600030.ss', '中信': '600030.ss', '东方财富': '300059.sz', '东财': '300059.sz',
    '宁波银行': '002142.sz', '兴业银行': '601166.ss',
    # A 股 - 医药
    '恒瑞医药': '600276.ss', '药明康德': '603259.ss', '泰格医药': '300347.sz',
    '片仔癀': '600436.ss', '云南白药': '000538.sz',
    # A 股 - 其他
    '万科 A': '000002.sz', '万科': '000002.sz', '保利发展': '600048.ss', '保利': '600048.ss',
    '格力电器': '000651.sz', '格力': '000651.sz', '美的集团': '000333.sz', '美的': '000333.sz',
    '海康威视': '002415.sz', '海康': '002415.sz', '立讯精密': '002475.sz',
    '中芯国际': '688981.ss', '韦尔股份': '603501.ss', '卓胜微': '300782.sz',
    # 港股
    '腾讯控股': '00700.hk', '腾讯': '00700.hk', '美团': '03690.hk', '小米集团': '01810.hk', '小米': '01810.hk',
    '阿里巴巴': '09988.hk', '阿里': '09988.hk', '京东': '09618.hk', '拼多多': 'PDD',
    '网易': '09999.hk', '百度': 'BIDU', '快手': '01024.hk', '哔哩哔哩': 'BILI',
    '融创中国': '01918.hk', '融创': '01918.hk', '恒大': '03333.hk', '碧桂园': '02007.hk',
    '华虹半导体': '01347.hk', '中芯国际': '00981.hk',
    # 美股
    '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA', '微软': 'MSFT',
    '亚马逊': 'AMZN', '谷歌': 'GOOGL', 'Meta': 'META', '脸书': 'META',
    # 指数/ETF
    '沪深 300': '000300.ss', '上证 50': '000016.ss', '中证 500': '000905.ss',
    '创业板': '399006.sz', '科创 50': '000688.ss', '恒生指数': '0HSI.hk',
}

def extract_symbols(text: str) -> List[str]:
    import re
    # 先移除 URL，避免从 URL 中提取假阳性股票代码
    text_no_url = re.sub(r'https?://\S+', '', text)
    
    symbols = [sym for name, sym in NAME_TO_SYMBOL.items() if name in text_no_url]
    
    # 只匹配带后缀的代码（.ss/.sz/.hk），避免纯数字误匹配
    for pattern in [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{5}\.hk)']:
        for match in re.findall(pattern, text_no_url):
            if match not in symbols:
                symbols.append(match)
    
    # 美股代码（$ 符号）
    for match in re.findall(r'\$([A-Z]{1,5})', text_no_url):
        if match not in symbols and match not in ['BTC', 'ETH', 'USDT', 'USDC']:  # 排除加密货币
            symbols.append(match)
    
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    t = text.lower()
    bull = sum(1 for kw in ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy'] if kw in t)
    bear = sum(1 for kw in ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell'] if kw in t)
    return "bullish" if bull > bear else ("bearish" if bear > bull else "neutral")

def load_existing_ids(username: str, output_dir: str = "data/twitter"):
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    existing.add(json.loads(line).get('tweet_id'))
                except:
                    pass
    return existing, output_file

def save_tweets(tweets: List[Dict], username: str, output_dir: str = "data/twitter"):
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    existing, _ = load_existing_ids(username, output_dir)
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        for t in tweets:
            if t['tweet_id'] not in existing:
                f.write(json.dumps(t, ensure_ascii=False) + '\n')
                new_count += 1
    return new_count

def collect_blogger(browser, username: str, target: int = 1000, max_scrolls: int = 200) -> int:
    """收集单个博主，返回新推文数量"""
    print(f"\n[{username}] Target: {target} stock tweets")
    
    tweets = []
    existing_ids, output_file = load_existing_ids(username)
    
    if len(existing_ids) >= target:
        print(f"  [Skip] Already have {len(existing_ids)} tweets")
        return 0
    
    page = browser.new_page()
    
    try:
        # Use main profile (not /with_replies) for more content
        page.goto(f"https://x.com/{username}", timeout=60000)
        time.sleep(5)
        
        # 检查登录
        if page.query_selector('input[autocomplete="username"]'):
            print(f"  [Error] Not logged in!")
            return 0
        
        # 滚动收集 - 更激进的滚动策略
        scroll_count = 0
        last_height = 0
        no_new = 0
        
        while len(tweets) < target and scroll_count < max_scrolls:
            scroll_count += 1
            
            # 更激进的滚动（每次 800px）
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1.5)  # 等待内容加载
            
            # 提取
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
                except:
                    continue
            
            if scroll_count % 10 == 0:
                print(f"  [{scroll_count}/{max_scrolls}] Tweets: {len(tweets)} (visible: {len(current_tweets)})")
            
            # 检查是否到底 - 更严格的判断
            h = page.evaluate("document.documentElement.scrollHeight")
            if h == last_height:
                no_new += 1
                if no_new >= 5:
                    print(f"  [End] Reached bottom after {scroll_count} scrolls")
                    break
            else:
                no_new = 0
            last_height = h
        
        # 保存
        if tweets:
            new_count = save_tweets(tweets, username)
            print(f"  [Done] {len(tweets)} total, {new_count} new saved")
        
        return len(tweets)
    
    except Exception as e:
        print(f"  [Error] {e}")
        return 0
    
    finally:
        page.close()

def export_for_backtest():
    """导出回测数据"""
    print("\n[Export] Generating backtest data...")
    
    input_dir = "data/twitter"
    output_file = "strategy/twitter_recommendations.json"
    
    recs = []
    if os.path.exists(input_dir):
        for fn in os.listdir(input_dir):
            if fn.endswith('.jsonl'):
                with open(os.path.join(input_dir, fn), 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            t = json.loads(line)
                            for sym in t.get('symbols', []):
                                recs.append({
                                    "symbol": sym, "date": t.get('timestamp', '')[:10],
                                    "blogger": f"@{t.get('username', '?')}", "note": t.get('content', '')[:150],
                                    "sentiment": t.get('sentiment', 'neutral'), "tweet_id": t.get('tweet_id'),
                                })
                        except:
                            pass
    
    # 去重
    seen = set()
    unique = []
    for r in recs:
        k = f"{r['symbol']}_{r['date']}_{r['tweet_id']}"
        if k not in seen:
            seen.add(k)
            unique.append(r)
    
    unique.sort(key=lambda x: x['date'], reverse=True)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    print(f"  [OK] {len(unique)} recommendations exported")
    
    # 统计
    bloggers = {}
    for r in unique:
        bloggers[r['blogger']] = bloggers.get(r['blogger'], 0) + 1
    
    print("\n  Stats:")
    for b, c in sorted(bloggers.items(), key=lambda x: -x[1]):
        print(f"    {b}: {c}")
    
    return len(unique)

def main():
    print("\n" + "="*70)
    print("Twitter Data Collector - FULLY AUTOMATED")
    print("="*70)
    print(f"Bloggers: {len(BLOGGERS)}")
    print(f"Target: 1000 tweets each")
    print(f"Total: ~{len(BLOGGERS) * 1000} tweets")
    print("="*70)
    
    user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # 持久化上下文
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            viewport={'width': 1280, 'height': 800},
        )
        
        # 验证登录
        print("\n[Check] Verifying login...")
        page = browser.new_page()
        page.goto("https://x.com/home", timeout=60000)
        time.sleep(3)
        
        if page.query_selector('input[autocomplete="username"]'):
            print("\n[ERROR] NOT LOGGED IN!")
            print("\nFirst time setup required:")
            print("  1. Run: python setup_login.py")
            print("  2. Or manually login in browser")
            print("  3. Then run this script again")
            page.close()
            browser.close()
            return False
        
        page.close()
        print("[OK] Logged in!\n")
        
        # 收集
        results = {}
        total = 0
        
        for i, username in enumerate(BLOGGERS, 1):
            print(f"\n[{i}/{len(BLOGGERS)}] @{username}")
            count = collect_blogger(browser, username, target=1000, max_scrolls=200)
            results[username] = count
            total += count
            
            # 保存进度
            with open(os.path.join(os.path.dirname(__file__), "progress.json"), 'w') as f:
                json.dump({"last_updated": datetime.now().isoformat(), "results": results}, f, indent=2)
            
            if i < len(BLOGGERS):
                time.sleep(3)  # 速率限制
        
        browser.close()
    
    # 汇总
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)
    for u, c in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  @{u:20s} {c:4d}")
    print("-"*70)
    print(f"  TOTAL: {total}")
    print("="*70)
    
    # 导出
    export_for_backtest()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[Next] Run backtest:")
        print("  python ..\\..\\strategy\\backtest_twitter.py")
