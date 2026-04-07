# 国内数据源方案

## 问题

**akshare** 需要访问东方财富/同花顺 API，可能被网络阻断。

## 解决方案

### 方案 1: Tushare Pro (推荐)

**优势**:
- ✅ 数据完整准确
- ✅ 国内访问快速
- ✅ 稳定可靠

**成本**:
- 免费注册得 100 积分
- 基础数据够日常使用
- 升级需每日访问或捐赠

**使用方法**:
```bash
# 注册 https://tushare.pro
# 获取 token

pip install tushare
```

```python
import tushare as ts

ts.set_token('your_token')

# 获取个股数据
df = ts.pro_bar(ts_code='600519.SH', start_date='20250101', end_date='20251231')

# 获取大盘指数
df = ts.index_daily(ts_code='000300.SH', start_date='20250101')
```

### 方案 2: 聚宽 (JoinQuant)

**优势**:
- ✅ 免费 (有调用限制)
- ✅ 数据完整
- ✅ 支持回测

**使用方法**:
```bash
pip install jqdatasdk
```

```python
from jqdatasdk import *

auth('username', 'password')

# 获取数据
df = get_price('600519.XSHG', start_date='2025-01-01')
```

### 方案 3: Baostock (无需注册)

**优势**:
- ✅ 完全免费
- ✅ 无需注册
- ✅ 国内访问

**使用方法**:
```bash
pip install baostock
```

```python
import baostock as bs

bs.login()

# 获取数据
rs = bs.query_history_k_data_plus("sh.600519",
    "date,time,open,high,low,close,volume",
    start_date='2025-01-01')

df = rs.to_dataframe()

bs.logout()
```

---

## 推荐配置

**优先顺序**:
1. Baostock (无需注册，先用)
2. Tushare Pro (稳定可靠，备用)
3. 聚宽 (功能强大，可选)

## 当前状态

- ⚠️ akshare: 网络问题，暂时不可用
- ✅ Baostock: 待测试
- ✅ Tushare Pro: 待配置

---

_更新时间：2026-04-03_
