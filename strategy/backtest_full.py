"""
秋生 Trader (@Hoyooyoo) 荐股回测 - 完整数据版

数据来源：原博 Twitter 亮点页面爬取
"""

import pandas as pd
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

# 从原博 Twitter 爬取的荐股记录
RECOMMENDATIONS = [
    # A 股
    {"symbol": "300750.sz", "date": "2025-05-07", "expect": "看涨", "note": "迈为股份 - 底部大牛"},
    
    # 美股
    {"symbol": "GOOG", "date": "2025-02-09", "expect": "看跌", "note": "谷歌 - 做空目标 270"},
    
    # Crypto
    {"symbol": "BTC-USD", "date": "2025-02-09", "expect": "看跌", "note": "比特币 - 72000 做空"},
    {"symbol": "BTC-USD", "date": "2025-01-21", "expect": "看跌", "note": "比特币 - 目标 62250"},
    
    # 商品
    {"symbol": "SI=F", "date": "2025-02-04", "expect": "看跌", "note": "白银 - 92 结束"},
    
    # 指数
    {"symbol": "^N225", "date": "2025-02-10", "expect": "看涨", "note": "日经 225 - 一路狂奔"},
    {"symbol": "^HSI", "date": "2025-03-05", "expect": "看涨", "note": "恒生科技 - 预告 4750"},
    
    # 黄金
    {"symbol": "GC=F", "date": "2025-03-23", "expect": "看跌", "note": "黄金 - 低点 4150"},
]

HOLD_DAYS = 3
TARGET_RETURN = 5.0

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print("秋生 Trader 荐股回测 - 完整数据版")
    print("=" * 70)
    print(f"样本数量：{len(RECOMMENDATIONS)}")
    print(f"持有天数：{HOLD_DAYS} 天")
    print()
    
    results = []
    
    for rec in RECOMMENDATIONS:
        symbol = rec['symbol']
        rec_date = rec['date']
        expect = rec['expect']
        
        print(f"\n分析 {symbol} ({rec_date})...")
        
        try:
            df = yf.download(symbol, start="2025-01-01", end="2025-12-31", progress=False)
            if len(df) == 0:
                print(f"  XX 无数据")
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' in df.columns:
                df = df.set_index('Date')
        except Exception as e:
            print(f"  XX 下载失败：{e}")
            continue
        
        try:
            rec_date_parsed = pd.to_datetime(rec_date)
            rec_idx = df.index.get_loc(rec_date_parsed)
        except:
            print(f"  XX 日期未找到：{rec_date}")
            continue
        
        df_before = df.iloc[:rec_idx+1]
        
        if len(df_before) < 60:
            print(f"  XX 数据不足 ({len(df_before)}天)")
            continue
        
        result = strategy.analyze(symbol, df_before)
        
        close_col = 'Close' if 'Close' in df.columns else 'close'
        price = df[close_col].iloc[rec_idx]
        
        if rec_idx + HOLD_DAYS < len(df):
            ret = (df[close_col].iloc[rec_idx+HOLD_DAYS] - price) / price * 100
        else:
            ret = None
        
        passed = '观察池' in result['recommendation'] or '有点东西' in result['recommendation']
        
        if expect == '看涨':
            expect_match = ret is not None and ret > 0
        else:
            expect_match = ret is not None and ret < 0
        
        results.append({
            'symbol': symbol,
            'date': rec_date,
            'score': result['score'],
            'recommendation': result['recommendation'],
            'passed': passed,
            'return_pct': ret,
            'expect': expect,
            'expect_match': expect_match,
            'note': rec['note']
        })
        
        status = "OK" if passed else "XX"
        ret_str = f"{ret:.1f}%" if ret else "N/A"
        match_str = "OK" if expect_match else "XX"
        rec_text = result['recommendation'].replace('✅', '').replace('❌', '').replace('⚠️', '').replace('⚪', '')[:20]
        print(f"  {status} score:{result['score']} | rec:{rec_text} | return:{ret_str} | expect:{match_str}")
    
    print()
    print("=" * 70)
    print("统计结果")
    print("=" * 70)
    
    total = len(results)
    if total == 0:
        print("无有效数据")
        return
    
    passed = sum(1 for r in results if r['passed'])
    success = sum(1 for r in results if r['expect_match'])
    
    print(f"总样本：{total}")
    print(f"策略通过：{passed} ({passed/total*100:.1f}%)")
    print(f"预期正确：{success} ({success/total*100:.1f}%)")
    print()
    
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
    print("结论")
    print("=" * 70)
    
    if passed / total > 0.5:
        print("OK 策略能捕捉原博推荐 (>50%)")
    else:
        print("XX 策略未能有效捕捉推荐")
    
    if success / total > 0.6:
        print("OK 原博预测准确率较高 (>60%)")
    else:
        print("XX 原博预测准确率一般")

if __name__ == "__main__":
    main()
