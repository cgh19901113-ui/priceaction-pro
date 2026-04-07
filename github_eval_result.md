# GitHub 仓库评估结果

**执行时间**: 2026-04-03

---

## ✅ 成功评估的仓库 (4 个)

| 排名 | 仓库 | 分数 | 评级 | 生命周期 |
|------|------|------|------|----------|
| 1 | wasp-lang/open-saas | 69.3 | Average | Active Development |
| 2 | TryGhost/Ghost | 64.5 | Average | Active Development |
| 3 | nextjs/saas-starter | 43.7 | Weak | Mature/Stable |
| 4 | easychen/one-person-businesses-methodology | 39.1 | Weak | Active Development |

---

## ❌ 失败的仓库 (14 个)

**原因**: GitHub API 限流 (未认证)

- FujiwaraChoki/MoneyPrinterV2
- vnpy/vnpy
- microsoft/qlib
- freqtrade/freqtrade
- nautechsystems/nautilus_trader
- ccxt/ccxt
- harry0703/MoneyPrinterTurbo
- linyqh/NarratoAI
- Huanshere/VideoLingo
- virattt/ai-hedge-fund
- virattt/dexter
- ranaroussi/yfinance
- mrjbq7/ta-lib
- twopirllc/pandas-ta

---

## 📊 分析结论

### Top 1: open-saas (69.3 分)
- **优点**: 活跃开发中，工程质量较好
- **适合**: SaaS 快速启动参考

### Top 2: Ghost (64.5 分)
- **优点**: 成熟项目，工程质量稳定
- **适合**: 内容订阅模式参考

### 低分原因
- easychen/one-person-businesses-methodology: 文档型项目，无代码
- nextjs/saas-starter: 维护频率低

---

## ⚠️ 限制

1. **API 限流**: 未认证 GitHub API 每小时 60 次请求
2. **简化评分**: 未使用 xreach 获取 Twitter 数据
3. **样本不足**: 18 个只成功了 4 个

---

## 🔧 改进建议

1. **配置 GitHub Token**: 提升到每小时 5000 次
2. **完整实现**: 使用原 github-quality skill
3. **添加 PriceAction Pro**: 评估我们自己的项目

---

_更新时间：2026-04-03_
