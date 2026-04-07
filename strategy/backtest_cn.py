"""
秋生 Trader (@Hoyooyoo) 荐股回测 - 国内数据版

专注：A 股 + 港股 + 国内商品期货
"""

import pandas as pd
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

# 国内荐股记录 (从原博 Twitter 爬取)
RECOMMENDATIONS = [
    # A 股
    {"symbol": "300750.sz", "date": "2025-05-07", "expect": "看涨", "note": "迈为股份 - 底部大牛"},
    {"symbol": "601888.ss", "date": "2025-11-12", "expect": "看涨", "note": "中国中免 - 大周期多头向上"},
    {"symbol": "002050.sz", "date": "2025-09-19", "expect": "看跌", "note": "三花智控 - 跌停"},
    {"symbol": "600580.ss", "date": "2025-09-19", "expect": "看跌", "note": "卧龙电驱 - 跌停"},
    {"symbol": "000981.sz", "date": "2025-09-19", "expect": "看跌", "note": "山子高科 - 高开跌停"},
    {"symbol": "600132.ss", "date": "2025-03-15", "expect": "看涨", "note": "重庆啤酒 - 突破 58 起飞"},
    
    # ETF
    {"symbol": "159755.sz", "date": "2025-06-12", "expect": "看涨", "note": "电池 ETF - 做多信号"},
    
    # 港股
    {"symbol": "0700.HK", "date": "2025-03-05", "expect": "看涨", "note": "腾讯控股 - 恒生科技成分股"},
    {"symbol": "9988.HK", "date": "2025-03-05", "expect": "看涨", "note": "阿里巴巴 - 恒生科技成分股"},
    
    # 国内商品期货 (用 yfinance 近似)
    {"symbol": "GC=F", "date": "2025-03-23", "expect": "看跌", "note": "黄金 - 低点 4150"},
    {"symbol": "SI=F", "date": "2025-02-04", "expect": "看跌", "note": "白银 - 92 结束"},
]

HOLD_DAYS = 3
TARGET_RETURN = 5.0

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print("秋生 Trader 荐股回测 - 国内数据版")
    print("=" * 70)
    print(f"样本数量：{len(RECOMMENDATIONS)}")
    print(f"持有天数：{HOLD_DAYS} 天")
    print()
    
    results = []
    valid_count = 0
    
    for rec in RECOMMENDATIONS:
        symbol = rec['symbol']
        rec_date = rec['date']
        expect = rec['expect']
        
        print(f"分析 {symbol} ({rec_date})...")
        
        try:
            # 下载 2025 年全年数据
            df = yf.download(symbol, period="1y", progress=False)
            if len(df) == 0:
                print(f"  XX 无数据")
                continue
            
            # 处理列名
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            if 'Date' in df.columns:
                df = df.set_index('Date')
            elif 'date' in df.columns:
                df = df.set_index('date')
            
            valid_count += 1
        except Exception as e:
            print(f"  XX 下载失败：{e}")
            continue
        
        # 找到推荐日索引
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
        
        # 执行策略分析
        result = strategy.analyze(symbol, df_before)
        
        # 计算收益
        close_col = 'Close' if 'Close' in df.columns else 'close'
        price = df[close_col].iloc[rec_idx]
        
        if rec_idx + HOLD_DAYS < len(df):
            ret = (df[close_col].iloc[rec_idx+HOLD_DAYS] - price) / price * 100
        else:
            ret = None
        
        # 判断是否通过
        passed = '观察池' in result['recommendation'] or '有点东西' in result['recommendation']
        
        # 判断预期是否正确
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
    print(f"有效数据：{valid_count}")
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
        print("   可能原因:")
        print("   1. 原博推荐时趋势已持续>10 天 (过期)")
        print("   2. 原博用更宽松的技术标准")
        print("   3. 数据质量不足 (yfinance 的 A 股数据有限)")
    
    print()
    print("建议:")
    print("1. 上线网页端收集真实数据")
    print("2. 接入 Tushare Pro/聚宽获取完整 A 股数据")
    print("3. 积累 50+ 样本后再回测优化")

if __name__ == "__main__":
    main()
