"""
FastAPI 后端 - Vercel 无状态版本
使用内存数据库 + 模拟数据
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib

# 导入 Vercel 适配器
from vercel_adapter import adapter

app = FastAPI(title="PriceAction Pro API - Vercel")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origigins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class AnalyzeRequest(BaseModel):
    symbol: str
    telegram_id: Optional[str] = None

# ==================== 工具函数 ====================

def get_client_ip(request: Request):
    """获取客户端 IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def hash_ip(ip: str):
    """IP 哈希"""
    return hashlib.md5(ip.encode()).hexdigest()[:16]

# ==================== API 路由 ====================

@app.get("/")
def root():
    return {"message": "PriceAction Pro API - Vercel", "version": "1.0.0"}

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze")
async def analyze(request: Request, req: AnalyzeRequest):
    """分析股票"""
    symbol = req.symbol.strip()
    
    # 验证股票代码
    if not symbol or len(symbol) != 6 or not symbol.isdigit():
        raise HTTPException(status_code=400, detail="无效的股票代码，请输入6位数字")
    
    # 获取用户信息
    ip = get_client_ip(request)
    ip_hash = hash_ip(ip)
    user = adapter.get_user(ip_hash)
    
    # 检查积分
    if user["credits"] <= 0:
        raise HTTPException(status_code=403, detail="免费次数已用完，请购买积分")
    
    # 执行分析
    result = adapter.analyze_stock(symbol)
    
    if "error" in result:
        return result
    
    # 扣除积分
    user["credits"] -= 1
    user["last_free_analysis"] = datetime.now().isoformat()
    adapter.update_user(ip_hash, user)
    
    # 保存分析记录
    adapter.save_analysis(ip_hash, symbol, result)
    
    return {
        "success": True,
        "remaining_credits": user["credits"],
        "analysis": result
    }

@app.get("/api/credits")
async def get_credits(request: Request):
    """获取剩余积分"""
    ip = get_client_ip(request)
    ip_hash = hash_ip(ip)
    user = adapter.get_user(ip_hash)
    
    return {
        "credits": user["credits"],
        "last_analysis": user.get("last_free_analysis")
    }

# Vercel 入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)