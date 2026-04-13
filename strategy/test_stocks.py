"""
PriceAction Pro - 热门股票策略测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from engine import PriceActionStrategy
import akshare as ak

strategy = PriceActionStrategy()

# 测试 5 只热门股票
stocks = ['600519', '000858', '300750', '000333', '002594']
names = ['贵州茅台', '五粮液', '宁德时代', '美的集团', '比亚迪']

print('=' * 80)
print('PriceAction Pro - 个股策略测试 (5 只热门股票)')
print('=' * 80)

results = []

for symbol, name in zip(stocks, names):
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')
        if len(df) < 60:
            print(f'{name} ({symbol}): 数据不足')
            continue
        
        result = strategy.analyze(
            f'{symbol}.ss' if symbol.startswith('6') else f'{symbol}.sz', 
            df
        )
        
        passed = '观察池' in result['recommendation'] or '有点东西' in result['recommendation']
        
        results.append({
            'symbol': symbol,
            'name': name,
            'score': result['score'],
            'recommendation': result['recommendation'],
            'passed': passed
        })
        
        print()
        print(f'{name} ({symbol})')
        print(f'  评分：{result["score"]}分')
        print(f'  建议：{result["recommendation"]}')
        print(f'  评论：{result["comment"]}')
        
    except Exception as e:
        print(f'{name} ({symbol}): 错误 - {e}')

# 统计
print()
print('=' * 80)
print('统计结果')
print('=' * 80)

total = len(results)
passed = sum(1 for r in results if r['passed'])

print(f'测试股票：{total}只')
print(f'进入观察池：{passed}只 ({passed/total*100:.1f}%)')

print()
print('观察池股票:')
for r in [x for x in results if x['passed']]:
    print(f'  - {r["name"]} ({r["symbol"]}): {r["score"]}分')
