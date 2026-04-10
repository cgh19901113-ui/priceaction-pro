"""
Vercel Serverless API - PriceAction Pro
AI 股票分析系统 - 裸 K 策略 v3.1

Using FastAPI for Vercel Serverless Functions
See: https://github.com/vercel/examples/tree/main/python/fastapi
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import os

app = FastAPI(title="PriceAction Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/api")
async def read_root():
    return {"message": "PriceAction Pro API", "status": "running"}


@app.get("/api/analyze")
async def analyze_stock(symbol: str = Query(..., description="Stock symbol (e.g., 600519 or 600519.SH)")):
    """Analyze stock with 6 indicators"""
    try:
        # Fetch stock data
        df = fetch_stock_data(symbol)
        if df is None or len(df) < 60:
            raise HTTPException(status_code=400, detail="数据不足，需要至少 60 个交易日")
        
        # Analyze stock
        result = analyze_stock_data(symbol, df)
        
        return {
            "success": True,
            "symbol": symbol,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败：{str(e)}")


def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """Fetch stock data from itick.org (Volcengine)"""
    try:
        # Normalize symbol
        symbol = symbol.upper().replace('.', '')
        
        # Determine market region and code
        if symbol.startswith('6'):
            region = 'SH'
            code = symbol
        elif symbol.startswith('0') or symbol.startswith('3'):
            region = 'SZ'
            code = symbol
        else:
            region = 'SH'  # Default to SH
            code = symbol
        
        print(f"Fetching data for {region}:{code}...")
        
        # Get token from environment variable
        token = os.environ.get('ITICK_TOKEN', 'MTllMmMyMThhMDM2NGZlNWIzNjJjMWViMzU2YzgxODY')
        
        # Fetch K-line data from itick.org
        url = "https://api.itick.org/stock/kline"
        headers = {
            "accept": "application/json",
            "token": token
        }
        params = {
            "type": "stock",
            "region": region,
            "code": code,
            "period": "day"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"API Response code: {result.get('code')}")
        
        if result.get('code') != 0:
            print(f"API Error: {result.get('msg')}")
            return None
        
        # Parse data
        data = result.get('data', {})
        klines = data.get('kline', [])
        
        if not klines or len(klines) == 0:
            print("No K-line data returned")
            return None
        
        print(f"Fetched {len(klines)} rows")
        
        # Convert to DataFrame
        # Expected format: [timestamp, open, close, high, low, volume, ...]
        df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'Close', 'High', 'Low', 'Volume', 'turnover', 'change', 'change_ratio'])
        
        # Convert timestamp to datetime
        df['Date'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.set_index('Date')
        
        # Convert numeric columns
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df[['Open', 'Close', 'High', 'Low', 'Volume']]
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {type(e).__name__}: {e}")
        return None


def analyze_stock_data(symbol: str, df: pd.DataFrame) -> dict:
    """Analyze stock with 6 indicators"""
    if len(df) < 60:
        return {"error": "数据不足"}
    
    indicators = {}
    
    # 1. Major Trend (MA20/MA60)
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
    
    # 2. Trend Duration
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
    
    # 3. Market Comparison (simplified)
    try:
        stock_ret = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10] * 100
        diff = stock_ret
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
    
    # 4. Volume Flow
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
    
    # 5. 10-Day Amplitude
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
    
    # 6. Signal (based on score)
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
    
    # Recommendation
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
    
    # Comment
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
