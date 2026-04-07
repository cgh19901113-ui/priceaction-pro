# 免费国内数据源 - Baostock

## 为什么选择 Baostock？

### 优势
1. ✅ **完全免费** - 无需注册，无需 token
2. ✅ **数据完整** - A 股历史数据齐全
3. ✅ **国内访问** - 不需要代理，速度快
4. ✅ **数据准确** - 与前复权数据一致
5. ✅ **持续维护** - 活跃开源项目

### 对比其他数据源

| 数据源 | A 股完整性 | 成本 | 需要注册 | 国内访问 |
|--------|------------|------|----------|----------|
| **Baostock** | ✅ 完整 | **免费** | ❌ 不需要 | ✅ 快速 |
| Tushare Pro | ✅ 完整 | 积分制 | ✅ 需要 | ✅ 快速 |
| akshare | ✅ 完整 | 免费 | ❌ 不需要 | ⚠️ 可能被墙 |
| yfinance | ⚠️ 部分缺失 | 免费 | ❌ 不需要 | ⚠️ 慢/被墙 |

## 数据覆盖

### A 股
- 全部 A 股 (600/000/002/300 开头)
- 历史数据：上市至今
- 复权数据：前复权/后复权/不复权

### 指数
- 沪深 300 (000300)
- 上证指数 (000001)
- 深证成指 (399001)
- 创业板指 (399006)

### 港股
- 部分港股支持 (格式：HK.00700)

## 使用方法

### 获取个股历史数据
```python
import baostock as bs
import pandas as pd

# 登录
bs.login()

# 获取贵州茅台历史数据 (前复权)
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,open,high,low,close,volume",
    start_date='2025-01-01',
    end_date='2025-12-31',
    frequency="d",
    adjustflag="2"  # 前复权
)

# 解析结果
data_list = []
while (rs.error_code == '0') and rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# 登出
bs.logout()
```

### 获取指数数据
```python
# 沪深 300
rs = bs.query_history_k_data_plus(
    "sh.000300",
    "date,open,high,low,close,volume",
    start_date='2025-01-01',
    end_date='2025-12-31',
    frequency="d"
)
```

### 获取 15 分钟线
```python
# 15 分钟数据
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,time,open,high,low,close,volume",
    start_date='2025-01-01',
    end_date='2025-12-31',
    frequency="15",
    adjustflag="2"
)
```

## 代码格式

### 股票代码格式
- A 股：`sh.600519` 或 `sz.000001`
- 指数：`sh.000300`
- 港股：`HK.00700`

### 复权类型
- `adjustflag="1"` - 不复权
- `adjustflag="2"` - 前复权 (推荐)
- `adjustflag="3"` - 后复权

### 频率
- `d` - 日线
- `w` - 周线
- `m` - 月线
- `5` - 5 分钟
- `15` - 15 分钟
- `30` - 30 分钟
- `60` - 60 分钟

## 注意事项

1. **需要登录**: 使用前必须调用 `bs.login()`
2. **需要登出**: 使用完毕调用 `bs.logout()`
3. **港股支持有限**: 部分港股可能无法获取
4. **数据延迟**: 日线数据 T+1 更新
5. **网络要求**: 需要能访问 baostock 服务器

## 错误处理

```python
rs = bs.query_history_k_data_plus(...)

if rs.error_code != '0':
    print(f"Error: {rs.error_msg}")
    return None

data_list = []
while (rs.error_code == '0') and rs.next():
    data_list.append(rs.get_row_data())

if not data_list:
    print("No data")
    return None
```

## 安装

```bash
pip install baostock
```

## 官方资源

- GitHub: https://github.com/baostock/baostock
- 文档：http://baostock.com
- 论坛：http://baostock.com/bbs

---

_文档版本：v1.0_
_更新时间：2026-04-03_
