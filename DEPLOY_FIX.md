# PriceAction-SaaS 部署说明

## 问题诊断

### 500 错误原因

**根本原因**: 数据源连接问题

**当前状态**:
- ✅ 代码逻辑正确
- ✅ 策略引擎完整
- ❌ 数据源连接失败 (代理问题)

---

## 解决方案

### 方案 A: 使用 Tushare (推荐)

**优点**:
- 稳定可靠
- 不需要代理
- API 友好

**步骤**:
1. 注册 Tushare: https://tushare.pro/register
2. 获取 Token
3. 配置环境变量:
   ```
   TUSHARE_TOKEN=your_token_here
   ```

### 方案 B: 修复 Akshare 代理

**步骤**:
1. 检查代理配置: `netsh winhttp show proxy`
2. 重置代理: `netsh winhttp reset proxy`
3. 或直接连接 (中国境外)

### 方案 C: Vercel 部署

**Vercel 环境优势**:
- 无代理限制
- 可直接访问东方财富 API
- 自动部署

**步骤**:
1. 推送到 GitHub
2. Vercel Import 项目
3. 配置环境变量
4. 自动部署

---

## 环境变量配置

### 必需
```
# 无 (可选 Tushare)
```

### 可选 (推荐)
```
TUSHARE_TOKEN=your_tushare_token
```

### Vercel 配置
```
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
```

---

## 本地测试

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行测试
python test_api.py

# 3. 查看结果
# 如果显示 "获取到 XXX 条数据" 则成功
```

---

## 下一步

1. **立即**: 部署到 Vercel (无代理限制)
2. **短期**: 配置 Tushare Token
3. **长期**: 添加更多数据源

---

**创建时间**: 2026-04-09 22:45
**状态**: 代码完成，待部署验证
