#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 BaoStock API (免费 A 股数据)
"""

import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_baostock():
    """测试 BaoStock"""
    print("=" * 70)
    print("测试 BaoStock API")
    print("=" * 70)
    print()
    
    try:
        import baostock as bs
        import pandas as pd
    except ImportError as e:
        print(f"❌ 导入失败：{e}")
        print()
        print("需要先安装：pip install baostock")
        return False
    
    # 登录
    print("登录 BaoStock...")
    lg = bs.login()
    
    if lg.error_code != '0':
        print(f"❌ 登录失败：{lg.error_msg}")
        return False
    
    print(f"✅ 登录成功 (error_code: {lg.error_code})")
    print()
    
    # 获取贵州茅台历史 K 线
    print("获取贵州茅台 (sh.600519) 历史 K 线...")
    rs = bs.query_history_k_data_plus(
        "sh.600519",
        "date,open,high,low,close,volume",
        start_date='2025-01-01',
        end_date='2026-04-10',
        frequency="d",
        adjustflag="3"  # 不复权
    )
    
    if rs.error_code != '0':
        print(f"❌ 查询失败：{rs.error_msg}")
        bs.logout()
        return False
    
    # 转换为 DataFrame
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    print(f"✅ 获取到 {len(df)} 条数据")
    print()
    
    if len(df) > 0:
        print("数据预览 (前 5 行):")
        print(df.head())
        print()
        
        print("数据预览 (后 5 行):")
        print(df.tail())
        print()
        
        # 检查数据量
        if len(df) >= 60:
            print(f"✅ 数据量充足：{len(df)} 条")
        else:
            print(f"⚠️  数据不足：{len(df)} 条")
    
    # 登出
    bs.logout()
    
    return len(df) >= 60


def test_alternative_api():
    """测试备用 API - 使用腾讯/新浪接口"""
    print()
    print("=" * 70)
    print("测试腾讯财经 API (备用方案)")
    print("=" * 70)
    print()
    
    import requests
    
    # 腾讯财经历史 K 线
    # 格式：http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz000001,day,,,200,qfq
    url = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "param": "sh600519,day,,,200,qfq"  # 贵州茅台，日 K,200 条，前复权
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"HTTP 状态码：{response.status_code}")
        print(f"返回数据：{str(data)[:500]}...")
        print()
        
        # 解析数据
        if 'data' in data and 'sh600519' in data['data']:
            stock_data = data['data']['sh600519']
            if 'day' in stock_data:
                klines = stock_data['day']
                print(f"✅ 获取到 {len(klines)} 条 K 线")
                print()
                print("前 5 条:")
                for line in klines[:5]:
                    print(f"  {line}")
                return len(klines) >= 60
        
        print("❌ 数据解析失败")
        return False
        
    except Exception as e:
        print(f"❌ 错误：{type(e).__name__}: {e}")
        return False


def main():
    print()
    print("🔍 开始测试免费 A 股数据源")
    print()
    
    # 测试 BaoStock
    baostock_ok = test_baostock()
    
    # 测试腾讯 API
    tencent_ok = test_alternative_api()
    
    # 汇总
    print()
    print("=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    print()
    print(f"BaoStock: {'✅ 通过' if baostock_ok else '❌ 失败'}")
    print(f"腾讯财经：{'✅ 通过' if tencent_ok else '❌ 失败'}")
    print()
    
    if baostock_ok or tencent_ok:
        print("✅ 至少有一个数据源可用！")
    else:
        print("⚠️  所有数据源都不可用，建议继续用 akshare (Vercel 环境)")


if __name__ == "__main__":
    main()
