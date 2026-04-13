# Twitter 数据收集 - 使用指南

## 🎯 目标
收集 10 位 Twitter 技术分析博主的历史推文，每条至少 1000 条，用于 PriceAction Pro 策略回测。

## 📋 目标博主列表

| 优先级 | 博主 | 风格 | 目标数量 |
|--------|------|------|----------|
| P0 | @Hoyooyoo | 价格行为 + 裸 K | 1000+ |
| P0 | @KillaXBT | PA+YTC 流动性 | 1000+ |
| P1 | @Will_Yang_ | 威科夫 + 量价 | 1000+ |
| P1 | @yekoikoi | 显著 K 线 | 1000+ |
| P1 | @0xtongcan | 裸 K+ 订单流 | 1000+ |
| P1 | @WallStreet0Name | 裸 K+ 缠论 | 1000+ |
| P2 | @CycleStudies | 趋势线 + 支撑压力 | 500+ |
| P2 | @Mingarithm | 形态 + 波浪 | 500+ |
| P2 | @Jingxin147741 | 裸 K 启蒙 | 500+ |
| P3 | @PAVLeader | 聪明钱概念 | 500+ |

**总计目标：8500+ 条含股票的推文**

---

## 🚀 使用方法

### 方法 1: 交互式爬虫（推荐）

**优点**: 可以手动控制滚动，确保加载足够的历史推文

```bash
cd D:\Projects\price-action-saas

# 启动爬虫（会打开浏览器）
python skills\twitter-distill\crawler_interactive.py --user Hoyooyoo
```

**操作步骤**:
1. 运行命令，浏览器自动打开
2. 如果未登录，手动登录 Twitter
3. 在博主页面**手动向下滚动**，加载历史推文
   - 滚动越多次，加载的推文越多
   - 建议滚动 50-100 次，加载 1-2 年的数据
4. 按 **Ctrl+C** 停止，数据自动保存

**收集下一个博主**:
```bash
python skills\twitter-distill\crawler_interactive.py --user KillaXBT
```

---

### 方法 2: 批量导出

收集完所有博主后，导出为回测格式：

```bash
# 导出所有数据
python skills\twitter-distill\crawler_browser.py --export

# 查看统计数据
# 导出时会自动显示每位博主的推文数量
```

---

### 方法 3: 运行回测

```bash
cd D:\Projects\price-action-saas\strategy
python backtest_twitter.py
```

---

## 📊 数据格式

### 原始数据 (JSONL)
`data/twitter/{username}.jsonl`
```json
{
  "tweet_id": "1234567890",
  "timestamp": "2025-11-12",
  "username": "Hoyooyoo",
  "content": "中国中免 601888，大周期多头向上",
  "symbols": ["601888.ss"],
  "sentiment": "bullish"
}
```

### 回测数据 (JSON)
`strategy/twitter_recommendations.json`
```json
{
  "symbol": "601888.ss",
  "date": "2025-11-12",
  "blogger": "@Hoyooyoo",
  "note": "大周期多头向上",
  "sentiment": "bullish"
}
```

---

## ⚡ 快速收集技巧

### 多标签页并行
1. 运行第一个博主：`python crawler_interactive.py --user Hoyooyoo`
2. 在新标签页打开其他博主页面
3. 在每个标签页手动滚动加载
4. 切换回第一个标签页按 Ctrl+C 保存

### 使用宏/脚本自动滚动
在浏览器控制台运行：
```javascript
// 自动滚动 100 次
let count = 0;
const interval = setInterval(() => {
  window.scrollTo(0, document.body.scrollHeight);
  count++;
  console.log(`Scroll ${count}/100`);
  if (count >= 100) clearInterval(interval);
}, 2000);
```

---

## 📈 预期数据量

| 博主 | 推文频率 | 预计含股票推文 | 收集时间 |
|------|----------|----------------|----------|
| @Hoyooyoo | 每天 2-3 条 | 800-1200 条 | 10 分钟 |
| @KillaXBT | 每天 5-10 条 | 1500-2000 条 | 15 分钟 |
| 其他博主 | 每天 1-3 条 | 500-800 条 | 5-10 分钟 |

**总预计时间**: 1-2 小时收集全部 10 位博主

---

## 🔧 故障排除

### 问题 1: 浏览器打不开
```bash
# 重新安装 Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### 问题 2: 找不到推文元素
- 确保已登录 Twitter
- 检查 URL 是否正确（应该是 `x.com/{username}/with_replies`）
- 手动刷新页面

### 问题 3: 收集到的数据太少
- 多滚动几次，加载更多内容
- 检查博主是否有足够的历史推文
- 有些博主可能不常发股票相关内容

### 问题 4: 港股/美股数据获取失败
回测时 Yahoo Finance 可能无法获取港股/美股数据，这是正常的。可以：
1. 使用 A 股 ETF 代替
2. 使用其他数据源（如 Tushare）

---

## 📝 进度追踪

创建文件 `data/twitter/progress.txt` 记录进度：

```
[2026-04-05] @Hoyooyoo: 0/1000
[2026-04-05] @KillaXBT: 0/1000
[2026-04-05] @Will_Yang_: 0/1000
...
```

---

## 🎯 下一步

1. **收集数据** (1-2 小时)
   - 按顺序收集 10 位博主
   - 每位至少 500 条含股票的推文

2. **导出回测** (1 分钟)
   ```bash
   python skills\twitter-distill\crawler_browser.py --export
   ```

3. **运行回测** (5-10 分钟)
   ```bash
   python strategy\backtest_twitter.py
   ```

4. **分析结果**
   - 查看每位博主的准确率
   - 识别高质量的博主
   - 优化策略参数

---

**大海，浏览器已启动，开始收集吧！** 🚀
