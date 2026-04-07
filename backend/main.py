"""
FastAPI 后端 - AI 个股分析 SaaS
使用 Akshare 数据源 (支持 serverless)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime

app = FastAPI(title="PriceAction Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 策略引擎 (内联) ====================

class PriceActionStrategy:
    """裸 K 策略引擎 - 简化版"""
    
    def __init__(self):
        self.BENCHMARK = "000300.ss"
    
    def analyze(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """完整分析流程"""
        if len(df) < 60:
            return {"error": "数据不足"}
        
        indicators = {}
        
        # 1. 大周期趋势
        indicators['大周期'], indicators['大周期_颜色'] = self._calc_trend(df)
        
        # 2. 趋势持续天数
        indicators['趋势持续'], indicators['趋势持续_颜色'] = self._calc_duration(df)
        
        # 3. 大盘对比
        indicators['大盘对比'], indicators['大盘对比_颜色'] = self._calc_market_compare(symbol, df)
        
        # 4. 主力量能
        indicators['主力量能'], indicators['主力量能_颜色'] = self._calc_flow(df)
        
        # 5. 10 日振幅
        indicators['10 日振幅'], indicators['10 日振幅_颜色'] = self._calc_amplitude(df)
        
        # 6. 当前信号
        indicators['当前信号'], indicators['当前信号_颜色'] = "中性", "⚪"
        
        # 评分
        score = self._calc_score(indicators)
        recommendation = self._get_recommendation(score, indicators)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "score": score,
            "recommendation": recommendation,
            "comment": self._generate_comment(indicators)
        }
    
    def _calc_trend(self, df: pd.DataFrame) -> tuple:
        """大周期趋势"""
        close = df['Close'].iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma60 = df['Close'].rolling(60).mean().iloc[-1]
        
        if close > ma20 and close > ma60:
            return "看涨", "🟢"
        elif close < ma20 and close < ma60:
            return "看跌", "🔴"
        else:
            return "震荡", "⚪"
    
    def _calc_duration(self, df: pd.DataFrame) -> tuple:
        """趋势持续天数"""
        close = df['Close']
        ma20 = close.rolling(20).mean()
        
        # 计算连续在 MA20 上的天数
        days = 0
        for i in range(len(df)-1, max(0, len(df)-20), -1):
            if close.iloc[i] > ma20.iloc[i]:
                days += 1
            else:
                break
        
        if days <= 3:
            return f"{days}天", "🟢"
        elif days <= 10:
            return f"{days}天", "🟠"
        else:
            return f"{days}天 过期", "⚪"
    
    def _calc_market_compare(self, symbol: str, df: pd.DataFrame) -> tuple:
        """大盘对比"""
        try:
            stock_ret = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10] * 100
            
            # 获取沪深 300
            benchmark = ak.stock_zh_index_hist(symbol="sh000300", period="daily")
            if len(benchmark) > 10:
                bench_ret = (benchmark['收盘'].iloc[-1] - benchmark['收盘'].iloc[-10]) / benchmark['收盘'].iloc[-10] * 100
            else:
                bench_ret = 0
            
            diff = stock_ret - bench_ret
            
            if diff > 2:
                return f"强于大盘 +{diff:.1f}%", "🔴"
            elif diff > 0:
                return f"强于大盘 +{diff:.1f}%", "🟢"
            else:
                return f"弱于大盘 {diff:.1f}%", "🟢"
        except:
            return "数据不足", "⚪"
    
    def _calc_flow(self, df: pd.DataFrame) -> tuple:
        """主力量能"""
        returns = df['Close'].pct_change()
        flow = (returns * df['Volume']).iloc[-10:].sum()
        flow_3d = (returns * df['Volume']).iloc[-3:].sum()
        
        if flow > 0 and flow_3d > 0:
            return "资金流入", "🟢"
        elif flow < 0:
            return "资金流出", "🔴"
        else:
            return "中性", "⚪"
    
    def _calc_amplitude(self, df: pd.DataFrame) -> tuple:
        """10 日振幅"""
        high = df['High'].iloc[-10:].max()
        low = df['Low'].iloc[-10:].min()
        close = df['Close'].iloc[-1]
        
        amplitude = (high - low) / close * 100
        
        if amplitude > 12:
            return f"{amplitude:.1f}% 高弹性", "🟣"
        elif amplitude >= 8:
            return f"{amplitude:.1f}% 蓄势中", "🟢"
        else:
            return f"{amplitude:.1f}% 低波动", "⚪"
    
    def _calc_score(self, indicators: Dict) -> int:
        """评分系统"""
        score = 0
        
        # 趋势持续 (0-10 分)
        duration = indicators.get('趋势持续', '')
        if '1 天' in duration or '2 天' in duration or '3 天' in duration:
            score += 10
        elif '4 天' in duration or '5 天' in duration:
            score += 5
        
        # 大周期 (0-10 分)
        if indicators.get('大周期') == '看涨':
            score += 10
        
        # 大盘对比 (0-10 分)
        if '强于大盘' in indicators.get('大盘对比', ''):
            score += 10
        
        # 主力量能 (0-10 分)
        if indicators.get('主力量能') == '资金流入':
            score += 10
        
        # 10 日振幅 (0-10 分)
        if '高弹性' in indicators.get('10 日振幅', ''):
            score += 10
        elif '蓄势中' in indicators.get('10 日振幅', ''):
            score += 5
        
        # 当前信号 (0-10 分)
        if indicators.get('当前信号') == '看涨':
            score += 10
        
        return score
    
    def _get_recommendation(self, score: int, indicators: Dict) -> str:
        """推荐"""
        if indicators.get('大周期') == '看跌':
            return "❌ Pass - 大周期看跌"
        
        if '过期' in indicators.get('趋势持续', ''):
            return "❌ Pass - 趋势过期"
        
        if score >= 50:
            return "✅ 观察池 - 有点东西"
        elif score >= 30:
            return "⚠️ 观望 - 等回踩"
        else:
            return "⚪ 观望"
    
    def _generate_comment(self, indicators: Dict) -> str:
        """简评"""
        comments = []
        
        if indicators.get('大周期') == '看涨':
            comments.append("日线趋势向上")
        
        duration = indicators.get('趋势持续', '')
        if '1 天' in duration or '2 天' in duration:
            comments.append("早期起涨")
        
        if indicators.get('主力量能') == '资金流入':
            comments.append("资金流入")
        
        if '强于大盘' in indicators.get('大盘对比', ''):
            comments.append("强于大盘")
        
        if '高弹性' in indicators.get('10 日振幅', ''):
            comments.append("高弹性")
        
        return "，".join(comments[:3]) + "，有点东西" if comments else "观望"

# 初始化策略引擎
strategy = PriceActionStrategy()

# ==================== 数据获取 ====================

def fetch_stock_data(symbol: str) -> Optional[pd.DataFrame]:
    """获取股票日线数据"""
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

# ==================== API 路由 ====================

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
