"""
价格行为策略引擎 - 裸 K 量化核心
买在起涨点：早、强、活、有钱

策略来源：秋生 Trader (@Hoyooyoo)
GitHub: @Hoyooyoo
适用：A 股/港股短线、波段，抓热点早期起涨点
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional, List
import akshare as ak  # 国内数据源, List


class PriceActionStrategy:
    """
    纯价格行为策略引擎
    
    核心理念:
    - 纯技术面，无基本面/宏观/估值过滤
    - 买在起涨点早期 (1-3 天)
    - 过滤一切趋势后期、弱于大盘、无资金确认的标的
    """
    
    def __init__(self):
        self.BENCHMARK = "000300.ss"  # 沪深 300
        
        # 可配置参数 - 根据回测结果微调
        self.TREND_CONFIRM_CONSECUTIVE_GREEN = 2  # 连续阳线数量
        self.TREND_CONFIRM_VOL_RATIO = 1.2  # 放量倍数 (vs 5 日均量)
        self.MARKET_COMPARE_PERIOD = 10  # 大盘对比周期 (10-20 日)
        self.MAIN_FORCE_PERIOD = 10  # 主力量能计算周期
        self.AMPLITUDE_HIGH_THRESHOLD = 12  # 高振幅阈值 (%)
        self.AMPLITUDE_LOW_THRESHOLD = 8  # 低振幅阈值 (%)
        self.RSI_PERIOD = 14  # RSI 周期
        self.EMA_PERIOD = 20  # EMA 周期
        
        # 趋势持续天数阈值
        self.TREND_DURATION_EARLY = 3  # 早期 (1-3 天) - 优质
        self.TREND_DURATION_MID = 10  # 中期 (4-10 天) - 可接受
        # >10 天视为过期
        
    # ==================== 指标计算 ====================
    
    def calculate_daily_trend(self, df: pd.DataFrame) -> Tuple[str, str]:
        """
        大周期 (D) - 日线整体趋势
        
        逻辑:
        1. 价格是否站上 20/60 日均线
        2. 最近 5-10 根日 K 高点/低点是否持续抬高
        3. 辅助：MACD 金叉或 ADX>25
        
        返回：(信号，颜色)
        """
        if len(df) < 60:
            return ("数据不足", "⚪")
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df.columns else 'close'
        
        current_price = df[close_col].iloc[-1]
        ma20 = df[close_col].rolling(20).mean().iloc[-1]
        ma60 = df[close_col].rolling(60).mean().iloc[-1]
        
        # 均线判断
        above_ma20 = current_price > ma20
        above_ma60 = current_price > ma60
        
        # 高低点抬高判断 (最近 5 天)
        high_col = 'High' if 'High' in df.columns else 'high'
        low_col = 'Low' if 'Low' in df.columns else 'low'
        
        recent_highs = df[high_col].iloc[-10:-5].max()
        recent_lows = df[low_col].iloc[-10:-5].min()
        current_high = df[high_col].iloc[-5:].max()
        current_low = df[low_col].iloc[-5:].min()
        
        structure_up = (current_high > recent_highs) and (current_low > recent_lows)
        
        # MACD 辅助
        macd = self._calculate_macd(df[close_col])
        macd_bullish = macd['macd'].iloc[-1] > macd['signal'].iloc[-1]
        
        # 综合判断
        if above_ma20 and above_ma60 and structure_up:
            return ("看涨", "🟢")
        elif not above_ma20 and not above_ma60:
            return ("看跌", "🔴")
        else:
            return ("震荡", "⚪")
    
    def calculate_trend_duration(self, df: pd.DataFrame) -> Tuple[str, str]:
        """
        趋势持续天数 - 从趋势确认 K 线开始计数
        
        确认信号:
        - 连续 2 根以上阳线
        - 成交量大于 1.2 倍 5 日均量
        - 收盘突破近期前高或均线
        
        返回：(天数描述，颜色)
        """
        if len(df) < 20:
            return ("数据不足", "⚪")
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df.columns else 'close'
        open_col = 'Open' if 'Open' in df.columns else 'open'
        high_col = 'High' if 'High' in df.columns else 'high'
        volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
        
        # 寻找趋势确认起点
        confirm_day = None
        
        for i in range(len(df) - 1, 5, -1):
            # 检查连续阳线
            consecutive_green = 0
            for j in range(i, max(0, i-5), -1):
                if df[close_col].iloc[j] > df[open_col].iloc[j]:
                    consecutive_green += 1
                else:
                    break
            
            if consecutive_green >= 2:
                # 检查放量
                avg_vol_5 = df[volume_col].iloc[max(0, i-5):i].mean()
                if df[volume_col].iloc[i] > 1.2 * avg_vol_5:
                    # 检查突破
                    recent_high = df[high_col].iloc[max(0, i-10):i].max()
                    if df[close_col].iloc[i] > recent_high:
                        confirm_day = i
                        break
        
        if confirm_day is None:
            return ("未确认", "⚪")
        
        # 计算持续天数
        days = len(df) - confirm_day
        
        # 放宽趋势持续阈值：早期 (1-3 天) / 中期 (4-10 天) / 过期 (>10 天)
        if days <= self.TREND_DURATION_EARLY:
            return (f"{days}天", "🟢")  # 优质早期
        elif days <= self.TREND_DURATION_MID:
            return (f"{days}天", "🟠")  # 中期可接受
        else:
            return (f"{days}天 过期", "⚪")  # 过期
    
    def calculate_market_comparison(self, symbol: str, df: pd.DataFrame) -> Tuple[str, str]:
        """
        大盘对比 - 个股 vs 沪深 300 相对强度
        
        使用 akshare 获取沪深 300 数据 (国内数据源，稳定可靠)
        
        逻辑：个股近 10 日累计涨跌幅 - 大盘同期涨跌幅
        """
        try:
            close_col = 'Close' if 'Close' in df.columns else 'close'
            
            # 计算个股近 10 日涨跌幅
            stock_return = (df[close_col].iloc[-1] - df[close_col].iloc[-10]) / df[close_col].iloc[-10] * 100
            
            # 获取沪深 300 数据 (使用 akshare)
            try:
                # akshare 获取沪深 300 历史数据
                benchmark_df = ak.stock_zh_index_hist(symbol="sh000300", period="daily")
                if len(benchmark_df) > 0:
                    bench_close = 'close' if 'close' in benchmark_df.columns else '收盘'
                    benchmark_return = (benchmark_df[bench_close].iloc[-1] - benchmark_df[bench_close].iloc[-10]) / benchmark_df[bench_close].iloc[-10] * 100
                else:
                    benchmark_return = 0
            except Exception as e:
                # 获取失败，用 0 作为基准
                benchmark_return = 0
            
            diff = stock_return - benchmark_return
            
            if diff > 2:
                return (f"强于大盘 +{diff:.1f}%", "🔴")  # 红色突出
            elif diff > 0:
                return (f"强于大盘 +{diff:.1f}%", "🟢")
            else:
                return (f"弱于大盘 {diff:.1f}%", "🟢")
                
        except Exception as e:
            # 极端情况下，用个股动量替代
            close_col = 'Close' if 'Close' in df.columns else 'close'
            momentum = (df[close_col].iloc[-1] - df[close_col].iloc[-20]) / df[close_col].iloc[-20] * 100
            
            if momentum > 5:
                return ("强势上涨", "🔴")
            elif momentum > 0:
                return ("震荡向上", "🟢")
            else:
                return ("弱势下跌", "🟢")
    
    def calculate_main_force_flow(self, df: pd.DataFrame) -> Tuple[str, str]:
        """
        主力量能 (1D) - 聪明钱资金流
        
        自定义资金流 = 涨跌幅×成交量 近 10 日净值
        """
        if len(df) < 10:
            return ("数据不足", "⚪")
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df.columns else 'close'
        volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
        
        # 计算资金流
        returns = df[close_col].pct_change()
        flow = returns * df[volume_col]
        
        net_flow = flow.iloc[-10:].sum()
        recent_3d = flow.iloc[-3:].sum()
        
        if net_flow > 0 and recent_3d > 0:
            return ("资金流入", "🟢")
        elif net_flow < 0:
            return ("资金流出", "🔴")
        else:
            return ("中性", "⚪")
    
    def calculate_10day_amplitude(self, df: pd.DataFrame) -> Tuple[str, str]:
        """
        10 日振幅 - ATR(10)/当前价
        """
        if len(df) < 10:
            return ("数据不足", "⚪")
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df.columns else 'close'
        high_col = 'High' if 'High' in df.columns else 'high'
        low_col = 'Low' if 'Low' in df.columns else 'low'
        
        # 计算 ATR
        high_low = df[high_col] - df[low_col]
        high_close = np.abs(df[high_col] - df[close_col].shift())
        low_close = np.abs(df[low_col] - df[close_col].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(10).mean().iloc[-1]
        
        current_price = df[close_col].iloc[-1]
        amplitude = (atr / current_price) * 100
        
        if amplitude > 12:
            return (f"{amplitude:.1f}% 高弹性", "🟣")
        elif amplitude >= 8:
            return (f"{amplitude:.1f}% 蓄势中", "🟢")
        else:
            return (f"{amplitude:.1f}% 低波动", "⚪")
    
    def calculate_15m_signal(self, df_15m: pd.DataFrame) -> Tuple[str, str]:
        """
        当前信号 - 15 分钟线即时结构
        
        逻辑:
        - 15M K 线高低点是否持续抬高
        - 价格 vs 15M EMA20
        - 15M RSI(14)>50
        """
        if len(df_15m) < 50:
            return ("数据不足", "⚪")
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df_15m.columns else 'close'
        high_col = 'High' if 'High' in df_15m.columns else 'high'
        
        current_price = df_15m[close_col].iloc[-1]
        ema20 = df_15m[close_col].ewm(span=self.EMA_PERIOD).mean().iloc[-1]
        
        # RSI
        rsi = self._calculate_rsi(df_15m[close_col], self.RSI_PERIOD).iloc[-1]
        
        # 高低点判断
        recent_highs = df_15m[high_col].iloc[-20:-10].max()
        current_high = df_15m[high_col].iloc[-10:].max()
        
        structure_up = current_high > recent_highs
        
        # 综合判断
        if structure_up and current_price > ema20 and rsi > 50:
            return ("看涨", "🔵")
        elif current_price < ema20 and rsi < 50:
            return ("看跌", "🔴")
        else:
            return ("中性", "⚪")
    
    # ==================== 辅助函数 ====================
    
    def _calculate_macd(self, series: pd.Series) -> pd.DataFrame:
        """计算 MACD"""
        exp1 = series.ewm(span=12, adjust=False).mean()
        exp2 = series.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return pd.DataFrame({'macd': macd, 'signal': signal})
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """计算 RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    # ==================== 评分系统 ====================
    
    def score_analysis(self, indicators: Dict) -> Dict:
        """
        评分系统
        
        趋势持续：1 天=10 分，2 天=8 分，3 天=5 分，>3 天=0 分
        其他指标各 10 分
        总分≥70 分进入高优先池
        """
        score = 0
        details = {}
        
        # 趋势持续评分 (放宽：1-3 天 10 分，4-10 天 5 分，>10 天 0 分)
        trend_text = indicators.get('趋势持续', '')
        if '1 天' in trend_text:
            score += 10
        elif '2 天' in trend_text:
            score += 10
        elif '3 天' in trend_text:
            score += 10
        elif '4 天' in trend_text or '5 天' in trend_text or '6 天' in trend_text:
            score += 5  # 中期加分
        elif '7 天' in trend_text or '8 天' in trend_text or '9 天' in trend_text or '10 天' in trend_text:
            score += 3  # 中后期少加分
        else:
            score += 0  # 过期
        details['趋势持续'] = score
        
        # 大周期
        if indicators.get('大周期') == '看涨':
            score += 10
        details['大周期'] = 10 if indicators.get('大周期') == '看涨' else 0
        
        # 大盘对比
        if '强于大盘' in indicators.get('大盘对比', ''):
            score += 10
        details['大盘对比'] = 10 if '强于大盘' in indicators.get('大盘对比', '') else 0
        
        # 主力量能
        if indicators.get('主力量能') == '资金流入':
            score += 10
        details['主力量能'] = 10 if indicators.get('主力量能') == '资金流入' else 0
        
        # 10 日振幅
        if '高弹性' in indicators.get('10 日振幅', ''):
            score += 10
        elif '蓄势中' in indicators.get('10 日振幅', ''):
            score += 5
        details['10 日振幅'] = score - sum(details.values()) + 10 if '高弹性' in indicators.get('10 日振幅', '') else 5
        
        # 当前信号
        if indicators.get('当前信号') == '看涨':
            score += 10
        details['当前信号'] = 10 if indicators.get('当前信号') == '看涨' else 0
        
        # 推荐
        recommendation = self._get_recommendation(score, indicators)
        
        return {
            'total_score': score,
            'details': details,
            'recommendation': recommendation
        }
    
    def _get_recommendation(self, score: int, indicators: Dict) -> str:
        """
        决策规则 (v3.1 放宽版)
        
        推荐买入观察池（通过标准）:
        - 大周期 (D) = 看涨（必备）
        - 趋势持续 = 1~10 天（优先 1-3 天早期）
        - 大盘对比 = 强于大盘（加分）
        - 主力量能 = 资金流入（必备）
        - 当前信号 = 看涨或中性
        - 10 日振幅 = 高弹性（加分）
        
        直接过滤:
        - 趋势持续 >10 天 → "过期"
        - 大周期看跌 → Pass
        - 主力量能流出 + 大盘对比弱 → Pass
        """
        # 直接过滤
        if indicators.get('大周期') == '看跌':
            return "❌ Pass - 大周期看跌"
        
        if '过期' in indicators.get('趋势持续', ''):
            return "❌ Pass - 趋势过期 (>10 天)"
        
        if indicators.get('主力量能') == '资金流出' and '弱于' in indicators.get('大盘对比', ''):
            return "❌ Pass - 资金流出 + 弱于大盘"
        
        # 通过标准 (放宽：4-10 天中期也可通过，扣分但不过滤)
        # 大周期看涨 + 主力量能流入 = 至少 20 分
        # 趋势持续 1-3 天 = +10 分 → 30 分
        # 其他指标各 10 分
        
        if (indicators.get('大周期') == '看涨' and 
            indicators.get('主力量能') == '资金流入'):
            # 核心条件满足，检查是否有严重负面
            if '过期' not in indicators.get('趋势持续', ''):
                return "✅ 观察池 - 有点东西"
        
        if score >= 40:
            return "⚠️ 观望 - 等回踩"
        
        return "⚪ 观望"
    
    # ==================== 验证模式 ====================
    
    def validate_with_history(self, symbol: str, df_daily: pd.DataFrame, 
                               recommend_date: str, hold_days: int = 3) -> Dict:
        """
        历史验证模式 - 用于回测原博推荐过的股票
        
        输入:
        - symbol: 股票代码
        - df_daily: 历史数据 (需包含推荐日期前后)
        - recommend_date: 原博推荐日期 (YYYY-MM-DD)
        - hold_days: 持有天数 (默认 3 天)
        
        输出:
        - 推荐时的指标
        - 持有期收益
        - 是否达标
        """
        # 找到推荐日期索引
        try:
            rec_idx = df_daily.index.get_loc(recommend_date)
        except KeyError:
            return {"error": f"未找到日期 {recommend_date}"}
        
        # 兼容大小写列名
        close_col = 'Close' if 'Close' in df_daily.columns else 'close'
        
        # 截取推荐日之前的数据
        df_before = df_daily.iloc[:rec_idx+1]
        
        if len(df_before) < 60:
            return {"error": "数据不足"}
        
        # 执行分析
        analysis = self.analyze(symbol, df_before)
        
        # 计算持有期收益
        if rec_idx + hold_days < len(df_daily):
            buy_price = df_daily[close_col].iloc[rec_idx]
            sell_price = df_daily[close_col].iloc[rec_idx + hold_days]
            return_pct = (sell_price - buy_price) / buy_price * 100
        else:
            return_pct = None
        
        return {
            'symbol': symbol,
            'recommend_date': recommend_date,
            'analysis': analysis,
            'hold_days': hold_days,
            'return_pct': return_pct,
            'success': return_pct > 5 if return_pct else None  # 5% 达标
        }
    
    def batch_validate(self, recommendations: List[Dict], 
                       data_cache: Dict[str, pd.DataFrame]) -> Dict:
        """
        批量验证 - 统计原博推荐股票的准确率
        
        输入:
        - recommendations: 推荐列表 [{symbol, date}, ...]
        - data_cache: 股票数据缓存 {symbol: df}
        
        输出:
        - 总数量
        - 通过率 (符合观察池标准的比例)
        - 准确率 (通过后 3 天涨幅>5% 的比例)
        - 假信号率 (通过后下跌的比例)
        """
        results = []
        
        for rec in recommendations:
            symbol = rec['symbol']
            date = rec['date']
            
            if symbol not in data_cache:
                continue
            
            result = self.validate_with_history(symbol, data_cache[symbol], date)
            if 'error' not in result:
                results.append(result)
        
        if not results:
            return {"error": "无有效数据"}
        
        # 统计
        total = len(results)
        passed = sum(1 for r in results if '✅' in r['analysis'].get('recommendation', ''))
        success = sum(1 for r in results if r.get('success') == True)
        failed = sum(1 for r in results if r.get('success') == False)
        
        return {
            'total': total,
            'pass_rate': passed / total * 100,
            'accuracy': success / passed * 100 if passed > 0 else 0,
            'false_rate': failed / passed * 100 if passed > 0 else 0,
            'details': results
        }
    
    # ==================== 完整分析流程 ====================
    
    def analyze(self, symbol: str, df_daily: pd.DataFrame, df_15m: pd.DataFrame = None) -> Dict:
        """
        完整分析流程
        
        输入：股票代码、日线数据、15 分钟数据
        输出：完整分析报告
        """
        # 计算所有指标
        indicators = {}
        
        # 大周期
        trend, trend_color = self.calculate_daily_trend(df_daily)
        indicators['大周期'] = trend
        indicators['大周期_颜色'] = trend_color
        
        # 趋势持续
        duration, duration_color = self.calculate_trend_duration(df_daily)
        indicators['趋势持续'] = duration
        indicators['趋势持续_颜色'] = duration_color
        
        # 大盘对比
        comparison, comp_color = self.calculate_market_comparison(symbol, df_daily)
        indicators['大盘对比'] = comparison
        indicators['大盘对比_颜色'] = comp_color
        
        # 主力量能
        flow, flow_color = self.calculate_main_force_flow(df_daily)
        indicators['主力量能'] = flow
        indicators['主力量能_颜色'] = flow_color
        
        # 10 日振幅
        amplitude, amp_color = self.calculate_10day_amplitude(df_daily)
        indicators['10 日振幅'] = amplitude
        indicators['10 日振幅_颜色'] = amp_color
        
        # 当前信号
        if df_15m is not None:
            signal, signal_color = self.calculate_15m_signal(df_15m)
        else:
            signal, signal_color = "数据不足", "⚪"
        indicators['当前信号'] = signal
        indicators['当前信号_颜色'] = signal_color
        
        # 评分
        score_result = self.score_analysis(indicators)
        
        # 生成报告
        report = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators,
            'score': score_result['total_score'],
            'recommendation': score_result['recommendation'],
            'comment': self._generate_comment(indicators, score_result)
        }
        
        return report
    
    def _generate_comment(self, indicators: Dict, score_result: Dict) -> str:
        """生成裸 K 简评"""
        comments = []
        
        if indicators.get('大周期') == '看涨':
            comments.append("日线趋势向上")
        
        if '1 天' in indicators.get('趋势持续', '') or '2 天' in indicators.get('趋势持续', ''):
            comments.append("早期起涨")
        
        if indicators.get('主力量能') == '资金流入':
            comments.append("资金流入")
        
        if '强于大盘' in indicators.get('大盘对比', ''):
            comments.append("强于大盘")
        
        if '高弹性' in indicators.get('10 日振幅', ''):
            comments.append("高弹性")
        
        if comments:
            return "，".join(comments[:3]) + "，有点东西"
        else:
            return "观望"


# 使用示例
if __name__ == "__main__":
    strategy = PriceActionStrategy()
    # 实际使用时传入真实数据
    print("价格行为策略引擎已加载")
