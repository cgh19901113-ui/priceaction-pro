"""
秋生 Trader (@Hoyooyoo) Twitter 荐股回测

从原博 Twitter 爬取的荐股记录进行批量回测
"""

import pandas as pd
import yfinance as yf
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategy.engine import PriceActionStrategy

# ==================== 从 Twitter 爬取的荐股记录 ====================
# 数据来源：skills/twitter-distill/import_data.py 导入

import json
import os

RECOMMENDATIONS_FILE = os.path.join(os.path.dirname(__file__), 'twitter_recommendations.json')

if os.path.exists(RECOMMENDATIONS_FILE):
    with open(RECOMMENDATIONS_FILE, 'r', encoding='utf-8') as f:
        RECOMMENDATIONS = json.load(f)
    print(f"[Info] Loaded {len(RECOMMENDATIONS)} recommendations from {RECOMMENDATIONS_FILE}")
else:
    # 默认数据（如果导入文件不存在）
    RECOMMENDATIONS = [
        {"symbol": "601888.ss", "date": "2025-11-12", "note": "大周期多头向上", "blogger": "@Hoyooyoo"},
        {"symbol": "002050.sz", "date": "2025-09-19", "note": "跌停", "blogger": "@Hoyooyoo"},
        {"symbol": "600580.ss", "date": "2025-09-19", "note": "跌停", "blogger": "@Hoyooyoo"},
        {"symbol": "000981.sz", "date": "2025-09-19", "note": "高开跌停", "blogger": "@Hoyooyoo"},
        {"symbol": "600132.ss", "date": "2025-03-15", "note": "突破 58 起飞", "blogger": "@Hoyooyoo"},
        {"symbol": "159755.sz", "date": "2025-06-12", "note": "做多信号", "blogger": "@Hoyooyoo"},
    ]
    print(f"[Info] Using {len(RECOMMENDATIONS)} default recommendations")

# 持有天数
HOLD_DAYS = 3

# 达标收益率 (%)
TARGET_RETURN = 5.0

# ==================== 主函数 ====================

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print("秋生 Trader (@Hoyooyoo) Twitter 荐股回测")
    print("=" * 70)
    print(f"样本数量：{len(RECOMMENDATIONS)}")
    print(f"持有天数：{HOLD_DAYS} 天")
    print(f"达标收益：{TARGET_RETURN}%")
    print()
    
    # 缓存数据
    print("正在下载数据...")
    data_cache = {}
    symbols = list(set(r['symbol'] for r in RECOMMENDATIONS))
    
    for symbol in symbols:
        try:
            print(f"  下载 {symbol}...")
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if len(df) > 0:
                # 处理列名
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index()
                if 'Date' in df.columns:
                    df = df.set_index('Date')
                elif 'date' in df.columns:
                    df = df.set_index('date')
                data_cache[symbol] = df
                print(f"    OK {symbol}: {len(df)} 天数据")
            else:
                print(f"    XX {symbol}: 无数据")
        except Exception as e:
            print(f"    XX {symbol}: {e}")
    
    print()
    print(f"成功加载 {len(data_cache)} 只股票/ETF 数据")
    print()
    
    if not data_cache:
        print("XX 没有可用数据，回测终止")
        return
    
    # 批量验证
    print("正在回测...")
    results = strategy.batch_validate(RECOMMENDATIONS, data_cache)
    
    if 'error' in results:
        print(f"错误：{results['error']}")
        return
    
    # 输出统计
    print()
    print("=" * 70)
    print("回测结果")
    print("=" * 70)
    print(f"总样本数：{results['total']}")
    print(f"通过率：{results['pass_rate']:.1f}% (符合观察池标准)")
    print(f"准确率：{results['accuracy']:.1f}% (通过后{HOLD_DAYS}天涨幅>{TARGET_RETURN}%)")
    print(f"假信号率：{results['false_rate']:.1f}% (通过后下跌)")
    print()
    
    # 详细结果
    print("=" * 70)
    print("详细结果")
    print("=" * 70)
    
    for r in results['details']:
        symbol = r['symbol']
        date = r['recommend_date']
        score = r['analysis']['score']
        rec = r['analysis']['recommendation']
        ret = r.get('return_pct', 'N/A')
        
        status = "OK" if r.get('success') == True else ("XX" if r.get('success') == False else "--")
        
        if ret is not None:
            ret_str = f"{ret:.1f}%"
        else:
            ret_str = "N/A"
        
        # 简化输出，避免 emoji 编码问题
        rec_clean = rec.encode('gbk', errors='ignore').decode('gbk')[:20]
        print(f"{status} {symbol} ({date}): {score} | {rec_clean} | return: {ret_str}")
    
    print()
    print("=" * 70)
    print("策略优化建议")
    print("=" * 70)
    
    if results['total'] < 10:
        print("[Warn] Sample size < 10, results for reference only")
        print("  Suggestion: Collect more historical recommendations")
    
    if results['accuracy'] < 50:
        print("[Warn] Accuracy < 50%, consider adjusting:")
        print("  1. Tighten trend confirmation conditions")
        print("  2. Add filters (RSI threshold, volume requirements)")
        print("  3. Adjust market comparison period")
    elif results['accuracy'] > 70:
        print("[OK] Good accuracy, ready for live testing")
    else:
        print("[Info] Medium accuracy, continue optimization")
    
    print()
    print("=" * 70)
    print("Next Steps")
    print("=" * 70)
    print("1. Collect more historical tweets from bloggers")
    print("2. Run import: python skills/twitter-distill/import_data.py --input data.xlsx")
    print("3. Re-run backtest: python strategy/backtest_twitter.py")
    print()

if __name__ == "__main__":
    main()
