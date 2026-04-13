# Twitter 数据收集 - 全自动流程

## 🚀 一次性设置（首次使用）

### 步骤 1: 登录 Twitter（只需一次）

```bash
cd D:\Projects\price-action-saas\skills\twitter-distill

# 运行登录设置
python setup_login.py
```

**操作**:
1. 浏览器打开，手动登录 Twitter
2. 登录成功后按 Enter
3. Cookie 会自动保存到 `browser_profile/`

---

## ⚡ 全自动收集（一键运行）

### 步骤 2: 运行全自动收集

```bash
# 收集所有 10 位博主（约 30-60 分钟）
python crawler_auto.py
```

**自动化流程**:
- ✅ 自动访问每位博主页面
- ✅ 自动滚动加载历史推文（最多 200 次/博主）
- ✅ 自动提取含股票的推文
- ✅ 自动去重保存
- ✅ 自动导出回测数据
- ✅ 自动运行回测

**目标**: 1000 条/博主 × 10 位 = **10000+ 条**

---

## 📊 查看进度

```bash
# 查看收集进度
cat progress.json
```

进度文件格式:
```json
{
  "last_updated": "2026-04-05T23:45:00",
  "results": {
    "Hoyooyoo": 856,
    "KillaXBT": 1234,
    ...
  }
}
```

---

## 📁 输出文件

| 文件 | 说明 |
|------|------|
| `data/twitter/{username}.jsonl` | 原始推文数据 |
| `strategy/twitter_recommendations.json` | 回测数据 |
| `progress.json` | 收集进度 |

---

## 🔄 增量更新

再次运行会自动跳过已收集的推文：

```bash
# 继续收集（增量更新）
python crawler_auto.py
```

---

## 📈 预期结果

| 博主 | 预计数量 | 收集时间 |
|------|----------|----------|
| @Hoyooyoo | 800-1200 | 5 分钟 |
| @KillaXBT | 1500-2000 | 8 分钟 |
| @Will_Yang_ | 500-800 | 3 分钟 |
| 其他 7 位 | 300-600 各 | 2-3 分钟各 |
| **总计** | **8000-12000** | **30-60 分钟** |

---

## 🎯 完整自动化命令

```bash
# 一条命令完成所有（首次需要先登录）
cd D:\Projects\price-action-saas\skills\twitter-distill

# 1. 登录（仅首次）
python setup_login.py

# 2. 全自动收集 + 导出 + 回测
python crawler_auto.py

# 3. 查看回测结果
python ..\..\strategy\backtest_twitter.py
```

---

## ⚠️ 注意事项

1. **首次必须手动登录**：之后 Cookie 保存，完全自动化
2. **网络稳定**：确保网络连接稳定，避免中断
3. **速率限制**：脚本已内置延迟，避免被封
4. **数据目录**：`data/twitter/` 会自动创建

---

## 🔧 故障排除

### 问题：提示未登录
```bash
# 重新登录
python setup_login.py
```

### 问题：收集中断
```bash
# 直接重新运行，会自动跳过已收集的
python crawler_auto.py
```

### 问题：数据太少
- 检查博主是否有足够的历史推文
- 增加 `max_scrolls` 参数（默认 200）

---

**大海，准备好就运行！** 🚀

```bash
python setup_login.py  # 首次
python crawler_auto.py # 全自动
```
