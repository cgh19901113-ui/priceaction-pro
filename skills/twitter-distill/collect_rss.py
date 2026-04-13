"""
Twitter 数据收集 - RSS/公开数据版本

使用 Twitter RSS 订阅（无需登录）
格式：https://r.jina.ai/http://twitter.com/{username}

优点：无需登录，完全自动化
缺点：数据量有限，依赖第三方服务
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict
import urllib.request
import ssl

# 忽略 SSL 证书
ssl._create_default_https_context = ssl._create_unverified_context

sys.path.insert(0, os.path.dirname(__file__))

# 目标博主
BLOGGERS = [
    "Hoyooyoo", "KillaXBT", "Will_Yang_", "yekoikoi", "0xtongcan",
    "WallStreet0Name", "CycleStudies", "Mingarithm", "Jingxin147741", "PAVLeader",
]

# 股票映射
NAME_TO_SYMBOL = {
    '贵州茅台': '600519.ss', '茅台': '600519.ss', '宁德时代': '300750.sz', '宁德': '300750.sz',
    '比亚迪': '002594.sz', '五粮液': '000858.sz', '中国中免': '601888.ss', '重庆啤酒': '600132.ss',
    '三花智控': '002050.sz', '卧龙电驱': '600580.ss', '山子高科': '000981.sz',
    '华虹半导体': '01347.hk', '特斯拉': 'TSLA', '苹果': 'AAPL', '英伟达': 'NVDA',
    '腾讯': '00700.hk', '美团': '03690.hk', '小米': '01810.hk',
}

def extract_symbols(text: str) -> List[str]:
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

def fetch_jina_twitter(username: str) -> List[Dict]:
    """
    使用 Jina AI 读取 Twitter 内容
    https://r.jina.ai/http://twitter.com/{username}
    """
    url = f"https://r.jina.ai/http://twitter.com/{username}"
    print(f"  Fetching: {url}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
        
        # 解析内容（Jina 返回的是格式化文本）
        tweets = []
        lines = content.split('\n')
        
        current_tweet = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测推文开始（通常包含时间戳）
            if any(kw in line for kw in ['·', 'posted', 'tweeted']) or (len(line) > 20 and '@' in line):
                if current_tweet and current_tweet.get('content'):
                    tweets.append(current_tweet)
                current_tweet = {
                    'timestamp': datetime.now().isoformat()[:10],
                    'content': line,
                    'username': username,
                }
            elif current_tweet:
                current_tweet['content'] = current_tweet.get('content', '') + '\n' + line
        
        if current_tweet and current_tweet.get('content'):
            tweets.append(current_tweet)
        
        print(f"  Found {len(tweets)} tweets")
        return tweets
    
    except Exception as e:
        print(f"  Error: {e}")
        return []

def fetch_jina_search(keyword: str, username: str) -> List[Dict]:
    """
    使用 Jina 搜索特定内容
    """
    url = f"https://r.jina.ai/http://twitter.com/{username}/with_replies"
    print(f"  Fetching: {url}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
        
        # 简单分割推文
        tweets = []
        for line in content.split('\n'):
            line = line.strip()
            if len(line) > 30:  # 过滤短内容
                tweets.append({
                    'timestamp': datetime.now().isoformat()[:10],
                    'content': line[:500],
                    'username': username,
                })
        
        print(f"  Found {len(tweets)} tweets")
        return tweets
    
    except Exception as e:
        print(f"  Error: {e}")
        return []

def save_tweets(tweets: List[Dict], username: str, output_dir: str = "data/twitter"):
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    
    # 加载已有
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    existing.add(json.loads(line).get('tweet_id'))
                except:
                    pass
    
    # 保存新数据
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        for t in tweets:
            tid = f"{username}_{hash(t['content'])}"
            if tid not in existing:
                symbols = extract_symbols(t['content'])
                if symbols:  # 只保存含股票的
                    data = {
                        "tweet_id": tid,
                        "timestamp": t.get('timestamp', datetime.now().isoformat()[:10]),
                        "username": username,
                        "content": t['content'][:300],
                        "symbols": symbols,
                        "sentiment": analyze_sentiment(t['content']),
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
                    new_count += 1
    
    return new_count

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
                                    "symbol": sym,
                                    "date": t.get('timestamp', '')[:10],
                                    "blogger": f"@{t.get('username', '?')}",
                                    "note": t.get('content', '')[:150],
                                    "sentiment": t.get('sentiment', 'neutral'),
                                    "tweet_id": t.get('tweet_id'),
                                })
                        except:
                            pass
    
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
    
    print(f"  [OK] {len(unique)} recommendations")
    return len(unique)

def main():
    print("\n" + "="*70)
    print("Twitter Collector - RSS/Jina AI (NO LOGIN REQUIRED)")
    print("="*70)
    print(f"Bloggers: {len(BLOGGERS)}")
    print("="*70)
    
    results = {}
    total = 0
    
    for i, username in enumerate(BLOGGERS, 1):
        print(f"\n[{i}/{len(BLOGGERS)}] @{username}")
        
        # 尝试 Jina 读取
        tweets = fetch_jina_search(None, username)
        
        if tweets:
            new_count = save_tweets(tweets, username)
            results[username] = new_count
            total += new_count
            print(f"  Saved: {new_count} stock tweets")
        else:
            results[username] = 0
            print(f"  No data available")
        
        # 速率限制
        time.sleep(2)
    
    # 汇总
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)
    for u, c in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  @{u:20s} {c:3d}")
    print("-"*70)
    print(f"  TOTAL: {total}")
    print("="*70)
    
    # 导出
    if total > 0:
        export_for_backtest()
        
        # 保存进度
        with open(os.path.join(os.path.dirname(__file__), "progress.json"), 'w') as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "results": results,
                "method": "jina_rss"
            }, f, indent=2)
    
    return total > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[Next] Run backtest:")
        print("  python ..\\..\\strategy\\backtest_twitter.py")
    else:
        print("\n[Error] No data collected. Try:")
        print("  1. Check network connection")
        print("  2. Use browser-based collector (requires login)")
        print("  3. Provide Twitter API credentials")
