"""
Vercel Serverless API - PriceAction Pro
AI 股票分析系统 - 裸 K 策略 v3.1

数据源：Tushare (需要配置 TUSHARE_TOKEN)
备用：Akshare (如果 Tushare 不可用)
"""

import json
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

# 尝试导入 Tushare
try:
    import tushare as ts
    TS_AVAILABLE = True
    ts.set_token(os.environ.get('TUSHARE_TOKEN', ''))
    pro = ts.pro_api()
except:
    TS_AVAILABLE = False
    pro = None

# 尝试导入 Akshare
try:
    import akshare as ak
    AK_AVAILABLE = True
except:
    AK_AVAILABLE = False


def handler(request):
    """Vercel Serverless Handler"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS (CORS preflight)
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    # Parse query params from URL
    from urllib.parse import parse_qs, urlparse
    
    # Get query params
    symbol = ''
    if hasattr(request, 'query_params'):
        symbol = request.query_params.get('symbol', '')
    elif hasattr(request, 'args'):
        symbol = request.args.get('symbol', '')
    elif hasattr(request, 'url'):
        parsed = urlparse(request.url)
        params = parse_qs(parsed.query)
        symbol = params.get('symbol', [''])[0]
    
    if not symbol:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': '缺少股票代码 (示例：600519 或 600519.SH)'})
        }
    
    try:
        # 获取数据
        df = fetch_stock_data(symbol)
        if df is None or len(df) < 60:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': '数据不足，需要至少 60 个交易日'})
            }
        
        # 执行分析
        result = analyze_stock(symbol, df)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'symbol': symbol,
                'analysis': result,
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False)
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error: {error_detail}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'分析失败：{str(e)}', 'detail': error_detail})
        }


def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """获取股票数据"""
    
    # 标准化股票代码
    symbol = symbol.upper().replace('.', '')
    
    # 尝试使用 Tushare
    if TS_AVAILABLE and pro:
        try:
            df = pro.daily(ts_code=symbol, start_date='20200101', end_date='20261231')
            if len(df) > 0:
                df = df.sort_values('trade_date')
                df['Date'] = pd.to_datetime(df['trade_date'])
                df = df.set_index('Date')
                df = df.rename(columns={
                    'open': 'Open',
                    'close': 'Close',
                    'high': 'High',
                    'low': 'Low',
                    'vol': 'Volume'
                })
                return df[['Open', 'Close', 'High', 'Low', 'Volume']]
        except Exception as e:
            print(f"Tushare error: {e}")
    
    # Tushare 不可用，尝试 Akshare
    if AK_AVAILABLE:
        try:
            # 添加后缀
            if not any(symbol.endswith(suffix) for suffix in ['.SZ', '.SH', '.SS']):
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SH"
                else:
                    symbol = f"{symbol}.SZ"
            
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", timeout=30)
            if len(df) > 0:
                df = df.set_index('Date')
                df.index = pd.to_datetime(df.index)
                for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                return df[['Open', 'Close', 'High', 'Low', 'Volume']]
        except Exception as e:
            print(f"Akshare error: {e}")
    
    return None


def analyze_stock(symbol: str, df: pd.DataFrame) -> dict:
    """分析股票"""
    if len(df) < 60:
        return {"error": "数据不足"}
    
    indicators = {}
    
    # 1. 大周期趋势
    close = df['Close'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma60 = df['Close'].rolling(60).mean().iloc[-1]
    
    if close > ma20 and close > ma60:
        indicators['大周期'] = "看涨"
        indicators['大周期_颜色'] = "🟢"
    elif close < ma20 and close < ma60:
        indicators['大周期'] = "看跌"
        indicators['大周期_颜色'] = "🔴"
    else:
        indicators['大周期'] = "震荡"
        indicators['大周期_颜色'] = "⚪"
    
    # 2. 趋势持续天数
    ma20_series = df['Close'].rolling(20).mean()
    days = 0
    for i in range(len(df)-1, max(0, len(df)-20), -1):
        if df['Close'].iloc[i] > ma20_series.iloc[i]:
            days += 1
        else:
            break
    
    if days <= 3:
        indicators['趋势持续'] = f"{days}天"
        indicators['趋势持续_颜色'] = "🟢"
    elif days <= 10:
        indicators['趋势持续'] = f"{days}天"
        indicators['趋势持续_颜色'] = "🟠"
    else:
        indicators['趋势持续'] = f"{days}天 过期"
        indicators['趋势持续_颜色'] = "⚪"
    
    # 3. 大盘对比
    try:
        stock_ret = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10] * 100
        # 简化：假设大盘收益为 0
        bench_ret = 0
        diff = stock_ret - bench_ret
        if diff > 2:
            indicators['大盘对比'] = f"强于大盘 +{diff:.1f}%"
            indicators['大盘对比_颜色'] = "🔴"
        elif diff > 0:
            indicators['大盘对比'] = f"强于大盘 +{diff:.1f}%"
            indicators['大盘对比_颜色'] = "🟢"
        else:
            indicators['大盘对比'] = f"弱于大盘 {diff:.1f}%"
            indicators['大盘对比_颜色'] = "🟢"
    except:
        indicators['大盘对比'] = "数据不足"
        indicators['大盘对比_颜色'] = "⚪"
    
    # 4. 主力量能
    returns = df['Close'].pct_change()
    flow = (returns * df['Volume']).iloc[-10:].sum()
    flow_3d = (returns * df['Volume']).iloc[-3:].sum()
    if flow > 0 and flow_3d > 0:
        indicators['主力量能'] = "资金流入"
        indicators['主力量能_颜色'] = "🟢"
    elif flow < 0:
        indicators['主力量能'] = "资金流出"
        indicators['主力量能_颜色'] = "🔴"
    else:
        indicators['主力量能'] = "中性"
        indicators['主力量能_颜色'] = "⚪"
    
    # 5. 10 日振幅
    high = df['High'].iloc[-10:].max()
    low = df['Low'].iloc[-10:].min()
    amplitude = (high - low) / close * 100
    if amplitude > 12:
        indicators['10 日振幅'] = f"{amplitude:.1f}% 高弹性"
        indicators['10 日振幅_颜色'] = "🟣"
    elif amplitude >= 8:
        indicators['10 日振幅'] = f"{amplitude:.1f}% 蓄势中"
        indicators['10 日振幅_颜色'] = "🟢"
    else:
        indicators['10 日振幅'] = f"{amplitude:.1f}%"
        indicators['10 日振幅_颜色'] = "⚪"
    
    # 6. 当前信号 (根据评分动态生成)
    score = 0
    if indicators.get('大周期') == '看涨':
        score += 25
    if '强于大盘' in indicators.get('大盘对比', ''):
        score += 20
    if indicators.get('主力量能') == '资金流入':
        score += 20
    if '高弹性' in indicators.get('10 日振幅', ''):
        score += 10
    elif '蓄势中' in indicators.get('10 日振幅', ''):
        score += 5
    if days <= 3:
        score += 10
    
    if score >= 70:
        indicators['当前信号'] = "买入"
        indicators['当前信号_颜色'] = "🟢"
    elif score >= 40:
        indicators['当前信号'] = "持有"
        indicators['当前信号_颜色'] = "🟠"
    else:
        indicators['当前信号'] = "卖出"
        indicators['当前信号_颜色'] = "🔴"
    
    # 推荐
    if indicators.get('大周期') == '看跌':
        recommendation = "❌ Pass - 大周期看跌"
    elif '过期' in indicators.get('趋势持续', ''):
        recommendation = "❌ Pass - 趋势过期"
    elif score >= 50:
        recommendation = "✅ 观察池 - 有点东西"
    elif score >= 30:
        recommendation = "⚠️ 观望 - 等回踩"
    else:
        recommendation = "⚪ 观望"
    
    # 简评
    comments = []
    if indicators.get('大周期') == '看涨':
        comments.append("日线趋势向上")
    if days <= 3:
        comments.append("早期起涨")
    if indicators.get('主力量能') == '资金流入':
        comments.append("资金流入")
    comment = "，".join(comments) if comments else "等待明确信号"
    
    return {
        "indicators": indicators,
        "score": score,
        "recommendation": recommendation,
        "comment": comment
    }
