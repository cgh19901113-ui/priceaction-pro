# PriceAction Pro - 数据源说明

## 国内数据源

本项目使用 **akshare** 作为主要数据源，数据来自：
- 同花顺
- 雪球
- 东方财富
- 新浪财经

## 为什么选择 akshare？

### 优势
1. ✅ **数据完整** - A 股/港股历史数据齐全
2. ✅ **免费开源** - 无需 API key，无使用限制
3. ✅ **国内访问** - 不需要代理，速度快
4. ✅ **数据准确** - 与国内主流平台一致
5. ✅ **持续维护** - 活跃开源项目

### 对比其他数据源

| 数据源 | A 股完整性 | 港股完整性 | 成本 | 国内访问 |
|--------|------------|------------|------|----------|
| **akshare** | ✅ 完整 | ✅ 完整 | 免费 | ✅ 快速 |
| yfinance | ⚠️ 部分缺失 | ⚠️ 部分缺失 | 免费 | ⚠️ 慢/被墙 |
| Tushare Pro | ✅ 完整 | ⚠️ 部分 | 积分制 | ✅ 快速 |
| 聚宽 | ✅ 完整 | ❌ 不支持 | 免费 (有限制) | ✅ 快速 |

## 数据覆盖

### A 股
- 全部 A 股 (600/000/002/300 开头)
- 历史数据：上市至今
- 复权数据：前复权/后复权/不复权

### 港股
- 全部港股 (.HK 结尾)
- 历史数据：2000 年至今
- 实时数据：延迟 15 分钟

### 指数
- 沪深 300 (000300)
- 上证指数 (000001)
- 深证成指 (399001)
- 恒生指数 (HSI)

## 使用方法

### 获取个股历史数据
```python
import akshare as ak

# A 股
df = ak.stock_zh_a_hist(symbol="sh600519", period="daily", adjust="qfq")

# 港股
df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
```

### 获取指数数据
```python
# 沪深 300
df = ak.stock_zh_index_hist(symbol="sh000300")

# 恒生指数
df = ak.stock_hk_index_daily(symbol="HSI")
```

## 注意事项

1. **网络要求**: 需要能访问同花顺/新浪等国内网站
2. **数据延迟**: 实时数据有 15 分钟延迟
3. **停牌股票**: 停牌期间无数据
4. **新股**: 上市不足 60 天的股票数据不足

## 备用数据源

如果 akshare 不可用，可以切换到：

### 1. Tushare Pro
```python
import tushare as ts

# 需要注册获取 token
ts.set_token('your_token')
df = ts.pro_bar(ts_code='600519.SH')
```

### 2. 聚宽 (JoinQuant)
```python
from jqdatasdk import *

auth('username', 'password')
df = get_price('600519.XSHG', start_date='2025-01-01')
```

---

_文档版本：v1.0_
_更新时间：2026-04-03_
