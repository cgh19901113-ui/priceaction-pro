"""
回测验证脚本 - 验证原博推荐股票的准确率

使用方法:
1. 收集原博 (@Hoyooyoo) 推荐过的股票列表
2. 填充 RECOMMENDATIONS 列表
3. 运行脚本查看统计结果

python strategy/backtest.py
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
import os

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategy.engine import PriceActionStrategy

# ==================== 配置区 ====================

# 原博推荐股票列表 (从 Twitter 手动收集)
# 格式：{symbol: 股票代码，date: 推荐日期 YYYY-MM-DD, note: 备注}
RECOMMENDATIONS = [
    # 示例数据 - 替换为真实推荐
    # {"symbol": "600519.ss", "date": "2026-03-01", "note": "起涨点"},
    
    # 测试数据 (用最近分析的日期)
    {"symbol": "600519.ss", "date": "2026-04-03", "note": "测试"},
    {"symbol": "300750.sz", "date": "2026-04-03", "note": "测试"},
]

# 持有天数
HOLD_DAYS = 3

# 达标收益率 (%)
TARGET_RETURN = 5.0

# ==================== 主函数 ====================

def main():
    strategy = PriceActionStrategy()
    
    print("=" * 60)
    print("秋生 Trader 策略回测验证")
    print("=" * 60)
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
            # 下载足够长的历史数据
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
    print(f"成功加载 {len(data_cache)} 只股票数据")
    print()
    
    if not data_cache:
        print("❌ 没有可用数据，回测终止")
        return
    
    # 批量验证
    print("正在回测...")
    results = strategy.batch_validate(RECOMMENDATIONS, data_cache)
    
    if 'error' in results:
        print(f"错误：{results['error']}")
        return
    
    # 输出统计
    print()
    print("=" * 60)
    print("回测结果")
    print("=" * 60)
    print(f"总样本数：{results['total']}")
    print(f"通过率：{results['pass_rate']:.1f}% (符合观察池标准)")
    print(f"准确率：{results['accuracy']:.1f}% (通过后{HOLD_DAYS}天涨幅>{TARGET_RETURN}%)")
    print(f"假信号率：{results['false_rate']:.1f}% (通过后下跌)")
    print()
    
    # 详细结果
    print("=" * 60)
    print("详细结果")
    print("=" * 60)
    
    for r in results['details']:
        symbol = r['symbol']
        date = r['recommend_date']
        score = r['analysis']['score']
        rec = r['analysis']['recommendation']
        ret = r.get('return_pct', 'N/A')
        
        status = "✅" if r.get('success') == True else ("❌" if r.get('success') == False else "⚪")
        
        if ret is not None:
            ret_str = f"{ret:.1f}%"
        else:
            ret_str = "N/A"
        
        print(f"{status} {symbol} ({date}): {score}分 | {rec} | 收益：{ret_str}")
    
    print()
    print("=" * 60)
    print("优化建议")
    print("=" * 60)
    
    if results['total'] < 10:
        print("⚠️ 样本数量不足 (<10)，统计结果仅供参考")
        print("  建议：收集至少 20 只推荐股票再回测")
    
    if results['accuracy'] < 50:
        print("⚠️ 准确率偏低，建议调整:")
        print("  1. 收紧'趋势持续'确认条件 (增加连续阳线数量/放量倍数)")
        print("  2. 增加过滤条件 (如 RSI 阈值、振幅要求)")
        print("  3. 调整大盘对比周期 (10 日 vs 20 日)")
    elif results['accuracy'] > 70:
        print("✅ 准确率良好，可以实盘测试")
    else:
        print("⚪ 准确率中等，建议继续优化")
    
    print()
    print("=" * 60)
    print("下一步")
    print("=" * 60)
    print("1. 收集更多原博推荐股票 (至少 20 只)")
    print("2. 编辑 strategy/backtest.py 填充 RECOMMENDATIONS 列表")
    print("3. 重新运行回测")
    print()

if __name__ == "__main__":
    main()
