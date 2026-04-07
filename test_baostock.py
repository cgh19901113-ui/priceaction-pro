import baostock as bs
import pandas as pd

print("测试 Baostock 数据源")
print("=" * 50)

# 登录
bs.login()
print("登录成功")

# 测试 1: 获取贵州茅台历史数据
print("\n1. 获取贵州茅台 (600519) 历史数据...")
try:
    rs = bs.query_history_k_data_plus(
        "sh.600519",
        "date,open,high,low,close,volume",
        start_date='2025-01-01',
        end_date='2025-12-31',
        frequency="d",
        adjustflag="2"  # 前复权
    )
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"   OK 获取成功：{len(df)} 条记录")
    if len(df) > 0:
        print(f"   最新价格：{df['close'].iloc[-1]}")
        print(f"   日期范围：{df['date'].iloc[0]} 至 {df['date'].iloc[-1]}")
except Exception as e:
    print(f"   XX 失败：{e}")

# 测试 2: 获取沪深 300 指数
print("\n2. 获取沪深 300 (000300) 指数...")
try:
    rs = bs.query_history_k_data_plus(
        "sh.000300",
        "date,open,high,low,close,volume",
        start_date='2025-01-01',
        end_date='2025-12-31',
        frequency="d",
        adjustflag="2"
    )
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"   OK 获取成功：{len(df)} 条记录")
    if len(df) > 0:
        print(f"   最新点位：{df['close'].iloc[-1]}")
except Exception as e:
    print(f"   XX 失败：{e}")

# 测试 3: 获取腾讯控股 (港股)
print("\n3. 获取腾讯控股 (00700.HK) 历史数据...")
try:
    rs = bs.query_history_k_data_plus(
        "HK.00700",
        "date,open,high,low,close,volume",
        start_date='2025-01-01',
        end_date='2025-12-31',
        frequency="d",
        adjustflag="2"
    )
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"   OK 获取成功：{len(df)} 条记录")
    if len(df) > 0:
        print(f"   最新价格：{df['close'].iloc[-1]}")
except Exception as e:
    print(f"   XX 失败：{e}")

# 登出
bs.logout()
print("\n" + "=" * 50)
print("Baostock 测试完成")
