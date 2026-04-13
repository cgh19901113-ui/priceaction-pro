# Twitter Distiller - 推特博主数据蒸馏器

## 快速开始

### 方案 A: 浏览器自动收集（推荐，可收集 1000+ 条）

```bash
# 1. 安装 Playwright（首次使用）
pip install playwright
playwright install chromium

# 2. 收集单个博主（会打开浏览器，需手动登录 Twitter）
cd D:\Projects\price-action-saas
python skills\twitter-distill\crawler_browser.py --user Hoyooyoo --limit 1000

# 3. 收集所有博主（10 位，目标 1000 条/人）
python skills\twitter-distill\crawler_browser.py --all --limit 1000

# 4. 导出为回测格式
python skills\twitter-distill\crawler_browser.py --export

# 5. 运行回测
python strategy\backtest_twitter.py
```

### 方案 B: 手动导入数据

```bash
# 创建 Excel 模板
python skills\twitter-distill\import_data.py --template

# 填写后导入
python skills\twitter-distill\import_data.py --input data.xlsx
```

## 输出文件

- `data/twitter/{username}.jsonl` - 原始推文数据（JSONL 格式）
- `strategy/twitter_recommendations.json` - 导出的荐股记录（用于回测）
- `strategy/backtest_twitter_result.csv` - 回测结果

## 数据格式

### 原始推文 (JSONL)
```json
{
  "tweet_id": "1234567890",
  "timestamp": "2025-11-12T10:30:00",
  "username": "Hoyooyoo",
  "content": "中国中免 601888，大周期多头向上...",
  "likes": 1234,
  "retweets": 567,
  "symbols": ["601888.ss"],
  "sentiment": "bullish",
  "analysis_type": "price_action"
}
```

### 荐股记录 (JSON)
```json
{
  "symbol": "601888.ss",
  "date": "2025-11-12",
  "blogger": "@Hoyooyoo",
  "note": "大周期多头向上，有很大向上空间",
  "sentiment": "bullish",
  "tweet_id": "1234567890"
}
```

## 目标博主

| 账号 | 风格 | 优先级 |
|------|------|--------|
| @Hoyooyoo | 价格行为 + 裸 K | P0 |
| @KillaXBT | PA+YTC | P0 |
| @Will_Yang_ | 威科夫 + 量价 | P1 |
| @yekoikoi | 显著 K 线 | P1 |
| @0xtongcan | 裸 K+ 订单流 | P1 |
| @WallStreet0Name | 裸 K+ 缠论 | P1 |
| @CycleStudies | 趋势线 + 支撑压力 | P2 |
| @Mingarithm | 形态 + 波浪 | P2 |
| @Jingxin147741 | 裸 K 启蒙 | P2 |
| @PAVLeader | 聪明钱概念 | P3 |

## 注意事项

1. **速率限制**: 每个博主请求间隔 5 秒，避免被 Twitter 封禁
2. **增量收集**: 自动去重，只保存新推文
3. **snscrape 限制**: 只能收集公开推文，私密账号无法收集
4. **数据合规**: 仅用于个人研究，不要公开分发

## 故障排除

### snscrape 安装失败
```bash
# 尝试从 git 安装
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```

### 收集速度慢
- 减少 `--limit` 参数
- 使用 `--since` 指定更近的日期
- 检查网络连接

### 找不到股票
- 检查推文是否包含股票代码/名称
- 可在 `collect.py` 的 `name_to_symbol` 字典中添加更多映射
