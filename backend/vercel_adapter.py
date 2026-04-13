"""
Vercel 适配器 - 无状态架构
使用内存数据库 + 外部 API 替代本地依赖
"""

import os
import json
from datetime import datetime, date
from typing import Optional, Dict, List
import requests

# 内存数据库（Vercel 无状态）
memory_db = {
    "users": {},
    "analyses": [],
    "payments": []
}

# 使用免费的 A 股数据 API（如腾讯财经）
def get_stock_data_tencent(symbol: str):
    """从腾讯财经获取股票数据"""
    try:
        # 转换股票代码格式
        if symbol.startswith('6'):
            code = f"sh{symbol}"
        else:
            code = f"sz{symbol}"
        
        url = f"http://qt.gtimg.cn/q={code}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # 解析腾讯财经数据
            data = response.text
            # 简化处理，实际需完整解析
            return {"data": data, "source": "tencent"}
        return None
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        return None

# 使用 mock 数据演示（无外部依赖）
def get_mock_stock_data(symbol: str):
    """生成模拟数据用于演示"""
    import random
    import pandas as pd
    
    # 生成 60 天模拟数据
    dates = pd.date_range(end=date.today(), periods=60, freq='B')
    base_price = random.uniform(10, 100)
    
    data = []
    for i, d in enumerate(dates):
        change = random.uniform(-0.05, 0.05)
        price = base_price * (1 + change)
        data.append({
            'date': d.strftime('%Y-%m-%d'),
            'open': price * 0.99,
            'high': price * 1.02,
            'low': price * 0.98,
            'close': price,
            'volume': random.randint(1000000, 10000000)
        })
        base_price = price
    
    return pd.DataFrame(data)

class VercelAdapter:
    """Vercel 无状态适配器"""
    
    def __init__(self):
        self.db = memory_db
    
    def get_user(self, ip_hash: str):
        """获取用户（内存）"""
        return self.db["users"].get(ip_hash, {
            "ip_hash": ip_hash,
            "credits": 3,
            "last_free_analysis": None
        })
    
    def update_user(self, ip_hash: str, data: dict):
        """更新用户（内存）"""
        self.db["users"][ip_hash] = data
    
    def save_analysis(self, user_id: str, symbol: str, analysis: dict):
        """保存分析记录"""
        self.db["analyses"].append({
            "user_id": user_id,
            "symbol": symbol,
            "analysis": analysis,
            "created_at": datetime.now().isoformat()
        })
    
    def analyze_stock(self, symbol: str):
        """分析股票（使用模拟数据）"""
        df = get_mock_stock_data(symbol)
        
        if df is None or len(df) < 60:
            return {
                "error": "数据不足",
                "message": "该股票历史数据少于60个交易日。请尝试：1) 主板股票如600519(茅台)、000001(平安银行) 2) 避免新股或近期复牌股票"
            }
        
        # 简单分析逻辑
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        change = (latest['close'] - prev['close']) / prev['close'] * 100
        
        return {
            "symbol": symbol,
            "current_price": round(latest['close'], 2),
            "change_percent": round(change, 2),
            "analysis": "基于模拟数据的分析演示",
            "recommendation": "观望" if abs(change) < 2 else ("买入" if change > 0 else "卖出"),
            "data_source": "模拟数据（Vercel 演示版）"
        }

# 全局适配器实例
adapter = VercelAdapter()