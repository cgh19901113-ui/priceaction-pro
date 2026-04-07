# PriceAction Pro - 起涨点捕捉器

**策略来源**: 秋生 Trader (@Hoyooyoo)
**策略类型**: 纯价格行为 (Price Action) + 裸 K 量化
**适用市场**: **仅限国内 A 股/港股** ❌ 不面向美股/币圈/期货

**Slogan**: 买在起涨点 · 早强活有钱

---

## ⚠️ 重要说明

**本工具仅适用于**:
- ✅ A 股 (600/000/002/300 开头)
- ✅ 港股 (.HK 结尾)

**不支持**:
- ❌ 美股
- ❌ 加密货币
- ❌ 商品期货
- ❌ 外汇

**策略基于**: 秋生 Trader(@Hoyooyoo) 的纯技术面价格行为理论，不看基本面/财务数据。

---

## 🚀 快速启动

### 环境要求
- Python 3.10+
- Node.js 18+ (可选，仅前端开发)

### 安装依赖

```bash
cd C:/Users/Administrator/.openclaw/workspace/projects/price-action-saas

# 安装 Python 依赖
pip install fastapi uvicorn yfinance pandas numpy python-multipart akshare

# 启动后端
cd backend
python main.py

# 后端运行在 http://localhost:8000
```

### 前端

直接打开 `frontend/index.html` 即可使用

或启动本地服务器：

```bash
cd frontend
python -m http.server 3000

# 访问 http://localhost:3000
```

---

## 📊 策略说明

### 核心理念
- **纯价格行为 (Price Action)** + **裸 K 量化**
- 买在起涨点早期 (1-3 天)
- 过滤一切趋势后期、弱于大盘、无资金确认的标的

### 6 大指标

| 指标 | 逻辑 | 信号 |
|------|------|------|
| 大周期 (D) | 20/60 日均线 + 高低点结构 + MACD | 🟢看涨/🔴看跌/⚪震荡 |
| 趋势持续 | 确认 K 线计数 (连续 2 阳 + 放量 + 突破) | 🟢1-3 天/🟠4-10 天/⚪>10 天过期 |
| 大盘对比 | 个股 vs 沪深 300 相对强度 | 🔴强于/🟢弱于 |
| 主力量能 | 涨跌幅×成交量 近 10 日净值 | 🟢流入/🔴流出 |
| 10 日振幅 | ATR(10)/价格 | 🟣>12%/🟢8-12%/⚪<8% |
| 当前信号 | 15M 结构 + EMA20 + RSI | 🔵看涨/🔴看跌/⚪中性 |

### 评分系统
- 趋势持续：1-3 天=10 分，4-10 天=5 分，>10 天=0 分
- 其他指标各 10 分
- **≥60 分** 进入观察池

### 过滤规则
❌ 直接 Pass:
- 趋势持续 >10 天 (过期)
- 大周期看跌
- 主力量能流出 + 大盘对比弱

---

## 💰 商业模式

```
免费：每天 1 次 (IP 限制)
付费：1 USDT = 5 次分析
```

### 支付集成
- NowPayments (支持 USDT，个人可用)
- 自动充值积分

### 收入预测
| 日活 | 转化率 | 月收入 |
|------|--------|--------|
| 100 | 5% | $150 |
| 500 | 5% | $750 |
| 1000 | 5% | $1,500 |

---

## 📁 项目结构

```
price-action-saas/
├── backend/
│   └── main.py          # FastAPI 后端
├── strategy/
│   └── engine.py        # 策略引擎
├── frontend/
│   └── index.html       # 单页应用
├── PROJECT.md
└── requirements.txt
```

---

## 🔧 API 文档

### POST /api/analyze
分析股票

```json
// Request
{
  "symbol": "600519.ss"
}

// Response
{
  "success": true,
  "remaining_credits": 4,
  "analysis": {
    "symbol": "600519.ss",
    "score": 85,
    "indicators": {
      "大周期": "看涨",
      "大周期_颜色": "🟢",
      "趋势持续": "2 天",
      "趋势持续_颜色": "🟢",
      ...
    },
    "recommendation": "✅ 观察池 - 有点东西",
    "comment": "日线趋势向上，早期起涨，资金流入，有点东西"
  }
}
```

### GET /api/daily-free/{ip}
检查每日免费额度

### POST /api/payment/create
创建支付订单

---

## 🌐 部署

### 前端 (Vercel)
```bash
# 安装 Vercel CLI
npm i -g vercel

cd frontend
vercel --prod
```

### 后端 (Railway)
1. 创建 Railway 项目
2. 连接 GitHub 仓库
3. 设置环境变量
4. 自动部署

### 域名
- 前端：priceaction.pro (示例)
- 后端：api.priceaction.pro

---

## 📈 推广渠道

1. **Telegram 群组**
   - @claudecode_cn
   - @ChineseDevelopers
   - @Pythonzh
   - @China_irl

2. **Twitter/X**
   - 每日免费分析 1 只股票
   - 带网站链接

3. **产品猎**
   - 发布产品获取早期用户

---

## ⚠️ 风险提示

- 本工具仅供学习参考
- 不构成投资建议
- 高振幅需紧止损 (ATR×1.5-2 倍)
- 系统性熊市或大盘转弱时，信号失效率高
- **仅适用于 A 股/港股，不适用于美股/币圈**

---

## 📝 待办事项

- [ ] 集成 NowPayments 支付
- [ ] Telegram OAuth 登录
- [ ] 历史回测功能 (1000+ A 股)
- [ ] 用户仪表盘
- [ ] 批量分析功能
- [ ] 导出报告 PDF

---

_项目启动：2026-04-03_
_版本：v3.1 (国内 A 股专用)_
