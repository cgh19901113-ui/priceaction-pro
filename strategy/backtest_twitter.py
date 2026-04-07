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

RECOMMENDATIONS = [
    # 格式：{symbol: 股票代码，date: 推荐日期，note: 备注}
    
    # 2025-11-12: 中国中免
    {"symbol": "601888.ss", "date": "2025-11-12", "note": "大周期多头向上，有很大向上空间"},
    
    # 2025-09-19: 提到的股票 (跌停，反向验证)
    {"symbol": "002050.sz", "date": "2025-09-19", "note": "三花智控 - 跌停"},
    {"symbol": "600580.ss", "date": "2025-09-19", "note": "卧龙电驱 - 跌停"},
    {"symbol": "000981.sz", "date": "2025-09-19", "note": "山子高科 - 高开跌停"},
    
    # 2025-07-25: 华虹半导体 (港股数据问题，暂时移除)
    # {"symbol": "01347.hk", "date": "2025-07-25", "note": "华虹半导体 - 42 块是重大关口"},
    
    # 2025-03-15: 重庆啤酒
    {"symbol": "600132.ss", "date": "2025-03-15", "note": "重庆啤酒 - 说 55 就 55，突破 58 起飞"},
    
    # 2025-06-12: 电池板块 (做多信号) - 用电池 ETF 代表
    {"symbol": "159755.sz", "date": "2025-06-12", "note": "电池 ETF - 做多信号"},
]

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
        print(f"{status} {symbol} ({date}): {score}fen | {rec[:20]}... | shouyi: {ret_str}")
    
    print()
    print("=" * 70)
    print("策略优化建议")
    print("=" * 70)
    
    if results['total'] < 10:
        print("⚠️ 样本数量不足 (<10)，统计结果仅供参考")
        print("  建议：继续爬取更多历史荐股记录")
    
    if results['accuracy'] < 50:
        print("⚠️ 准确率偏低，建议调整:")
        print("  1. 收紧'趋势持续'确认条件 (增加连续阳线数量/放量倍数)")
        print("  2. 增加过滤条件 (如 RSI 阈值、振幅要求)")
        print("  3. 调整大盘对比周期 (10 日 vs 20 日)")
    elif results['accuracy'] > 70:
        print("OK 准确率良好，可以实盘测试")
    else:
        print("-- 准确率中等，建议继续优化")
    
    print()
    print("=" * 70)
    print("下一步")
    print("=" * 70)
    print("1. 继续爬取原博历史推文，收集更多荐股记录")
    print("2. 编辑 backtest_twitter.py 填充 RECOMMENDATIONS 列表")
    print("3. 重新运行回测：python strategy/backtest_twitter.py")
    print()

if __name__ == "__main__":
    main()
