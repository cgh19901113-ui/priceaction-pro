# 错误与教训日志

## 2026-04-05

### 错误 1: 假设 snscrape 可以直接安装

**时间**: 22:39  
**影响**: 浪费时间尝试安装

**问题**:
```bash
pip install snscrape  # 失败
pip install git+https://github.com/JustAnotherArchivist/snscrape.git  # 也失败
```

**教训**:
- ✅ 先检查包的兼容性和依赖
- ✅ 在 Windows 环境下优先选择纯 Python 包
- ✅ 备选方案要提前准备

**改进**:
- 下次先搜索 "package_name windows installation"
- 查看 PyPI 页面的系统支持信息

---

### 错误 2: 高估 Nitter 可用性

**时间**: 22:45  
**影响**: 编写了完整的 Nitter 爬虫但无法使用

**问题**:
- 假设 Nitter 实例可以访问
- 没有提前测试连通性
- 写了 300+ 行代码（collect_nitter.py）但无法使用

**教训**:
- ✅ 先 ping/test 目标服务
- ✅ 不要假设第三方服务可用
- ✅ 快速验证可行性再深入开发

**改进**:
```python
# 应该先测试
import urllib.request
try:
    urllib.request.urlopen("https://nitter.net", timeout=5)
    print("Nitter accessible")
except:
    print("Nitter not accessible, skip this approach")
```

---

### 错误 3: 后台进程无法交互

**时间**: 23:30  
**影响**: setup_login.py 在后台运行时失败（EOFError）

**问题**:
```python
# 后台进程无法调用 input()
input("按 Enter 继续...")  # EOFError: EOF when reading a line
```

**教训**:
- ✅ 后台进程不能有交互式 input
- ✅ 需要自动检测代替人工确认
- ✅ 或者使用前台进程运行需要交互的脚本

**改进**:
```python
# 改为自动检测
for i in range(24):  # 2 分钟，每 5 秒检查
    time.sleep(5)
    if is_logged_in():  # 自动检测登录状态
        break
```

---

### 错误 4: 低估 Twitter 登录要求

**时间**: 23:40  
**影响**: 无法实现 100% 自动化

**问题**:
- 假设可以完全自动化（无需人工）
- 不知道 Twitter 注册需要手机验证
- 浏览器自动化需要 Cookie，Cookie 需要登录

**教训**:
- ✅ 提前调研目标平台的反爬机制
- ✅ 了解登录/注册流程的自动化难度
- ✅ 设定合理的自动化程度预期

**改进**:
- 接受"一次手动登录 + 永久自动化"的方案
- 或者寻找不需要登录的替代数据源

---

### 错误 5: RSS 方案数据量预估过于乐观

**时间**: 23:51  
**影响**: 收集到 2 条数据 vs 目标 10000 条

**问题**:
- 假设 RSS 能提供完整推文
- 不知道 Jina AI 只返回有限内容
- 没有提前测试数据量

**教训**:
- ✅ 先小规模测试（1 位博主）再批量运行
- ✅ 验证数据量是否满足需求
- ✅ 不要假设第三方服务的数据完整性

**改进**:
```python
# 应该先测试一位博主
test_user = "Hoyooyoo"
tweets = fetch_jina_twitter(test_user)
print(f"Found {len(tweets)} tweets")

if len(tweets) < 100:
    print("RSS data insufficient, need alternative approach")
```

---

## 总结的通用教训

### 1. 快速验证 > 完整实现
- 先用 5 分钟验证可行性
- 不要花 1 小时实现不可行的方案

### 2. 提前调研 > 盲目尝试
- 搜索 "twitter scraping 2026"
- 查看最新的技术方案和限制

### 3. 小步测试 > 批量运行
- 先测试 1 位博主
- 验证数据量、质量
- 再扩展到 10 位

### 4. 备选方案 > 单一依赖
- 始终准备 Plan B/C
- 当一个方案失败时快速切换

### 5. 记录过程 > 只做不说
- 详细记录每个尝试
- 方便回顾和分享
- 避免重复错误

---

## 正面经验（做对的）

### ✅ 及时创建学习笔记
- 避免遗忘细节
- 方便后续回顾
- 知识沉淀

### ✅ 多种方案并行探索
- 不把所有鸡蛋放一个篮子
- 快速切换方案

### ✅ 代码模块化
- 每个方案独立文件
- 方便测试和维护
- 可复用

### ✅ 数据持久化
- Cookie 保存
- 推文去重
- 进度跟踪

---

**最后更新**: 2026-04-05 23:54  
**教训数量**: 5 个错误 + 5 个通用教训 + 4 个正面经验
