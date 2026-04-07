"""
秋生 Trader 策略批量回测 - A 股 1000+ 标的

使用 akshare 获取完整 A 股数据 (免费、国内数据源)
"""

import pandas as pd
import akshare as ak
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

def get_a_stock_list():
    """获取全部 A 股列表"""
    print("获取 A 股列表...")
    df = ak.stock_info_a_code_name()
    return df

def get_stock_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取个股历史数据"""
    try:
        # 格式化代码
        if symbol.startswith('6'):
            symbol = f"sh{symbol}"
        else:
            symbol = f"sz{symbol}"
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"  # 前复权
        )
        
        if len(df) == 0:
            return None
        
        # 重命名列
        df = df.rename(columns={
            '日期': 'Date',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        })
        
        df = df.set_index('Date')
        df.index = pd.to_datetime(df.index)
        
        return df
    except Exception as e:
        return None

def backtest_batch(stock_list: list, test_date: str, sample_size: int = 1000):
    """
    批量回测
    
    Args:
        stock_list: 股票列表
        test_date: 回测日期 (YYYY-MM-DD)
        sample_size: 回测样本数量
    """
    strategy = PriceActionStrategy()
    
    print("=" * 70)
    print(f"秋生 Trader 策略批量回测 - A 股 {sample_size}标的")
    print("=" * 70)
    print(f"回测日期：{test_date}")
    print(f"样本数量：{sample_size}")
    print()
    
    results = []
    processed = 0
    
    for _, row in stock_list.head(sample_size).iterrows():
        symbol = row['code']
        name = row['name']
        
        processed += 1
        if processed % 50 == 0:
            print(f"进度：{processed}/{sample_size} ({processed/sample_size*100:.1f}%)")
        
        # 获取历史数据 (回测日期前 1 年)
        test_dt = datetime.strptime(test_date, '%Y-%m-%d')
        start_dt = test_dt - timedelta(days=365)
        
        df = get_stock_history(
            symbol,
            start_dt.strftime('%Y-%m-%d'),
            test_dt.strftime('%Y-%m-%d')
        )
        
        if df is None or len(df) < 60:
            continue
        
        # 执行策略分析
        result = strategy.analyze(f"{symbol}.ss" if symbol.startswith('6') else f"{symbol}.sz", df)
        
        # 计算后 3 天收益
        try:
            test_idx = df.index.get_loc(test_dt)
            if test_idx + 3 < len(df):
                ret = (df['Close'].iloc[test_idx+3] - df['Close'].iloc[test_idx]) / df['Close'].iloc[test_idx] * 100
            else:
                ret = None
        except:
            ret = None
        
        passed = '观察池' in result['recommendation'] or '有点东西' in result['recommendation']
        
        results.append({
            'symbol': symbol,
            'name': name,
            'score': result['score'],
            'recommendation': result['recommendation'],
            'passed': passed,
            'return_3d': ret
        })
    
    # 统计
    print()
    print("=" * 70)
    print("回测结果")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    
    # 计算通过率
    pass_rate = passed / total * 100 if total > 0 else 0
    
    # 计算准确率 (通过的股票中赚钱的比例)
    passed_results = [r for r in results if r['passed'] and r['return_3d'] is not None]
    if len(passed_results) > 0:
        accuracy = sum(1 for r in passed_results if r['return_3d'] > 0) / len(passed_results) * 100
        avg_return = sum(r['return_3d'] for r in passed_results) / len(passed_results)
    else:
        accuracy = 0
        avg_return = 0
    
    print(f"总样本：{total}")
    print(f"策略通过：{passed} ({pass_rate:.1f}%)")
    print(f"准确率：{accuracy:.1f}% (通过股票中赚钱比例)")
    print(f"平均收益：{avg_return:.2f}% (通过股票 3 日平均)")
    print()
    
    # Top 10
    print("=" * 70)
    print("Top 10 推荐股票")
    print("=" * 70)
    
    passed_sorted = sorted(
        [r for r in results if r['passed'] and r['return_3d'] is not None],
        key=lambda x: x['return_3d'],
        reverse=True
    )[:10]
    
    for i, r in enumerate(passed_sorted, 1):
        print(f"{i}. {r['symbol']} ({r['name']}): {r['score']}分 | 3 日收益：{r['return_3d']:.1f}%")
    
    print()
    
    # 保存结果
    output_file = os.path.join(os.path.dirname(__file__), f'backtest_result_{test_date}.csv')
    pd.DataFrame(results).to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"结果已保存：{output_file}")
    
    return results

if __name__ == "__main__":
    # 获取 A 股列表
    stock_list = get_a_stock_list()
    print(f"共 {len(stock_list)} 只 A 股")
    print()
    
    # 回测日期 (用最近一个交易日)
    test_date = "2025-11-01"
    
    # 执行批量回测
    backtest_batch(stock_list, test_date, sample_size=1000)
