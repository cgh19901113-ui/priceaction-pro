"""
FastAPI 后端 - PriceAction Pro Vercel 版
- 标准化信号输出
- 延迟免费 + 实时付费
- 公开信号记录
"""
import sys, os
# 确保能找到同目录模块

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib

from api import adapter, get_signals

app = FastAPI(title="PriceAction Pro API - Vercel")

# CORS（修了 typo: allow_origigins → allow_origins）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def hash_ip(ip: str):
    return hashlib.md5(ip.encode()).hexdigest()[:16]

# ==================== API 路由 ====================

@app.get("/")
def root():
    return {"message": "PriceAction Pro - 裸 K 信号", "version": "2.0.0"}

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze")
async def analyze(request: Request, req: AnalyzeRequest):
    """分析股票（免费：延迟信号 / 付费：实时信号）"""
    symbol = req.symbol.strip()
    
    # 验证股票代码
    clean = symbol.replace(".ss", "").replace(".sz", "").replace(".SH", "").replace(".SZ", "")
    if not clean or len(clean) < 6 or not clean[:6].isdigit():
        raise HTTPException(status_code=400, detail="无效的股票代码，请输入6位数字")
    
    symbol_clean = clean[:6]
    
    ip = get_client_ip(request)
    ip_hash = hash_ip(ip)
    
    # 免费额度检查
    if adapter.can_get_free_analysis(ip_hash):
        # 使用免费额度 → 延迟信号
        result = adapter.analyze_stock(symbol_clean, is_premium=False)
        adapter.use_free_analysis(ip_hash)
        
        if "error" in result:
            if result.get("error") == "PREMIUM_ONLY":
                return result
            return result
        
        user = adapter.get_user(ip_hash)
        result["remaining_free"] = max(0, adapter.FREE_DAILY - user["free_used_today"])
        result["is_premium"] = False
        return result
    else:
        # 免费额度用尽 → 返回付费引导
        return {
            "error": "FREE_LIMIT",
            "message": f"今日免费额度已用完（每日{adapter.FREE_DAILY}次）",
            "upgrade": {
                "plan": "实时信号",
                "price": "$30/月",
                "features": ["无限实时信号", "完整入场/失效条件", "优先推送"],
            },
            "is_premium": False,
        }

@app.get("/api/signals")
def get_public_signals(limit: int = 50):
    """获取公开信号记录"""
    signals = get_signals(limit=limit)
    return {"signals": signals, "total": len(signals)}

@app.post("/api/analyze/premium")
async def analyze_premium(request: Request, req: AnalyzeRequest):
    """付费用户实时分析（需验证 Token）"""
    symbol = req.symbol.strip()
    clean = symbol.replace(".ss", "").replace(".sz", "").replace(".SH", "").replace(".SZ", "")
    if not clean or len(clean) < 6 or not clean[:6].isdigit():
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    symbol_clean = clean[:6]
    
    # 验证付费 Token（从 Header 获取）
    token = request.headers.get("X-Api-Key", "")
    if not token or not _verify_premium_token(token):
        raise HTTPException(status_code=403, detail="无效的 API Key，请升级到付费计划")
    
    result = adapter.analyze_stock(symbol_clean, is_premium=True)
    if "error" in result:
        return result
    
    result["is_premium"] = True
    return result

def _verify_premium_token(token: str) -> bool:
    """验证付费 Token（简单实现，正式用数据库）"""
    return token.startswith("pa_") and len(token) > 10
