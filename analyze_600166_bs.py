# -*- coding: utf-8 -*-
"""600166 福田汽车 - PriceAction 策略分析 (baostock 版)"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

# 导入策略引擎
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\projects\price-action-saas\strategy')
from engine import PriceActionStrategy

symbol = "sh.600166"  # baostock 格式
print("=" * 70)
print(f"  600166 福田汽车 - PriceAction 策略分析")
print(f"  分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  策略来源：秋生 Trader (@Hoyooyoo)")
print(f"  数据源：Baostock")
print("=" * 70)

# 登录 baostock
lg = bs.login()

# 获取日线数据
print("\n[1/3] 获取日线数据...")
rs = bs.query_history_k_data_plus(
    symbol,
    "date,code,open,high,low,close,volume,amount,turn,pctChg",
    start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    frequency="d",
    adjustflag="3"  # 不复权
)

data_list = []
while (rs.error_code == '0') and rs.next():
    data_list.append(rs.get_row_data())

if not data_list:
    print(f"  ERROR: 无法获取数据 ({rs.error_msg})")
    bs.logout()
    sys.exit(1)

df = pd.DataFrame(data_list, columns=rs.fields)
df = df.rename(columns={
    'date': 'Date',
    'close': 'Close',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'volume': 'Volume',
    'amount': 'Amount',
    'pctChg': 'PctChange'
})
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# 转换数值类型
for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"  OK - 获取 {len(df)} 个交易日数据")
print(f"  最新价：{df['Close'].iloc[-1]:.2f} 元")
print(f"  数据范围：{df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")

# 获取基本资料
print("\n[2/3] 获取基本资料...")
rs_basic = bs.query_stock_basic(symbol)
basic_info = {}
while (rs_basic.error_code == '0') and rs_basic.next():
    row = rs_basic.get_row_data()
    for i, field in enumerate(rs_basic.fields):
        basic_info[field] = row[i]

if basic_info:
    print(f"  公司名称：{basic_info.get('companyName', 'N/A')}")
    print(f"  所属行业：{basic_info.get('industry', 'N/A')}")
    print(f"  上市日期：{basic_info.get('ipoDate', 'N/A')}")

# 运行策略分析
print("\n[3/3] 运行 PriceAction 策略分析...")
strategy = PriceActionStrategy()
report = strategy.analyze("600166", df, None)

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

bs.logout()
