"""
Twitter 博主数据蒸馏器 - Nitter API 版本

使用 Nitter 实例（无需 Twitter API 认证）
Nitter: https://github.com/zedeus/nitter
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Nitter 实例列表（多个用于负载均衡）
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacy.com.de",
    "https://nitter.in.projectsegfau.lt",
    "https://nitter.moomoo.me",
]

# 当前使用的实例
CURRENT_INSTANCE = 0

# 目标博主列表
BLOGGERS = [
    {"username": "Hoyooyoo", "priority": "P0", "lang": "zh", "focus": "price_action"},
    {"username": "KillaXBT", "priority": "P0", "lang": "en", "focus": "price_action"},
    {"username": "Will_Yang_", "priority": "P1", "lang": "zh", "focus": "wyckoff"},
    {"username": "yekoikoi", "priority": "P1", "lang": "zh", "focus": "volume_price"},
    {"username": "0xtongcan", "priority": "P1", "lang": "zh", "focus": "naked_k"},
    {"username": "WallStreet0Name", "priority": "P1", "lang": "zh", "focus": "naked_k"},
    {"username": "CycleStudies", "priority": "P2", "lang": "zh", "focus": "trend_line"},
    {"username": "Mingarithm", "priority": "P2", "lang": "en", "focus": "pattern"},
    {"username": "Jingxin147741", "priority": "P2", "lang": "zh", "focus": "naked_k"},
    {"username": "PAVLeader", "priority": "P3", "lang": "en", "focus": "smart_money"},
]

# A 股/港股/美股代码正则
SYMBOL_PATTERNS = [
    r'(\d{6}\.ss)',
    r'(\d{6}\.sz)',
    r'(\d{6})',
    r'(\d{5}\.hk)',
    r'(\$[A-Z]{1,5})',
    r'([A-Z]{1,5})',
]

# 中文股票名映射表
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
    '特斯拉': 'TSLA', 'TSLA': 'TSLA',
    '苹果': 'AAPL', 'AAPL': 'AAPL',
    '英伟达': 'NVDA', 'NVDA': 'NVDA',
    '微软': 'MSFT', 'MSFT': 'MSFT',
    '谷歌': 'GOOGL', 'GOOGL': 'GOOGL',
    '亚马逊': 'AMZN', 'AMZN': 'AMZN',
    '腾讯': '00700.hk', '腾讯控股': '00700.hk',
    '阿里巴巴': 'BABA', '阿里': 'BABA',
    '美团': '03690.hk',
    '小米': '01810.hk',
}

def get_nitter_url() -> str:
    """获取当前可用的 Nitter 实例"""
    return NITTER_INSTANCES[CURRENT_INSTANCE]

def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """获取 URL 内容"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return None

def extract_symbols(text: str) -> List[str]:
    """从推文文本中提取股票代码"""
    symbols = []
    
    # 查找股票名
    for name, symbol in NAME_TO_SYMBOL.items():
        if name in text:
            symbols.append(symbol)
    
    # 查找代码模式
    for pattern in SYMBOL_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.isdigit() and len(match) == 6:
                if match.startswith('6'):
                    symbols.append(f"{match}.ss")
                elif match.startswith('3'):
                    symbols.append(f"{match}.sz")
                elif match.startswith('0'):
                    symbols.append(f"{match}.sz")
            elif match not in symbols:
                symbols.append(match)
    
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    """分析推文情感"""
    text_lower = text.lower()
    
    bullish_keywords = ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy', '做多', '看涨', '看多']
    bearish_keywords = ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell', '做空', '看跌', '看空']
    
    bull_score = sum(1 for kw in bullish_keywords if kw in text_lower)
    bear_score = sum(1 for kw in bearish_keywords if kw in text_lower)
    
    if bull_score > bear_score:
        return "bullish"
    elif bear_score > bull_score:
        return "bearish"
    else:
        return "neutral"

def extract_analysis_type(text: str) -> str:
    """分析推文类型"""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ['裸 k', 'naked k', '纯 k', 'k 线']):
        return "naked_k"
    elif any(kw in text_lower for kw in ['价格行为', 'price action', 'pa']):
        return "price_action"
    elif any(kw in text_lower for kw in ['威科夫', 'wyckoff', '量价']):
        return "wyckoff"
    elif any(kw in text_lower for kw in ['波浪', 'elliott', 'ew']):
        return "elliott_wave"
    elif any(kw in text_lower for kw in ['缠论', 'chan']):
        return "chan_theory"
    elif any(kw in text_lower for kw in ['支撑', '压力', 'support', 'resistance']):
        return "support_resistance"
    else:
        return "general_ta"

def parse_nitter_timeline(username: str, html: str) -> List[Dict]:
    """解析 Nitter 时间线 HTML"""
    tweets = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有推文
        tweet_elements = soup.find_all('div', class_='timeline-item')
        
        for tweet_el in tweet_elements:
            try:
                # 提取推文内容
                content_el = tweet_el.find('div', class_='tweet-content')
                if not content_el:
                    continue
                
                content = content_el.get_text(strip=True)
                
                # 提取时间
                time_el = tweet_el.find('span', class_='tweet-date')
                timestamp = None
                if time_el:
                    time_str = time_el.get('title', '')
                    if time_str:
                        try:
                            # 尝试解析日期
                            timestamp = datetime.strptime(time_str[:10], '%Y-%m-%d').isoformat()
                        except:
                            timestamp = time_str[:10]
                
                # 提取互动数据
                likes_el = tweet_el.find('span', class_='icon-heart')
                retweets_el = tweet_el.find('span', class_='icon-retweet')
                
                likes = 0
                retweets = 0
                
                if likes_el:
                    likes_text = likes_el.parent.get_text(strip=True)
                    try:
                        likes = int(likes_text.replace(',', '').replace('K', '000').replace('M', '000000'))
                    except:
                        pass
                
                if retweets_el:
                    rt_text = retweets_el.parent.get_text(strip=True)
                    try:
                        retweets = int(rt_text.replace(',', '').replace('K', '000').replace('M', '000000'))
                    except:
                        pass
                
                # 提取推文链接（包含 ID）
                link_el = tweet_el.find('a', class_='tweet-link')
                tweet_id = None
                if link_el and link_el.get('href'):
                    href = link_el['href']
                    # 从 URL 提取 ID
                    parts = href.split('/')
                    if len(parts) >= 2:
                        tweet_id = parts[-1].split('#')[0]
                
                # 构建推文数据
                tweet_data = {
                    "tweet_id": tweet_id or f"{username}_{len(tweets)}",
                    "timestamp": timestamp or datetime.now().isoformat(),
                    "username": username,
                    "content": content,
                    "likes": likes,
                    "retweets": retweets,
                    "symbols": extract_symbols(content),
                    "sentiment": analyze_sentiment(content),
                    "analysis_type": extract_analysis_type(content),
                }
                
                tweets.append(tweet_data)
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"  解析失败：{e}")
    
    return tweets

def collect_tweets_nitter(username: str, limit: int = 500, max_pages: int = 20) -> List[Dict]:
    """
    使用 Nitter 收集用户推文
    
    Args:
        username: Twitter 用户名（不含@）
        limit: 最大收集数量
        max_pages: 最大翻页数
    """
    print(f"[Collect] Fetching @{username} tweets via Nitter...")
    
    all_tweets = []
    base_url = f"{get_nitter_url()}/{username}/with_replies"
    
    for page in range(max_pages):
        try:
            # 构建 URL
            if page == 0:
                url = base_url
            else:
                url = f"{base_url}?page={page + 1}"
            
            print(f"  [Page {page + 1}]")
            
            html = fetch_url(url)
            if not html:
                print(f"  [Error] Fetch failed, switching instance...")
                # 切换实例
                global CURRENT_INSTANCE
                CURRENT_INSTANCE = (CURRENT_INSTANCE + 1) % len(NITTER_INSTANCES)
                continue
            
            # 解析
            tweets = parse_nitter_timeline(username, html)
            
            if not tweets:
                print(f"  [Done] No more tweets")
                break
            
            # 过滤：只保留含股票的推文
            stock_tweets = [t for t in tweets if t['symbols']]
            all_tweets.extend(stock_tweets)
            
            print(f"  [Found] {len(stock_tweets)} stock tweets (total {len(tweets)})")
            
            if len(all_tweets) >= limit:
                break
            
            # 速率限制
            time.sleep(2)
            
        except Exception as e:
            print(f"  [Error] {e}")
            break
    
    # 限制数量
    all_tweets = all_tweets[:limit]
    
    print(f"[Done] @{username}: {len(all_tweets)} stock tweets collected")
    
    return all_tweets

def save_tweets(tweets: List[Dict], username: str, output_dir: str = "data/twitter"):
    """保存推文到 JSONL 文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{username}.jsonl")
    
    # 读取已有数据（去重）
    existing_ids = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                existing_ids.add(data.get('tweet_id'))
    
    # 追加新数据
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        for tweet in tweets:
            if tweet['tweet_id'] not in existing_ids:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
                new_count += 1
    
    print(f"[Save] {new_count} new tweets saved to {output_file}")

def export_for_backtest(input_dir: str = "data/twitter", output_file: str = "strategy/twitter_recommendations.json"):
    """导出为回测格式"""
    recommendations = []
    
    if not os.path.exists(input_dir):
        print(f"[Error] Directory not found: {input_dir}")
        return recommendations
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.jsonl'):
            continue
        
        filepath = os.path.join(input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                tweet = json.loads(line)
                
                for symbol in tweet['symbols']:
                    rec = {
                        "symbol": symbol,
                        "date": tweet['timestamp'][:10],
                        "blogger": f"@{tweet['username']}",
                        "note": tweet['content'][:100],
                        "sentiment": tweet['sentiment'],
                        "tweet_id": tweet['tweet_id'],
                    }
                    recommendations.append(rec)
    
    # 按日期排序
    recommendations.sort(key=lambda x: x['date'])
    
    # 保存
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    
    print(f"[Export] {len(recommendations)} recommendations saved to {output_file}")
    return recommendations

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter 博主数据蒸馏器 (Nitter 版)')
    parser.add_argument('--user', type=str, help='单个用户名（不含@）')
    parser.add_argument('--all', action='store_true', help='收集所有博主')
    parser.add_argument('--limit', type=int, default=100, help='每个博主最大收集数')
    parser.add_argument('--export', action='store_true', help='导出为回测格式')
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("[Error] beautifulsoup4 not installed. Run: pip install beautifulsoup4")
        return
    
    if args.all:
        for blogger in BLOGGERS:
            print(f"\n{'='*60}")
            print(f"处理：@{blogger['username']} (优先级：{blogger['priority']})")
            print(f"{'='*60}")
            
            tweets = collect_tweets_nitter(blogger['username'], limit=args.limit)
            
            if tweets:
                save_tweets(tweets, blogger['username'])
            
            time.sleep(3)
    
    elif args.user:
        tweets = collect_tweets_nitter(args.user, limit=args.limit)
        if tweets:
            save_tweets(tweets, args.user)
    
    if args.export:
        export_for_backtest()

if __name__ == "__main__":
    main()
