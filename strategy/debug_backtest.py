"""
秋生 Trader 荐股回测 - 调试版

输出每个指标的详细值，找出过滤原因
"""

import pandas as pd
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

RECOMMENDATIONS = [
    {"symbol": "601888.ss", "date": "2025-11-12", "expect": "看涨", "note": "大周期多头向上"},
    {"symbol": "002050.sz", "date": "2025-09-19", "expect": "看跌", "note": "跌停"},
    {"symbol": "600580.ss", "date": "2025-09-19", "expect": "看跌", "note": "跌停"},
    {"symbol": "159755.sz", "date": "2025-06-12", "expect": "看涨", "note": "做多信号"},
]

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print("Debug Backtest")
    print("=" * 70)
    
    for rec in RECOMMENDATIONS:
        symbol = rec['symbol']
        rec_date = rec['date']
        
        print(f"\n{symbol} ({rec_date})")
        print("-" * 50)
        
        try:
            df = yf.download(symbol, start="2025-01-01", end="2025-12-31", progress=False)
            if len(df) == 0:
                print("  No data")
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' in df.columns:
                df = df.set_index('Date')
        except Exception as e:
            print(f"  Download failed: {e}")
            continue
        
        try:
            rec_date_parsed = pd.to_datetime(rec_date)
            rec_idx = df.index.get_loc(rec_date_parsed)
        except:
            print(f"  Date not found: {rec_date}")
            continue
        
        df_before = df.iloc[:rec_idx+1]
        
        if len(df_before) < 60:
            print(f"  Insufficient data: {len(df_before)} days")
            continue
        
        # 手动计算每个指标
        print("\nIndicators:")
        
        # 1. 大周期
        trend, trend_color = strategy.calculate_daily_trend(df_before)
        print(f"  Trend: {trend}")
        
        # 2. 趋势持续
        duration, duration_color = strategy.calculate_trend_duration(df_before)
        print(f"  Duration: {duration}")
        
        # 3. 大盘对比
        comparison, comp_color = strategy.calculate_market_comparison(symbol, df_before)
        print(f"  Market: {comparison}")
        
        # 4. 主力量能
        flow, flow_color = strategy.calculate_main_force_flow(df_before)
        print(f"  Flow: {flow}")
        
        # 5. 10 日振幅
        amplitude, amp_color = strategy.calculate_10day_amplitude(df_before)
        print(f"  Amplitude: {amplitude}")
        
        # 6. 当前信号
        close_col = 'Close' if 'Close' in df.columns else 'close'
        price = df[close_col].iloc[rec_idx]
        print(f"  当前价格：{price:.2f}")
        
        # 完整分析
        result = strategy.analyze(symbol, df_before)
        rec_text = result['recommendation'].replace('✅', '').replace('❌', '').replace('⚠️', '').replace('⚪', '')
        print(f"\nScore: {result['score']}")
        print(f"Rec: {rec_text}")
        print(f"Comment: {result['comment']}")
        
        # 计算收益
        if rec_idx + 3 < len(df):
            ret = (df[close_col].iloc[rec_idx+3] - price) / price * 100
            print(f"3D Return: {ret:.1f}%")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
