"""
FastAPI 后端 - AI 个股分析 SaaS
使用 Akshare 数据源 (支持 serverless)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os
import pandas as pd
import akshare as ak

# 添加策略引擎路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from strategy.engine import PriceActionStrategy

app = FastAPI(title="PriceAction Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化策略引擎
strategy = PriceActionStrategy()

def fetch_stock_data(symbol: str) -> Optional[pd.DataFrame]:
    """获取股票日线数据 (使用 Akshare)"""
    try:
        # A 股代码转换
        if symbol.isdigit():
            if symbol.startswith('6'):
                symbol = f"sh{symbol}"
            else:
                symbol = f"sz{symbol}"
        
        # 获取历史数据
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        
        if len(df) < 60:
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
        
        # 转换数值类型
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

@app.get("/")
def root():
    return {"message": "PriceAction Pro API", "status": "running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/analyze")
def analyze_stock(symbol: str):
    """分析股票"""
    if not symbol:
        raise HTTPException(status_code=400, detail="缺少股票代码")
    
    # 获取数据
    df = fetch_stock_data(symbol)
    if df is None or len(df) < 60:
        raise HTTPException(status_code=400, detail=f"无法获取 {symbol} 的数据")
    
    # 执行分析
    result = strategy.analyze(symbol, df)
    
    return {
        "success": True,
        "symbol": symbol,
        "analysis": result
    }

@app.get("/api/popular")
def get_popular_stocks():
    """热门股票列表"""
    return {
        "stocks": [
            {"symbol": "600519", "name": "贵州茅台"},
            {"symbol": "000858", "name": "五粮液"},
            {"symbol": "300750", "name": "宁德时代"},
            {"symbol": "002594", "name": "比亚迪"},
            {"symbol": "000333", "name": "美的集团"}
        ]
    }
