# Twitter 博主数据蒸馏技能

## 功能
自动化收集 Twitter 纯技术分析博主的历史推文，提取股票分析/推荐，结构化存储用于策略回测。

## 目标博主列表

### 核心博主（纯技术/裸 K/价格行为）
| 账号 | 风格 | 语言 | 优先级 |
|------|------|------|--------|
| @Hoyooyoo | 价格行为 + 裸 K，CFA 背景 | 中文 | P0 |
| @KillaXBT | PA+YTC，流动性猎杀 | 英文/中文 | P0 |
| @Will_Yang_ | 量价趋势 + 威科夫 | 中文 | P1 |
| @yekoikoi | 显著 K 线 + 量价 | 中文 | P1 |
| @0xtongcan | 裸 K 修行 + 订单流 | 中文 | P1 |
| @WallStreet0Name | 裸 K+ 缠论 + 威科夫 | 中文 | P1 |
| @CycleStudies | 趋势线 + 支撑压力 | 中文 | P2 |
| @Mingarithm | 形态 + 波浪 + 流动性 | 英文 | P2 |
| @Jingxin147741 | 裸 K 启蒙 | 中文 | P2 |
| @PAVLeader | 聪明钱概念 | 英文 | P3 |

## 数据收集方式

### 方案 A: Nitter API（推荐，无需认证）
```bash
# 使用 nitter 实例爬取
https://nitter.net/{username}/with_replies
```

### 方案 B: Twitter API v2（需要开发者账号）
```python
import tweepy
client = tweepy.Client(bearer_token=BEARER_TOKEN)
tweets = client.get_users_tweets(id=user_id, max_results=100)
```

### 方案 C: snscrape 库（无需 API）
```python
import snscrape.modules.twitter as sntwitter
tweets = sntwitter.TwitterSearchScraper('from:username').get_items()
```

## 输出格式

```json
{
  "blogger": "@Hoyooyoo",
  "tweet_id": "1234567890",
  "timestamp": "2025-11-12T10:30:00Z",
  "content": "中国中免 601888，大周期多头向上，有很大向上空间",
  "symbols": ["601888.ss"],
  "sentiment": "bullish",
  "target_price": null,
  "stop_loss": null,
  "timeframe": "daily",
  "analysis_type": "price_action",
  "tags": ["大周期", "多头"]
}
```

## 使用方式

```bash
# 收集单个博主
python skills/twitter-distill/collect.py --user Hoyooyoo --limit 500

# 收集所有博主
python skills/twitter-distill/collect.py --all

# 导出为回测格式
python skills/twitter-distill/export.py --format backtest
```

## 数据存储

- 原始推文：`data/twitter/{username}.jsonl`
- 结构化数据：`data/analysis/{symbol}_{date}.json`
- 回测结果：`strategy/backtest_twitter_result.csv`

## 注意事项

1. **速率限制**: 每个博主请求间隔 5-10 秒
2. **去重**: 基于 tweet_id 去重
3. **增量更新**: 记录最后收集的 tweet_id
4. **合规**: 仅用于个人研究，不公开分发数据
