"""
秋生 Trader (@Hoyooyoo) 荐股回测 - 严谨版

逻辑:
1. 用推荐日**之前**的数据分析 (模拟当时能看到的信息)
2. 看策略是否给出"观察池"信号
3. 验证推荐日后 3 天的实际收益
"""

import pandas as pd
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

# ==================== 荐股记录 ====================
# 从原博 Twitter 爬取，格式：{股票代码，推荐日期，推荐后表现}

RECOMMENDATIONS = [
    # 重庆啤酒 - 2025-03-15 推荐，说"突破 58 等着起飞"
    {"symbol": "600132.ss", "date": "2025-03-15", "expect": "看涨", "note": "说 55 就 55，突破 58 起飞"},
    
    # 中国中免 - 2025-11-12 推荐，"大周期多头向上"
    {"symbol": "601888.ss", "date": "2025-11-12", "expect": "看涨", "note": "大周期多头向上"},
    
    # 三花智控 - 2025-09-19 提到跌停 (反向验证)
    {"symbol": "002050.sz", "date": "2025-09-19", "expect": "看跌", "note": "跌停"},
    
    # 卧龙电驱 - 2025-09-19 提到跌停 (反向验证)
    {"symbol": "600580.ss", "date": "2025-09-19", "expect": "看跌", "note": "跌停"},
    
    # 电池 ETF - 2025-06-12 做多信号
    {"symbol": "159755.sz", "date": "2025-06-12", "expect": "看涨", "note": "做多信号"},
]

HOLD_DAYS = 3
TARGET_RETURN = 5.0

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print("秋生 Trader 荐股回测 - 严谨版")
    print("=" * 70)
    print()
    
    results = []
    
    for rec in RECOMMENDATIONS:
        symbol = rec['symbol']
        rec_date = rec['date']
        expect = rec['expect']
        
        print(f"分析 {symbol} ({rec_date})...")
        
        # 下载数据 (1 年)
        try:
            df = yf.download(symbol, start="2025-01-01", end="2025-12-31", progress=False)
            if len(df) == 0:
                print(f"  XX 无数据")
                continue
            
            # 处理列名
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' in df.columns:
                df = df.set_index('Date')
        except Exception as e:
            print(f"  XX 下载失败：{e}")
            continue
        
        # 找到推荐日索引
        try:
            # 尝试多种日期格式
            rec_idx = None
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y']:
                try:
                    rec_date_parsed = pd.to_datetime(rec_date)
                    rec_idx = df.index.get_loc(rec_date_parsed)
                    break
                except:
                    continue
            
            if rec_idx is None:
                # 尝试直接匹配
                df_dates = pd.to_datetime(df.index)
                rec_date_parsed = pd.to_datetime(rec_date)
                rec_idx = df_dates.get_loc(rec_date_parsed)
                
        except Exception as e:
            print(f"  XX 未找到日期 {rec_date} ({e})")
            continue
        
        # 用推荐日**之前**的数据分析 (模拟当时)
        df_before = df.iloc[:rec_idx+1]
        
        if len(df_before) < 60:
            print(f"  XX 数据不足 ({len(df_before)}天)")
            continue
        
        # 执行策略分析
        result = strategy.analyze(symbol, df_before)
        
        # 计算推荐后收益
        if rec_idx + HOLD_DAYS < len(df):
            close_col = 'Close' if 'Close' in df.columns else 'close'
            buy_price = df[close_col].iloc[rec_idx]
            sell_price = df[close_col].iloc[rec_idx + HOLD_DAYS]
            return_pct = (sell_price - buy_price) / buy_price * 100
        else:
            return_pct = None
        
        # 判断策略是否捕捉到
        passed = '✅' in result['recommendation']
        
        # 判断预期是否正确
        if expect == '看涨':
            expect_match = return_pct is not None and return_pct > 0
        else:
            expect_match = return_pct is not None and return_pct < 0
        
        results.append({
            'symbol': symbol,
            'date': rec_date,
            'score': result['score'],
            'recommendation': result['recommendation'],
            'passed': passed,
            'return_pct': return_pct,
            'expect': expect,
            'expect_match': expect_match,
            'note': rec['note']
        })
        
        status = "OK" if passed else "XX"
        ret_str = f"{return_pct:.1f}%" if return_pct else "N/A"
        rec_text = result['recommendation'].replace('✅', '').replace('❌', '').replace('⚠️', '').replace('⚪', '')[:20]
        print(f"  {status} score:{result['score']} | rec:{rec_text} | return:{ret_str}")
    
    # 统计
    print()
    print("=" * 70)
    print("回测统计")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    success = sum(1 for r in results if r['expect_match'])
    
    print(f"Total: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Expect Match: {success} ({success/total*100:.1f}%)")
    print()
    
    # 详细结果
    print("=" * 70)
    print("详细结果")
    print("=" * 70)
    
    for r in results:
        ret_str = f"{r['return_pct']:.1f}%" if r['return_pct'] else "N/A"
        match_str = "OK" if r['expect_match'] else "XX"
        rec_text = r['recommendation'].replace('✅', '').replace('❌', '').replace('⚠️', '').replace('⚪', '')[:30]
        print(f"{r['symbol']} ({r['date']}): {r['score']}pts | {rec_text} | return:{ret_str} | expect:{match_str}")
        print(f"  Note: {r['note']}")
    
    print()
    print("=" * 70)
    print("Conclusion")
    print("=" * 70)
    
    if passed / total > 0.5:
        print("OK Strategy can capture original blogger recommendations (>50%)")
    else:
        print("XX Strategy failed to capture recommendations")
        print("   Possible reasons:")
        print("   1. Trend duration >3 days at recommendation time (expired)")
        print("   2. Original blogger uses looser technical standards")
        print("   3. Original blogger combines real-time order flow/capital data")
    
    print()

if __name__ == "__main__":
    main()
