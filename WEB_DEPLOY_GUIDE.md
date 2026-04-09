# PriceAction-SaaS 网页部署指南

**版本**: v1.1  
**更新时间**: 2026-04-08 17:40  
**状态**: 🟢 支持网页部署

---

## 快速部署（网页版）

### 方式 1: 使用部署管理页面

1. **打开部署管理页面**
   ```
   打开文件：frontend/deploy.html
   ```

2. **获取 Vercel Token**
   - 访问：https://vercel.com/account/tokens
   - 点击 "Create Token"
   - 复制 Token

3. **填写配置**
   - Vercel Token: 粘贴刚才复制的 Token
   - Vercel Org ID: 在 Vercel Dashboard 查看
   - Vercel Project ID: 在 Vercel Dashboard 查看

4. **保存配置**
   - 点击 "保存配置" 按钮

5. **一键部署**
   - 点击 "部署到 Vercel" 按钮
   - 等待 2-5 分钟
   - 部署完成后访问：https://priceaction-pro.vercel.app

---

### 方式 2: 使用 Vercel Dashboard

1. **访问 Vercel**
   ```
   https://vercel.com
   ```

2. **登录/注册**
   - 使用 GitHub 登录（推荐）
   - 或使用邮箱注册

3. **导入项目**
   - 点击 "Add New Project"
   - 选择 "Import Git Repository"
   - 选择你的 GitHub 仓库

4. **配置项目**
   - Framework Preset: Python
   - Root Directory: `./`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: 留空

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成
   - 访问生成的 URL

---

### 方式 3: 使用 Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录 Vercel
vercel login

# 3. 进入项目目录
cd C:\Users\Administrator\.openclaw\workspace\projects\price-action-saas

# 4. 部署
vercel --prod
```

---

## 获取 Vercel 配置信息

### Vercel Token

1. 访问：https://vercel.com/account/tokens
2. 点击 "Create Token"
3. 输入 Token 名称（如：priceaction）
4. 选择权限（至少需要 "Deployments"）
5. 点击 "Create"
6. 复制 Token（只显示一次）

### Vercel Org ID

1. 访问：https://vercel.com/dashboard
2. 点击右上角头像
3. 选择 "Settings"
4. 在 "General" 页面找到 "Org ID"
5. 复制 Org ID

### Vercel Project ID

1. 访问：https://vercel.com/dashboard
2. 点击你的项目
3. 在 "Settings" → "General" 找到 "Project ID"
4. 复制 Project ID

---

## 部署后验证

### 1. 健康检查

```bash
curl https://priceaction-pro.vercel.app/api/health
```

**预期响应**:
```json
{"status": "healthy"}
```

### 2. 分析股票

```bash
curl "https://priceaction-pro.vercel.app/api/analyze?symbol=600519"
```

**预期响应**:
```json
{
  "success": true,
  "symbol": "600519",
  "analysis": {
    "大周期": "看涨",
    "大周期_颜色": "🟢",
    ...
  }
}
```

### 3. 访问前端

打开浏览器访问：
```
https://priceaction-pro.vercel.app
```

测试项:
- [ ] 页面加载正常
- [ ] 输入股票代码
- [ ] 点击分析按钮
- [ ] 显示分析结果
- [ ] 颜色标识正确

---

## 故障排查

### 问题 1: 部署失败

**症状**: Vercel 显示部署失败

**解决**:
1. 查看 Vercel Dashboard → Deployments → 查看日志
2. 检查 requirements.txt 是否完整
3. 确认 Python 版本为 3.12

### 问题 2: API 返回 500 错误

**症状**: 访问 API 返回 500 错误

**解决**:
1. 查看 Vercel Function Logs
2. 检查 Akshare 数据源是否可用
3. 添加错误日志

### 问题 3: 前端无法访问 API

**症状**: 前端显示网络错误

**解决**:
1. 检查 CORS 配置（已在 main.py 配置）
2. 检查 API 路由是否正确
3. 查看浏览器控制台错误

---

## 优化建议

### 性能优化

- [ ] 添加 Redis 缓存
- [ ] 优化 Akshare 请求
- [ ] 添加 CDN

### 安全优化

- [ ] 添加 Rate Limit
- [ ] 添加 API Key 验证
- [ ] 添加输入验证

### 监控优化

- [ ] 添加 Sentry 错误追踪
- [ ] 添加 Uptime Robot 监控
- [ ] 添加访问统计

---

## 快速链接

| 链接 | 说明 |
|------|------|
| [Vercel Dashboard](https://vercel.com/dashboard) | 管理部署 |
| [Vercel Tokens](https://vercel.com/account/tokens) | 获取 Token |
| [Vercel Docs](https://vercel.com/docs) | 官方文档 |
| [部署管理页面](frontend/deploy.html) | 网页部署工具 |

---

**创建时间**: 2026-04-08 17:40  
**最后更新**: 2026-04-08 17:40
