import akshare as ak
import pandas as pd

print("测试 akshare 数据源")
print("=" * 50)

# 测试 1: 获取贵州茅台历史数据
print("\n1. 获取贵州茅台 (600519) 历史数据...")
try:
    df = ak.stock_zh_a_hist(symbol="sh600519", period="daily", adjust="qfq")
    print(f"   OK 获取成功：{len(df)} 条记录")
    print(f"   最新价格：{df['收盘'].iloc[-1]:.2f}")
    print(f"   日期范围：{df.index[0]} 至 {df.index[-1]}")
except Exception as e:
    print(f"   XX 失败：{e}")

# 测试 2: 获取沪深 300 指数
print("\n2. 获取沪深 300 (000300) 指数...")
try:
    df = ak.stock_zh_index_hist(symbol="sh000300")
    print(f"   OK 获取成功：{len(df)} 条记录")
    print(f"   最新点位：{df['close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"   XX 失败：{e}")

# 测试 3: 获取腾讯控股 (港股)
print("\n3. 获取腾讯控股 (00700.HK) 历史数据...")
try:
    df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
    print(f"   OK 获取成功：{len(df)} 条记录")
    print(f"   最新价格：{df['收盘'].iloc[-1]:.2f}")
except Exception as e:
    print(f"   XX 失败：{e}")

print("\n" + "=" * 50)
print("akshare 数据源测试完成")
