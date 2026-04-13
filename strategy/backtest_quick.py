"""
秋生 Trader 策略快速回测 - 随机 100 只 A 股
"""

import pandas as pd
import akshare as ak
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

def get_random_stocks(n=100):
    """随机获取 N 只 A 股代码"""
    print(f"获取 A 股列表并随机选择 {n} 只...")
    try:
        df = ak.stock_info_a_code_name()
        codes = df['code'].tolist()
        # 只选 600/000/002/300 开头的
        codes = [c for c in codes if c.startswith('6') or c.startswith('0') or c.startswith('3')]
        selected = random.sample(codes, min(n, len(codes)))
        print(f"已选择：{selected[:10]}... (共{len(selected)}只)")
        return selected
    except Exception as e:
        print(f"获取失败：{e}")
        # 备用列表
        return [
            '600519', '000858', '300750', '000333', '002594',
            '601318', '600036', '000001', '600276', '000063',
            '600030', '601166', '600588', '002415', '300059',
            '600887', '000568', '600900', '601888', '000002',
            '600048', '000100', '600585', '002304', '000725',
            '601288', '601988', '601398', '601668', '600028',
            '600050', '000776', '600518', '000538', '600276',
            '600436', '000425', '600745', '000009', '600104',
            '000651', '000977', '002230', '002049', '600703',
            '300274', '300014', '300316', '300450', '300760',
            '688012', '688981', '688599', '688005', '688111',
            '002714', '002001', '000895', '000999', '600196',
            '600763', '000661', '300122', '300601', '300529',
            '002821', '002920', '002466', '002129', '002192',
            '601012', '600438', '000860', '000908', '000718',
            '600009', '600115', '600029', '601021', '600019',
            '600690', '000625', '000937', '600547', '600489',
            '000878', '000630', '600309', '600141', '600256',
            '600160', '600346', '600989', '000059', '000060'
        ]

def get_stock_history(symbol: str, days=365) -> pd.DataFrame:
    """获取个股历史数据"""
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        if len(df) == 0:
            return None
        
        df = df.rename(columns={
            '日期': 'Date', '开盘': 'Open', '收盘': 'Close',
            '最高': 'High', '最低': 'Low', '成交量': 'Volume'
        })
        df = df.set_index('Date')
        df.index = pd.to_datetime(df.index)
        
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        return None

def backtest_quick(stock_codes: list, test_days_ago=3):
    """
    快速回测
    
    逻辑：
    1. 获取每只股票历史数据
    2. 用 test_days_ago 天前的数据做分析
    3. 计算之后 3 天的实际收益
    """
    strategy = PriceActionStrategy()
    
    test_date = datetime.now() - timedelta(days=test_days_ago)
    test_date_str = test_date.strftime('%Y-%m-%d')
    
    print("=" * 70)
    print("秋生 Trader 策略快速回测 - 随机 100 只 A 股")
    print("=" * 70)
    print(f"回测基准日：{test_date_str}")
    print(f"持有期：3 天")
    print()
    
    results = []
    
    for i, symbol in enumerate(stock_codes):
        if i % 20 == 0:
            print(f"进度：{i}/{len(stock_codes)}")
        
        # 获取历史数据 (需要包含测试日之后 3 天)
        df = get_stock_history(symbol, days=test_days_ago + 10)
        
        if df is None or len(df) < 60:
            continue
        
        # 找到测试日索引
        try:
            # 找最接近 test_date 的日期
            test_idx = df.index.get_indexer([test_date], method='nearest')[0]
            if test_idx < 0 or test_idx >= len(df) - 3:
                continue
            
            # 截取测试日之前的数据做分析
            df_before = df.iloc[:test_idx+1]
            
            if len(df_before) < 60:
                continue
            
            # 执行策略分析
            full_symbol = f"{symbol}.ss" if symbol.startswith('6') else f"{symbol}.sz"
            result = strategy.analyze(full_symbol, df_before)
            
            # 计算之后 3 天收益
            buy_price = df['Close'].iloc[test_idx]
            sell_price = df['Close'].iloc[test_idx + 3]
            ret_3d = (sell_price - buy_price) / buy_price * 100
            
            passed = '观察池' in result['recommendation'] or '有点东西' in result['recommendation']
            
            results.append({
                'symbol': symbol,
                'score': result['score'],
                'recommendation': result['recommendation'],
                'passed': passed,
                'return_3d': ret_3d
            })
            
        except Exception as e:
            continue
    
    # 统计
    print()
    print("=" * 70)
    print("回测结果")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    pass_rate = passed / total * 100 if total > 0 else 0
    
    # 准确率
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
    
    # Top 5
    if passed_results:
        print("=" * 70)
        print("Top 5 推荐股票")
        print("=" * 70)
        top5 = sorted(passed_results, key=lambda x: x['return_3d'], reverse=True)[:5]
        for i, r in enumerate(top5, 1):
            print(f"{i}. {r['symbol']}: {r['score']}分 | 3 日收益：{r['return_3d']:.1f}%")
    
    # 保存
    output_file = os.path.join(os.path.dirname(__file__), f'backtest_quick_{test_date_str}.csv')
    pd.DataFrame(results).to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存：{output_file}")
    
    return results

if __name__ == "__main__":
    stocks = get_random_stocks(100)
    backtest_quick(stocks, test_days_ago=5)
