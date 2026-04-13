"""
Twitter 荐股数据导入器

支持手动导入 Twitter 数据（从 Twitter 导出工具/手动整理）
数据格式：JSON/CSV/Excel

使用方式:
1. 从 Twitter 导出数据（或使用提供的模板手动整理）
2. 运行：python import_data.py --input data.xlsx
3. 自动转换为回测格式
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

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
    '腾讯': '00700.hk',
    '美团': '03690.hk',
    '小米': '01810.hk',
}

def parse_excel(filepath: str) -> List[Dict]:
    """解析 Excel 文件"""
    try:
        import pandas as pd
        df = pd.read_excel(filepath)
        return df.to_dict('records')
    except ImportError:
        print("请安装 pandas 和 openpyxl: pip install pandas openpyxl")
        return []
    except Exception as e:
        print(f"解析 Excel 失败：{e}")
        return []

def parse_csv(filepath: str) -> List[Dict]:
    """解析 CSV 文件"""
    try:
        import pandas as pd
        df = pd.read_csv(filepath)
        return df.to_dict('records')
    except Exception as e:
        print(f"解析 CSV 失败：{e}")
        return []

def parse_json(filepath: str) -> List[Dict]:
    """解析 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"解析 JSON 失败：{e}")
        return []

def normalize_data(raw_data: List[Dict]) -> List[Dict]:
    """
    标准化数据格式
    
    输入格式（支持多种）:
    - {date, symbol, blogger, content/note/text}
    - {timestamp, stock, user, comment}
    - 等
    
    输出格式:
    - {symbol, date, blogger, note, sentiment, tweet_id}
    """
    normalized = []
    
    for row in raw_data:
        # 提取日期
        date = row.get('date') or row.get('timestamp', '')[:10]
        
        # 提取股票代码
        symbol = row.get('symbol') or row.get('stock') or row.get('ticker', '')
        
        # 如果是股票名，转换为代码
        if symbol and symbol in NAME_TO_SYMBOL:
            symbol = NAME_TO_SYMBOL[symbol]
        
        # 提取博主
        blogger = row.get('blogger') or row.get('user') or row.get('username') or '@Unknown'
        if not blogger.startswith('@'):
            blogger = f'@{blogger}'
        
        # 提取内容
        note = row.get('note') or row.get('content') or row.get('text') or row.get('comment', '')
        
        # 提取情感
        sentiment = row.get('sentiment', 'neutral')
        
        # 提取推文 ID
        tweet_id = row.get('tweet_id') or row.get('id') or f"manual_{len(normalized)}"
        
        if symbol:
            normalized.append({
                'symbol': symbol,
                'date': date,
                'blogger': blogger,
                'note': note[:200],  # 限制长度
                'sentiment': sentiment,
                'tweet_id': tweet_id,
            })
    
    return normalized

def save_recommendations(data: List[Dict], output_file: str):
    """保存为标准回测格式"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved {len(data)} recommendations to {output_file}")

def create_template():
    """创建 Excel 模板"""
    try:
        import pandas as pd
        
        template_data = [
            {
                'date': '2025-11-12',
                'symbol': '601888.ss',
                'blogger': '@Hoyooyoo',
                'note': '大周期多头向上，有很大向上空间',
                'sentiment': 'bullish',
            },
            {
                'date': '2025-09-19',
                'symbol': '002050.sz',
                'blogger': '@Hoyooyoo',
                'note': '跌停',
                'sentiment': 'bearish',
            },
        ]
        
        df = pd.DataFrame(template_data)
        
        output_file = 'data/twitter/twitter_import_template.xlsx'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_excel(output_file, index=False)
        
        print(f"[OK] Template created: {output_file}")
        print("Fill in the template and run: python import_data.py --input data/twitter/twitter_import_template.xlsx")
        
    except Exception as e:
        print(f"[Error] Cannot create template: {e}")
        print("Please install: pip install pandas openpyxl")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter 荐股数据导入器')
    parser.add_argument('--input', type=str, help='输入文件 (JSON/CSV/Excel)')
    parser.add_argument('--output', type=str, default='strategy/twitter_recommendations.json', help='输出文件')
    parser.add_argument('--template', action='store_true', help='创建 Excel 模板')
    
    args = parser.parse_args()
    
    if args.template:
        create_template()
        return
    
    if not args.input:
        print("Usage: python import_data.py --input data.xlsx [--template]")
        print("       python import_data.py --template")
        return
    
    # 解析输入文件
    ext = os.path.splitext(args.input)[1].lower()
    
    if ext in ['.xlsx', '.xls']:
        raw_data = parse_excel(args.input)
    elif ext == '.csv':
        raw_data = parse_csv(args.input)
    elif ext == '.json':
        raw_data = parse_json(args.input)
    else:
        print(f"[Error] Unsupported file format: {ext}")
        return
    
    if not raw_data:
        print("[Error] No data parsed")
        return
    
    print(f"[Input] Loaded {len(raw_data)} rows from {args.input}")
    
    # 标准化
    normalized = normalize_data(raw_data)
    print(f"[Normalize] {len(normalized)} valid recommendations")
    
    # 保存
    save_recommendations(normalized, args.output)
    
    # 显示统计
    bloggers = {}
    for rec in normalized:
        b = rec['blogger']
        bloggers[b] = bloggers.get(b, 0) + 1
    
    print("\n[Stats] By blogger:")
    for b, count in sorted(bloggers.items(), key=lambda x: -x[1]):
        print(f"  {b}: {count}")

if __name__ == "__main__":
    main()
