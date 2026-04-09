#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PriceAction Pro 本地测试脚本
测试 API 是否正常工作
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'api')

from index import fetch_stock_data, analyze_stock

def test_api():
    """测试 API"""
    print("=" * 60)
    print("PriceAction Pro 本地测试")
    print("=" * 60)
    print()
    
    # 测试股票
    test_symbols = ['600519', '000858', '300750']
    
    for symbol in test_symbols:
        print(f"测试股票：{symbol}")
        print("-" * 40)
        
        try:
            # 获取数据
            print("1. 获取数据...")
            df = fetch_stock_data(symbol)
            
            if df is None:
                print(f"   ❌ 数据获取失败 - 返回 None")
                continue
            
            print(f"   ✅ 获取到 {len(df)} 条数据")
            
            # 分析
            print("2. 执行分析...")
            result = analyze_stock(symbol, df)
            
            if 'error' in result:
                print(f"   ❌ 分析失败：{result['error']}")
                continue
            
            print(f"   ✅ 分析完成")
            print()
            
            # 显示结果
            print("3. 分析结果:")
            print(f"   大周期：{result['indicators'].get('大周期')} {result['indicators'].get('大周期_颜色')}")
            print(f"   趋势持续：{result['indicators'].get('趋势持续')} {result['indicators'].get('趋势持续_颜色')}")
            print(f"   大盘对比：{result['indicators'].get('大盘对比')} {result['indicators'].get('大盘对比_颜色')}")
            print(f"   主力量能：{result['indicators'].get('主力量能')} {result['indicators'].get('主力量能_颜色')}")
            print(f"   10 日振幅：{result['indicators'].get('10 日振幅')} {result['indicators'].get('10 日振幅_颜色')}")
            print(f"   当前信号：{result['indicators'].get('当前信号')} {result['indicators'].get('当前信号_颜色')}")
            print()
            print(f"   评分：{result['score']}")
            print(f"   推荐：{result['recommendation']}")
            print(f"   简评：{result['comment']}")
            print()
            
        except Exception as e:
            print(f"   ❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
