# -*- coding: utf-8 -*-
"""600166 福田汽车 - PriceAction 策略分析"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 导入策略引擎
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\projects\price-action-saas\strategy')
from engine import PriceActionStrategy

symbol = "600166"
print("=" * 70)
print(f"  {symbol} 福田汽车 - PriceAction 策略分析")
print(f"  分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  策略来源：秋生 Trader (@Hoyooyoo)")
print("=" * 70)

# 获取日线数据
print("\n[1/3] 获取日线数据...")
try:
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
    
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
    
    if df.empty:
        print("  ERROR: 无法获取数据，请检查网络连接")
        sys.exit(1)
    
    # 重命名列以匹配策略引擎
    df = df.rename(columns={
        '日期': 'Date',
        '收盘': 'Close',
        '开盘': 'Open',
        '最高': 'High',
        '最低': 'Low',
        '成交量': 'Volume',
        '成交额': 'Amount',
        '涨跌幅': 'PctChange'
    })
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    
    print(f"  OK - 获取 {len(df)} 个交易日数据")
    print(f"  最新价：{df['Close'].iloc[-1]:.2f} 元")
    print(f"  数据范围：{df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# 获取 15 分钟数据 (可选)
print("\n[2/3] 获取 15 分钟数据...")
df_15m = None
try:
    df_15m = ak.stock_zh_a_hist_min(symbol=symbol, period="15")
    if not df_15m.empty:
        df_15m = df_15m.rename(columns={
            '日期': 'Date',
            '收盘': 'Close',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        })
        df_15m['Date'] = pd.to_datetime(df['Date'])
        df_15m = df_15m.set_index('Date')
        print(f"  OK - 获取 {len(df_15m)} 条 15 分钟 K 线")
except Exception as e:
    print(f"  SKIP: 15 分钟数据获取失败 ({e})，使用日线分析")

# 运行策略分析
print("\n[3/3] 运行 PriceAction 策略分析...")
strategy = PriceActionStrategy()
report = strategy.analyze(symbol, df, df_15m)

# 输出结果
print("\n" + "=" * 70)
print("  分析结果")
print("=" * 70)

indicators = report['indicators']
for key, value in indicators.items():
    if not key.endswith('_颜色'):
        color_key = key + '_颜色'
        color = indicators.get(color_key, '')
        print(f"  {color} {key}: {value}")

print("\n" + "-" * 70)
print(f"  总分：{report['score']} / 60")
print(f"  推荐：{report['recommendation']}")
print(f"  简评：{report['comment']}")
print("=" * 70)

# 过滤规则说明
if '❌' in report['recommendation']:
    print("\n⚠️  该股票未通过策略过滤，建议观望")
elif '✅' in report['recommendation']:
    print("\n✅ 该股票进入观察池，符合起涨点特征")
else:
    print("\n⚪ 该股票需继续观察，等待更好买点")

print("\n" + "=" * 70)
print("  风险提示：本分析仅供参考，不构成投资建议")
print("  高振幅标的需紧止损 (ATR×1.5-2 倍)")
print("=" * 70)
