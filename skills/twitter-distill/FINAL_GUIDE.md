# Twitter 数据收集 - 完整自动化方案

## 📦 已创建的文件

```
D:\Projects\price-action-saas\skills\twitter-distill/
├── main.py              # 主控制器（推荐）
├── run_auto.py          # 全自动收集器
├── setup_login.py       # 登录设置
├── run.bat              # Windows 一键脚本
├── crawler_auto.py      # 旧版自动收集
├── crawler_interactive.py # 交互式收集
├── import_data.py       # 手动导入
├── collect_nitter.py    # Nitter 版本
├── SKILL.md             # 技能说明
├── README_AUTO.md       # 自动化文档
└── USAGE.md             # 使用指南
```

---

## 🚀 一键自动化（推荐）

### 首次使用（需要登录一次）

```bash
cd D:\Projects\price-action-saas\skills\twitter-distill

# 运行主控制器（会自动引导登录）
python main.py
```

**流程**:
1. 检测登录状态
2. 未登录 → 打开浏览器让你登录 → 保存 Cookie
3. 已登录 → 直接开始收集

### 之后使用（完全自动）

```bash
# 一键完成：收集 + 导出 + 回测
python main.py
```

---

## 📊 目标数据量

| 博主 | 目标 | 预计时间 |
|------|------|----------|
| @Hoyooyoo | 1000 条 | 5 分钟 |
| @KillaXBT | 1000 条 | 8 分钟 |
| @Will_Yang_ | 1000 条 | 5 分钟 |
| @yekoikoi | 1000 条 | 5 分钟 |
| @0xtongcan | 1000 条 | 5 分钟 |
| @WallStreet0Name | 1000 条 | 5 分钟 |
| @CycleStudies | 1000 条 | 5 分钟 |
| @Mingarithm | 1000 条 | 5 分钟 |
| @Jingxin147741 | 1000 条 | 5 分钟 |
| @PAVLeader | 1000 条 | 5 分钟 |
| **总计** | **10000 条** | **~50 分钟** |

---

## 📁 输出文件

- `data/twitter/{username}.jsonl` - 每位博主的原始推文
- `strategy/twitter_recommendations.json` - 回测数据
- `progress.json` - 收集进度
- `browser_profile/` - 登录 Cookie（持久化）

---

## ⚡ 快速命令

```bash
# 完整流程（推荐）
python main.py

# 仅收集
python run_auto.py

# 仅导出
python run_auto.py --export

# 仅回测
python ..\..\strategy\backtest_twitter.py

# 查看进度
cat progress.json
```

---

## 🔧 故障排除

### 问题：提示未登录
```bash
python setup_login.py
```

### 问题：收集中断
```bash
# 直接重新运行，会自动跳过已收集的
python run_auto.py
```

### 问题：浏览器无法启动
```bash
# 重新安装 Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

---

## 📈 预期结果

收集完成后，回测会显示：
- 每位博主的荐股准确率
- 整体通过率
- 策略优化建议

**目标**: 识别出准确率>60% 的高质量博主，用于实盘参考

---

**大海，现在运行 `python main.py` 开始全自动收集！** 🚀
