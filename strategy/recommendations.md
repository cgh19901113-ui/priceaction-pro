# 回测验证 - 秋生 Trader (@Hoyooyoo) 推荐股票

**策略版本**: v3.0
**持有期**: 3 天
**达标收益**: 5%

---

## 📝 收集方法

1. 访问原博 Twitter: https://twitter.com/Hoyooyoo
2. 搜索关键词："起涨点"、"有点东西"、"观察池"
3. 记录推荐过的股票和日期
4. 填充下方列表

---

## 📊 推荐股票列表

**格式**: `{symbol: 股票代码，date: 推荐日期 YYYY-MM-DD，note: 备注}`

```python
RECOMMENDATIONS = [
    # 示例数据 (替换为真实推荐)
    {"symbol": "600519.ss", "date": "2026-03-01", "note": "示例"},
    {"symbol": "000858.sz", "date": "2026-03-05", "note": "示例"},
    
    # 在此处添加真实推荐...
    # {"symbol": "股票代码", "date": "YYYY-MM-DD", "note": "原博备注"},
]
```

---

## 🎯 回测目标

| 指标 | 目标值 |
|------|--------|
| 通过率 | >60% (符合观察池标准) |
| 准确率 | >70% (通过后 3 天涨幅>5%) |
| 假信号率 | <30% (通过后下跌) |

---

## 🔧 参数微调

如果准确率不达标，调整以下参数：

### 趋势持续确认条件
```python
TREND_CONFIRM_CONSECUTIVE_GREEN = 2  # 连续阳线数量 (2-3)
TREND_CONFIRM_VOL_RATIO = 1.2  # 放量倍数 (1.2-1.5)
```

### 大盘对比周期
```python
MARKET_COMPARE_PERIOD = 10  # 10 或 20 日
```

### 过滤阈值
```python
SCORE_PASS_THRESHOLD = 70  # 通过分数线 (60-80)
```

---

## 📈 运行步骤

1. 填充上方 RECOMMENDATIONS 列表
2. 运行回测脚本:
   ```bash
   cd C:/Users/Administrator/.openclaw/workspace/projects/price-action-saas
   python strategy/backtest.py
   ```
3. 查看输出结果
4. 根据结果微调参数
5. 重复测试直到达标

---

## ⚠️ 注意事项

1. **数据质量**: yfinance 的 A 股数据可能有延迟，建议用复权数据
2. **日期匹配**: 推荐日期必须是交易日
3. **样本数量**: 至少 20 只股票才有统计意义
4. **持有期**: 可调整 HOLD_DAYS (3/5/10 天)

---

_创建时间：2026-04-03_
