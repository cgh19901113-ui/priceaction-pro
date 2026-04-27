"""
Vercel 适配器 - 无状态架构
数据源: Yahoo Finance 直接 API（全球可访问）
分析输出: 标准化信号格式
定价: 延迟信号免费 / 实时信号付费
"""
import os, json, random, hashlib, hmac, base64
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List

# ========== 信号记录（公开） ==========
SIGNAL_LOG: List[Dict] = []  # 内存记录，Vercel 每次冷启动重置

def add_signal(signal: dict):
    """添加信号到公开记录"""
    signal["id"] = hashlib.md5(f"{signal['symbol']}{signal['timestamp']}".encode()).hexdigest()[:8]
    signal["timestamp"] = datetime.now().isoformat()
    signal["result"] = "待验证"
    SIGNAL_LOG.append(signal)
    if len(SIGNAL_LOG) > 200:
        SIGNAL_LOG.pop(0)

def get_signals(limit: int = 50) -> List[Dict]:
    """获取公开信号记录"""
    return sorted(SIGNAL_LOG, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

# ========== 数据源 ==========
def get_stock_data(symbol: str) -> Optional[List[Dict]]:
    """
    从 Yahoo Finance 直接 API 获取 A 股数据（全球可访问）
    返回: [{date, open, high, low, close, volume}, ...]
    """
    try:
        import requests

        if symbol.startswith('6') or symbol.startswith('9'):
            yahoo_symbol = f"{symbol}.SS"
        else:
            yahoo_symbol = f"{symbol}.SZ"

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        params = {"range": "1y", "interval": "1d", "includePrePost": "false"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code != 200:
            print(f"Yahoo API 返回 {resp.status_code} for {yahoo_symbol}")
            return None

        data = resp.json()
        result_data = data.get("chart", {}).get("result", [])
        if not result_data:
            print(f"Yahoo API 无数据 for {yahoo_symbol}")
            return None

        timestamps = result_data[0].get("timestamp", [])
        quotes = result_data[0].get("indicators", {}).get("quote", [{}])[0]
        opens = quotes.get("open", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        closes = quotes.get("close", [])
        volumes = quotes.get("volume", [])

        if not timestamps or len(timestamps) < 60:
            print(f"数据不足 {symbol}: 仅 {len(timestamps)} 条")
            return None

        result = []
        for i in range(len(timestamps)):
            if closes[i] is None or opens[i] is None:
                continue
            dt = datetime.fromtimestamp(timestamps[i])
            result.append({
                "date": dt.strftime("%Y-%m-%d"),
                "open": round(float(opens[i]), 2),
                "high": round(float(highs[i]), 2),
                "low": round(float(lows[i]), 2),
                "close": round(float(closes[i]), 2),
                "volume": int(volumes[i]) if volumes[i] else 0,
            })

        print(f"Yahoo Finance 获取 {symbol} ({yahoo_symbol}): {len(result)} 条")
        return result
    except Exception as e:
        print(f"数据获取失败 {symbol}: {e}")
        return None

# ========== 信号分析引擎 ==========
def analyze_price_action(df: List[Dict]) -> Dict:
    """裸 K 价格行为分析 - 返回标准化信号"""
    if not df or len(df) < 20:
        return {"error": "数据不足，至少需要 20 个交易日"}

    closes = [d["close"] for d in df]
    highs = [d["high"] for d in df]
    lows = [d["low"] for d in df]
    volumes = [d["volume"] for d in df]

    current_price = closes[-1]
    change_pct = (closes[-1] - closes[-2]) / closes[-2] * 100

    # ===== 结构判断 =====
    recent_high = max(highs[-20:])
    recent_low = min(lows[-20:])
    mid_price = (recent_high + recent_low) / 2

    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20

    if current_price > ma5 > ma10 > ma20 and current_price > mid_price:
        structure = "上升趋势"
    elif current_price < ma5 < ma10 < ma20 and current_price < mid_price:
        structure = "下降趋势"
    elif abs(current_price - mid_price) / mid_price < 0.03:
        structure = "横盘震荡"
    elif current_price > ma20 and ma5 > ma20:
        structure = "偏多震荡"
    else:
        structure = "偏空震荡"

    # ===== 方向判断 =====
    if closes[-1] > max(highs[-6:-1]) and volumes[-1] > sum(volumes[-6:-1]) / 5 * 1.5:
        direction = "做多"
        entry_condition = f"突破 {max(highs[-6:-1]):.2f} 放量确认"
        invalidate = f"跌破 {min(lows[-3:]):.2f}"
        confidence = "高"
    elif closes[-1] < min(lows[-6:-1]):
        direction = "做空"
        entry_condition = f"跌破 {min(lows[-6:-1]):.2f}"
        invalidate = f"突破 {max(highs[-3:]):.2f}"
        confidence = "中"
    elif closes[-1] > closes[-2] and closes[-2] > closes[-3] and volumes[-1] > volumes[-2]:
        direction = "偏多"
        entry_condition = f"回踩 {ma10:.2f} 不破"
        invalidate = f"跌破 {ma20:.2f}"
        confidence = "中低"
    elif closes[-1] < closes[-2] and closes[-2] < closes[-3]:
        direction = "偏空"
        entry_condition = "等待止跌信号"
        invalidate = f"突破 {ma10:.2f}"
        confidence = "低"
    else:
        direction = "观望"
        entry_condition = f"突破 {recent_high:.2f} 或 回踩 {recent_low:.2f}"
        invalidate = "无明确方向"
        confidence = "低"

    # ===== 量能确认 =====
    avg_vol = sum(volumes[-10:]) / 10
    vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 1
    volume_signal = "放量" if vol_ratio > 1.3 else ("缩量" if vol_ratio < 0.7 else "平量")

    # ===== 置信度评分 =====
    score = 50
    if structure in ("上升趋势", "偏多震荡"):
        score += 15
    if direction == "做多" and volume_signal == "放量":
        score += 20
    elif direction == "做空" and volume_signal == "放量":
        score += 10
    if vol_ratio > 1.5:
        score += 10
    if confidence == "高":
        score += 15
    elif confidence == "中":
        score += 5
    score = min(max(score, 0), 100)

    return {
        "symbol": "",
        "current_price": round(current_price, 2),
        "change_pct": round(change_pct, 2),
        "direction": direction,
        "structure": structure,
        "entry_condition": entry_condition,
        "invalidate_condition": invalidate,
        "confidence": confidence,
        "score": score,
        "volume_signal": volume_signal,
        "volume_ratio": round(vol_ratio, 2),
        "support": round(recent_low, 2),
        "resistance": round(recent_high, 2),
        "ma5": round(ma5, 2),
        "ma10": round(ma10, 2),
        "ma20": round(ma20, 2),
    }


class VercelAdapter:
    """Vercel 无状态适配器"""
    FREE_DAILY = 1
    SIGNAL_DELAY = 24

    def __init__(self):
        self.db = {"users": {}, "analyses": []}

    def get_user(self, ip_hash: str) -> dict:
        today = date.today().isoformat()
        user = self.db["users"].get(ip_hash, {
            "ip_hash": ip_hash, "is_premium": False,
            "free_used_today": 0, "free_date": today, "total_analyses": 0,
        })
        if user.get("free_date") != today:
            user["free_used_today"] = 0
            user["free_date"] = today
        return user

    def update_user(self, ip_hash: str, data: dict):
        self.db["users"][ip_hash] = data

    def can_get_free_analysis(self, ip_hash: str) -> bool:
        return self.get_user(ip_hash)["free_used_today"] < self.FREE_DAILY

    def use_free_analysis(self, ip_hash: str):
        user = self.get_user(ip_hash)
        user["free_used_today"] += 1
        user["total_analyses"] += 1
        self.update_user(ip_hash, user)

    def analyze_stock(self, symbol: str, is_premium: bool = False) -> Dict:
        df = get_stock_data(symbol)
        if not df:
            return {"error": "数据不足", "message": "无法获取该股票数据，请检查代码是否正确"}

        analysis = analyze_price_action(df)
        analysis["symbol"] = symbol
        if "error" in analysis:
            return analysis

        if not is_premium:
            analysis["entry_condition"] = "🔒 实时入场条件仅对付费用户开放"
            analysis["invalidate_condition"] = "🔒 升级后可查看"
            analysis["data_source"] = f"延迟信号（D-{self.SIGNAL_DELAY}h）"
        else:
            analysis["data_source"] = "实时信号"

        add_signal({
            "symbol": symbol,
            "direction": analysis.get("direction", "观望"),
            "structure": analysis.get("structure", ""),
            "confidence": analysis.get("confidence", "低"),
            "price": analysis.get("current_price", 0),
            "is_premium": is_premium,
        })
        return analysis

adapter = VercelAdapter()
