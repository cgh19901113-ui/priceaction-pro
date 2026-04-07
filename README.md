# AI 个股分析 SaaS - 价格行为策略

**项目名**: PriceAction Pro / 起涨点捕捉器

**Slogan**: 买在起涨点 · 早强活有钱

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Next.js)                        │
│  首页 + 输入框 + 结果表格 + 支付弹窗                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   后端 (FastAPI)                         │
│  API 路由 + 策略引擎 + 用户管理 + 支付回调                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   yfinance   │  │   SQLite     │  │  NowPayments │
│   数据源      │  │   数据库      │  │   支付网关    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 核心策略引擎

### 指标计算模块

```python
# strategy/indicators.py

def calculate_trend_duration(df: pd.DataFrame) -> int:
    """计算趋势持续天数"""
    # 确认信号：连续 2 阳 + 放量 1.2 倍 + 突破前高
    # 从确认 K 线计数到今天
    
def calculate_market_comparison(symbol: str, benchmark: str = "000300.ss") -> float:
    """大盘对比：个股 vs 沪深 300"""
    # 近 10-20 日累计涨跌幅差值
    
def calculate_main_force_flow(df: pd.DataFrame) -> float:
    """主力量能：涨跌幅×成交量 近 10 日净值"""
    
def calculate_10day_amplitude(df: pd.DataFrame) -> float:
    """10 日振幅：ATR(10)/价格"""
    
def calculate_15m_signal(df_15m: pd.DataFrame) -> str:
    """15 分钟线即时结构"""
    # 15M 高低点抬高 + EMA20 + RSI>50
```

### 评分系统

```python
# strategy/scorer.py

def score_stock(indicators: dict) -> dict:
    """
    评分规则:
    - 趋势持续：1 天=10 分，2 天=8 分，3 天=5 分，>3 天=0 分
    - 其他指标各 10 分
    - 总分≥70 分进入高优先池
    """
    
def get_recommendation(score: int, indicators: dict) -> str:
    """
    推荐买入观察池（通过标准）:
    - 大周期 (D) = 看涨（必备）
    - 趋势持续 = 1~3 天（优先 1-2 天）
    - 大盘对比 = 强于大盘（加分）
    - 主力量能 = 资金流入（必备）
    - 当前信号 = 看涨或中性
    - 10 日振幅 = 高弹性（加分）
    """
```

---

## API 设计

```python
# api/routes.py

POST /api/analyze
- 输入：{ "symbol": "600519.ss", "credits": 1 }
- 输出：{ "analysis": {...}, "remaining_credits": 4 }

GET /api/daily-free/{ip}
- 输入：IP 地址
- 输出：{ "available": true/false, "reset_at": "2026-04-04 00:00" }

POST /api/payment/create
- 输入：{ "amount": 1, "currency": "USDT" }
- 输出：{ "payment_url": "...", "order_id": "..." }

POST /api/payment/callback
- NowPayments 回调
- 自动充值积分
```

---

## 数据库设计

```sql
-- users 表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id TEXT UNIQUE,
    credits INTEGER DEFAULT 0,
    last_free_analysis DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- analyses 表
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    symbol TEXT,
    analysis_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- payments 表
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    credits_added INTEGER,
    status TEXT,
    nowpayments_id TEXT,
    created_at DATETIME
);
```

---

## 输出格式（固定表格）

```markdown
| 指标 | 信号 | 颜色 |
|------|------|------|
| 大周期 (D) | 看涨 | 🟢 |
| 趋势持续 | 2 天 | 🟢 |
| 大盘对比 | 强于大盘 +3.2% | 🔴 |
| 主力量能 (1D) | 资金流入 | 🟢 |
| 10 日振幅 | 14.5% 高弹性 | 🟣 |
| 当前信号 | 看涨 | 🔵 |

**裸 K 简评**: 日线突破前高，15 分钟线连续抬高，有点东西。
**建议**: 观察池，紧止损 ATR×1.5
```

---

## 部署清单

- [ ] 域名购买 (priceaction.pro / qizhangdian.com)
- [ ] Vercel 部署前端
- [ ] Railway 部署后端
- [ ] NowPayments 注册
- [ ] Telegram Bot 创建
- [ ] 测试环境验证

---

## 推广渠道

1. **Telegram 群组**
   - @claudecode_cn
   - @ChineseDevelopers
   - @Pythonzh
   - @China_irl

2. **Twitter/X**
   - 每日免费分析 1 只股票
   - 带网站链接

3. **产品猎**
   - 发布产品
   - 获取早期用户

---

_项目启动时间：2026-04-03 16:45_
