"""Re-export data with fixed symbol extraction"""
import json
import os
import re

# 股票映射
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
    # 移除 URL
    text_no_url = re.sub(r'https?://\S+', '', text)
    
    symbols = [sym for name, sym in NAME_TO_SYMBOL.items() if name in text_no_url]
    
    # 只匹配带后缀的代码
    for pattern in [r'(\d{6}\.ss)', r'(\d{6}\.sz)', r'(\d{5}\.hk)']:
        for match in re.findall(pattern, text_no_url):
            if match not in symbols:
                symbols.append(match)
    
    return list(set(symbols))

def analyze_sentiment(text: str) -> str:
    t = text.lower()
    bull = sum(1 for kw in ['多', '涨', '买', '突破', '向上', 'bullish', 'long', 'buy'] if kw in t)
    bear = sum(1 for kw in ['空', '跌', '卖', '跌破', '向下', 'bearish', 'short', 'sell'] if kw in t)
    return "bullish" if bull > bear else ("bearish" if bear > bull else "neutral")

# 导出
input_dir = "data/twitter"
output_file = "../../strategy/twitter_recommendations.json"

recs = []
if os.path.exists(input_dir):
    for fn in os.listdir(input_dir):
        if fn.endswith('.jsonl'):
            username = fn.replace('.jsonl', '')
            filepath = os.path.join(input_dir, fn)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        t = json.loads(line)
                        # 重新提取符号（使用修复后的逻辑）
                        symbols = extract_symbols(t.get('content', ''))
                        
                        if symbols:  # 只保存有真实股票的推文
                            for sym in symbols:
                                recs.append({
                                    "symbol": sym,
                                    "date": t.get('timestamp', '')[:10],
                                    "blogger": f"@{username}",
                                    "note": t.get('content', '')[:150],
                                    "sentiment": analyze_sentiment(t.get('content', '')),
                                    "tweet_id": t.get('tweet_id'),
                                })
                    except Exception as e:
                        print(f"Error processing {fn}: {e}")

# 去重
seen = set()
unique = []
for r in recs:
    k = f"{r['symbol']}_{r['date']}_{r['tweet_id']}"
    if k not in seen:
        seen.add(k)
        unique.append(r)

unique.sort(key=lambda x: x['date'], reverse=True)

# 保存
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"[OK] Exported {len(unique)} recommendations")

# 统计
bloggers = {}
for r in unique:
    bloggers[r['blogger']] = bloggers.get(r['blogger'], 0) + 1

print("\nBy blogger:")
for b, c in sorted(bloggers.items(), key=lambda x: -x[1]):
    print(f"  {b}: {c}")

# 统计符号类型
a_shares = sum(1 for r in unique if '.ss' in r['symbol'] or '.sz' in r['symbol'])
hk_shares = sum(1 for r in unique if '.hk' in r['symbol'])
us_shares = sum(1 for r in unique if '.ss' not in r['symbol'] and '.sz' not in r['symbol'] and '.hk' not in r['symbol'])

print(f"\nBy market:")
print(f"  A 股：{a_shares}")
print(f"  港股：{hk_shares}")
print(f"  美股：{us_shares}")
