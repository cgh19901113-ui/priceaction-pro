# PriceAction Pro - A 股起涨点雷达

> **提前 3 天，告诉你哪只 A 股要涨**

**策略来源**: 秋生 Trader (@Hoyooyoo)  
**策略类型**: 纯价格行为 (Price Action) + 裸 K 量化  
**适用市场**: **仅限国内 A 股/港股** ❌ 不面向美股/币圈/期货

---

## 🚀 快速启动

### 环境要求
- Python 3.10+
- 依赖见 `requirements.txt`

### 安装依赖

```bash
cd D:/Projects/price-action-saas
pip install -r requirements.txt
```

### 启动后端

```bash
cd backend
python main.py

# 访问 http://localhost:8000
```

### 打开前端

直接双击 `frontend/index.html` 或访问后端首页

---

## 💰 商业模式

**包月订阅制** (乔布斯评估后优化)

| 版本 | 价格 | 权益 |
|------|------|------|
| **免费版** | ¥0 | 每天 1 次分析，仅显示"买/不买" |
| **Pro 版** | ¥99/月 | 无限次 + 完整数据 + 实时推送 |

**涨价路径**:
- 100 个 Pro 用户 → ¥99
- 500 个 Pro 用户 → ¥149
- 1000 个 Pro 用户 → ¥199

---

## 📊 核心功能

### 简化版主界面 (乔布斯原则)

**只显示 2 个核心指标**:
1. **起涨概率** (0-100 分)
2. **预期涨幅** (3 日预期%)

**6 大详细指标** 收起到"查看详情"：
- 大周期 (D)
- 趋势持续
- 大盘对比
- 主力量能
- 10 日振幅
- 当前信号

### 数据记录系统

**每次分析自动记录**:
- 用户 ID + 股票代码
- 评分/概率/预期涨幅
- 6 大指标详情
- 分析时间

**月度统计报告**:
- 总分析次数
- 观察池信号数量
- 策略准确率 (需回填实际收益)
- Pro 用户数
- 月收入

---

## 📁 项目结构

```
D:\Projects\price-action-saas\
├── backend/
│   ├── main.py          # FastAPI 后端 (订阅制 + 数据记录)
│   └── priceaction.db   # SQLite 数据库
├── frontend/
│   └── index.html       # 简化版主界面
├── strategy/
│   ├── engine.py        # 策略引擎 (6 大指标)
│   └── backtest_*.py    # 回测脚本
├── PROJECT.md           # 本文档
└── requirements.txt     # Python 依赖
```

---

## 🔧 API 文档

### POST /api/analyze
分析股票

```json
// Request
{
  "symbol": "600519.ss",
  "client_ip": "1.2.3.4"
}

// Response
{
  "success": true,
  "remaining_credits": 999,
  "is_pro": true,
  "analysis": {
    "symbol": "600519.ss",
    "score": 85,
    "probability": 85,
    "expectation": 2.5,
    "signal": "观察池 - 有点东西",
    "signal_type": "success",
    "indicators": {...},
    "comment": "日线趋势向上，早期起涨，资金流入"
  }
}
```

### GET /api/credits
获取剩余额度

### POST /api/upgrade
升级到 Pro 版

```json
{
  "amount": 99.0,
  "currency": "CNY",
  "duration_days": 30
}
```

### GET /api/stats/monthly
获取月度统计报告

### GET /api/stats/accuracy
获取策略准确率统计

---

## 📈 数据记录与准确率验证

### 核心数据表

**analyses 表**:
```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    symbol TEXT,
    score INTEGER,
    probability INTEGER,
    expectation REAL,
    signal TEXT,
    indicators TEXT,
    actual_3d_return REAL,  -- 3 日后实际收益 (需回填)
    is_profitable INTEGER,  -- 是否赚钱
    created_at DATETIME,
    reviewed_at DATETIME
);
```

### 月度报告模板

```markdown
## 【2026 年 4 月】策略准确率报告

- 总分析数：1,234 次
- 观察池信号：312 次 (25.3%)
- 观察池 3 日平均收益：+4.2%
- 观察池赚钱比例：68%
- Pro 用户数：47 人
- 月收入：¥4,653

**策略有效性**: ✅ 有效 (赚钱率>60%)
```

### 回填实际收益

```bash
# 调用管理员接口回填 3 日前记录的实际收益
POST /api/admin/review-returns
```

**注意**: 需要接入行情数据 API 获取真实 3 日后收益

---

## 🎯 乔布斯评估优化点

### ✅ 已实施

| 优化 | 说明 |
|------|------|
| **指标简化** | 主界面只显示 2 个核心指标 |
| **详情收起** | 6 大指标隐藏到"查看详情" |
| **包月定价** | ¥99/月，替代 1 USDT 5 次 |
| **数据记录** | 每次分析记录到数据库 |
| **月度报告** | 自动生成策略准确率统计 |

### 🔄 待实施

| 优化 | 优先级 | 说明 |
|------|--------|------|
| **实时推送** | P1 | 信号出现时主动推送给用户 |
| **Telegram 登录** | P1 | 替代 IP 限制，支持多设备 |
| **预测准确率公开** | P1 | 每月发布报告建立信任 |
| **护城河思考** | P0 | 什么是东方财富无法复制的？ |

---

## ⚠️ 风险提示

- 本工具仅供学习参考，**不构成投资建议**
- 高振幅需紧止损 (ATR×1.5-2 倍)
- 系统性熊市或大盘转弱时，信号失效率高
- **仅适用于 A 股/港股，不适用于美股/币圈**

---

## 📞 联系方式

- Telegram: @aresdawn
- 升级 Pro: 联系上方 Telegram

---

_项目启动：2026-04-03_  
_版本：v3.2 (乔布斯评估优化版)_  
_最后更新：2026-04-05_
