"""
FastAPI 后端 - AI 个股分析 SaaS
仅支持 A 股/港股，使用 Baostock 免费国内数据源
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sqlite3
import hashlib
from datetime import datetime, date
import sys
import os
import pandas as pd
import baostock as bs  # 免费国内数据源

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategy.engine import PriceActionStrategy

# 初始化 Baostock
bs.login()

app = FastAPI(title="PriceAction Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化策略引擎
strategy = PriceActionStrategy()

# 数据库初始化
def init_db():
    conn = sqlite3.connect("priceaction.db")
    cursor = conn.cursor()
    
    # users 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_hash TEXT UNIQUE,
            telegram_id TEXT,
            credits INTEGER DEFAULT 1,
            last_free_analysis DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # analyses 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            analysis_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # payments 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            credits_added INTEGER,
            status TEXT,
            nowpayments_id TEXT,
            created_at DATETIME
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ==================== 数据模型 ====================

class AnalyzeRequest(BaseModel):
    symbol: str
    telegram_id: Optional[str] = None

class PaymentRequest(BaseModel):
    amount: float  # USDT 数量
    currency: str = "USDT"

class PaymentCallback(BaseModel):
    order_id: str
    payment_status: str
    pay_address: str
    price_amount: float
    actually_paid: float

# ==================== 辅助函数 ====================

def get_user_by_ip(ip: str) -> Dict:
    """根据 IP 获取或创建用户"""
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
    
    conn = sqlite3.connect("priceaction.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE ip_hash = ?", (ip_hash,))
    user = cursor.fetchone()
    
    if not user:
        # 创建新用户，赠送 3 次免费分析
        cursor.execute(
            "INSERT INTO users (ip_hash, credits, last_free_analysis) VALUES (?, ?, ?)",
            (ip_hash, 3, date.today().isoformat())
        )
        conn.commit()
        user_id = cursor.lastrowid
        credits = 3
    else:
        user_id, user_ip_hash, telegram_id, credits, last_free, created = user
        
        # 检查是否可以重置免费次数 (每天赠送 1 次)
        if last_free != date.today().isoformat():
            cursor.execute(
                "UPDATE users SET credits = credits + 1, last_free_analysis = ? WHERE id = ?",
                (date.today().isoformat(), user_id)
            )
            conn.commit()
            credits += 1
    
    conn.close()
    
    return {"id": user_id, "ip_hash": ip_hash, "credits": credits}

def fetch_stock_data(symbol: str) -> Optional[pd.DataFrame]:
    """获取股票日线数据 (使用 Baostock)"""
    try:
        # 格式化代码为 baostock 格式 (sh.600519)
        # Baostock 要求：sh.600519 (9 位代码)，不区分大小写
        symbol_upper = symbol.upper()
        
        if symbol_upper.endswith('.SS'):
            code = symbol_upper.replace('.SS', '')
            stock_code = f"sh.{code}"
        elif symbol_upper.endswith('.SZ'):
            code = symbol_upper.replace('.SZ', '')
            stock_code = f"sz.{code}"
        elif symbol_upper.endswith('.HK'):
            code = symbol_upper.replace('.HK', '')
            stock_code = f"HK.{code}"
        else:
            # 如果是纯数字，添加前缀
            code = symbol_upper
            if code.startswith('6'):
                stock_code = f"sh.{code}"
            elif code.startswith('0') or code.startswith('3'):
                stock_code = f"sz.{code}"
            else:
                stock_code = code
        
        print(f"Fetching data for {symbol} -> {stock_code}")
        
        # 获取近 100 天数据 (前复权)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.Timedelta(days=365)).strftime('%Y-%m-%d')
        
        rs = bs.query_history_k_data_plus(
            stock_code,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"  # 前复权
        )
        
        if rs.error_code != '0':
            print(f"Error fetching {symbol}: {rs.error_msg}")
            return None
        
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            print(f"No data for {symbol}")
            return None
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 重命名列
        df = df.rename(columns={
            'date': 'Date',
            'open': 'Open',
            'close': 'Close',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume'
        })
        
        df = df.set_index('Date')
        df.index = pd.to_datetime(df.index)
        
        # 转换数值类型
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"Got {len(df)} records for {symbol}")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def fetch_15m_data(symbol: str) -> Optional[pd.DataFrame]:
    """获取 15 分钟线数据 (使用 Baostock)"""
    try:
        # 格式化代码
        if symbol.endswith('.ss'):
            stock_code = f"sh.{symbol.replace('.ss', '')}"
        elif symbol.endswith('.sz'):
            stock_code = f"sz.{symbol.replace('.sz', '')}"
        else:
            stock_code = symbol
        
        # 获取 15 分钟数据 (最近 5 天)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.Timedelta(days=10)).strftime('%Y-%m-%d')
        
        rs = bs.query_history_k_data_plus(
            stock_code,
            "date,time,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="15",
            adjustflag="2"
        )
        
        if rs.error_code != '0':
            return None
        
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            return None
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 重命名列
        df = df.rename(columns={
            'date': 'Date',
            'time': 'Time',
            'open': 'Open',
            'close': 'Close',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume'
        })
        
        # 合并日期时间
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df = df.set_index('Datetime')
        
        # 转换数值类型
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error fetching 15m data for {symbol}: {e}")
        return None

# ==================== API 路由 ====================

@app.get("/")
def root():
    return {"message": "PriceAction Pro API", "status": "running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze")
def analyze_stock(request: AnalyzeRequest, client: Request):
    """
    分析股票
    
    - 检查用户积分
    - 执行分析
    - 扣除积分
    - 返回结果
    """
    # 获取用户
    user = get_user_by_ip(client.client.host)
    
    if user['credits'] <= 0:
        raise HTTPException(status_code=402, detail="积分不足，请充值 1 USDT = 5 次分析")
    
    # 获取数据
    symbol = request.symbol.upper()
    
    # A 股代码转换
    if symbol.isdigit():
        if symbol.startswith('6'):
            symbol = f"{symbol}.ss"
        else:
            symbol = f"{symbol}.sz"
    
    df_daily = fetch_stock_data(symbol)
    if df_daily is None or len(df_daily) < 60:
        raise HTTPException(status_code=400, detail="无法获取股票数据，请检查代码")
    
    df_15m = fetch_15m_data(symbol)
    
    # 执行分析
    result = strategy.analyze(symbol, df_daily, df_15m)
    
    # 扣除积分
    conn = sqlite3.connect("priceaction.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET credits = credits - 1 WHERE id = ?",
        (user['id'],)
    )
    
    # 保存分析记录
    cursor.execute(
        "INSERT INTO analyses (user_id, symbol, analysis_data) VALUES (?, ?, ?)",
        (user['id'], symbol, str(result))
    )
    
    conn.commit()
    conn.close()
    
    # 返回结果
    return {
        "success": True,
        "remaining_credits": user['credits'] - 1,
        "analysis": result
    }

@app.get("/api/daily-free/{ip}")
def check_daily_free(ip: str):
    """检查每日免费额度"""
    user = get_user_by_ip(ip)
    return {
        "available": user['credits'] > 0,
        "credits": user['credits']
    }

@app.post("/api/payment/create")
def create_payment(request: PaymentRequest, client: Request):
    """
    创建支付订单
    
    集成 NowPayments
    """
    # TODO: 集成 NowPayments API
    # 这里先返回模拟数据
    
    order_id = f"PA{datetime.now().strftime('%Y%m%d%H%M%S')}"
    credits = int(request.amount * 5)  # 1U = 5 次
    
    return {
        "order_id": order_id,
        "amount": request.amount,
        "currency": request.currency,
        "credits": credits,
        "payment_url": f"https://nowpayments.io/payment/?iid={order_id}",
        "status": "pending"
    }

@app.post("/api/payment/callback")
def payment_callback(callback: PaymentCallback):
    """
    NowPayments 支付回调
    
    - 验证签名
    - 更新订单状态
    - 充值积分
    """
    # TODO: 实现支付回调逻辑
    
    return {"status": "received"}

@app.get("/api/stock/{symbol}")
def get_stock_info(symbol: str):
    """获取股票基本信息"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "symbol": symbol,
            "name": info.get('shortName', ''),
            "price": info.get('currentPrice', 0),
            "change": info.get('regularMarketChangePercent', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/popular")
def get_popular_stocks():
    """获取热门股票列表"""
    popular = [
        {"symbol": "600519.ss", "name": "贵州茅台"},
        {"symbol": "000858.sz", "name": "五粮液"},
        {"symbol": "300750.sz", "name": "宁德时代"},
        {"symbol": "000333.sz", "name": "美的集团"},
        {"symbol": "002594.sz", "name": "比亚迪"},
    ]
    return {"stocks": popular}

# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
