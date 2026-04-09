# PriceAction-SaaS 部署检查清单

**版本**: v1.1  
**更新时间**: 2026-04-08 17:30  
**状态**: 🟡 待部署验证

---

## 一、部署前检查

### 1.1 代码检查

- [x] ✅ 后端代码优化 (添加错误处理)
- [x] ✅ 当前信号逻辑优化 (动态生成)
- [x] ✅ 前端 UI 完整
- [x] ✅ vercel.json 配置更新
- [x] ✅ GitHub Actions 配置更新

### 1.2 依赖检查

```bash
# 检查 requirements.txt
cat requirements.txt

# 应包含:
# fastapi
# uvicorn
# pandas
# numpy
# akshare
```

**状态**: ✅ 完整

### 1.3 本地测试

```bash
# 1. 安装依赖
cd C:\Users\Administrator\.openclaw\workspace\projects\price-action-saas
pip install -r requirements.txt

# 2. 测试后端
cd backend
python -c "import main; print('Backend OK')"

# 3. 运行本地服务
uvicorn main:app --reload

# 4. 测试 API
curl http://localhost:8000/api/analyze?symbol=600519
```

**状态**: ⏳ 待测试

---

## 二、Vercel 部署

### 2.1 部署步骤

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

### 2.2 环境变量配置

在 Vercel Dashboard 配置：
- `VERCEL_TOKEN` - Vercel API Token
- `VERCEL_ORG_ID` - 组织 ID
- `VERCEL_PROJECT_ID` - 项目 ID

### 2.3 部署验证

```bash
# 访问生产 URL
curl https://priceaction-pro.vercel.app/api/health

# 应返回:
# {"status": "healthy"}
```

---

## 三、GitHub 集成

### 3.1 配置 Secrets

在 GitHub Repository Settings → Secrets and variables → Actions:

- `VERCEL_TOKEN`: Vercel API Token
- `VERCEL_ORG_ID`: 组织 ID
- `VERCEL_PROJECT_ID`: 项目 ID

### 3.2 推送代码

```bash
# 1. 初始化 Git (如果未初始化)
git init
git add .
git commit -m "PriceAction-SaaS v1.1 - 优化部署和错误处理"

# 2. 推送到 main 分支
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

### 3.3 自动部署

推送后 GitHub Actions 会自动：
1. 安装 Python 3.12
2. 安装依赖
3. 测试后端
4. 部署到 Vercel

---

## 四、部署后验证

### 4.1 API 测试

```bash
# 1. 健康检查
curl https://priceaction-pro.vercel.app/api/health

# 2. 分析股票
curl "https://priceaction-pro.vercel.app/api/analyze?symbol=600519"

# 3. 错误处理测试
curl "https://priceaction-pro.vercel.app/api/analyze?symbol=invalid"
```

### 4.2 前端测试

访问：https://priceaction-pro.vercel.app

测试项:
- [ ] 页面加载正常
- [ ] 输入股票代码
- [ ] 点击分析按钮
- [ ] 显示分析结果
- [ ] 颜色标识正确
- [ ] 响应式设计正常

### 4.3 性能测试

```bash
# 使用 curl 测试响应时间
time curl https://priceaction-pro.vercel.app/api/analyze?symbol=600519

# 目标：< 2 秒
```

---

## 五、问题排查

### 5.1 常见问题

**问题 1**: 部署失败

```bash
# 查看 Vercel 日志
vercel logs <deployment-url>
```

**问题 2**: API 返回 500 错误

- 检查 Akshare 数据源
- 查看 Vercel Function Logs
- 添加错误日志

**问题 3**: 前端无法访问 API

- 检查 CORS 配置
- 检查 API 路由
- 查看浏览器控制台

### 5.2 Vercel Dashboard

访问：https://vercel.com/dashboard

检查项:
- [ ] 部署状态
- [ ] Function Logs
- [ ] 错误报告
- [ ] 性能指标

---

## 六、优化建议

### 6.1 性能优化

- [ ] 添加 Redis 缓存 (热门股票)
- [ ] 优化 Akshare 请求 (批量获取)
- [ ] 添加 CDN (静态资源)

### 6.2 安全优化

- [ ] 添加 Rate Limit
- [ ] 添加 API Key 验证
- [ ] 添加输入验证

### 6.3 监控优化

- [ ] 添加 Sentry 错误追踪
- [ ] 添加 Uptime Robot 监控
- [ ] 添加访问统计

---

## 七、回滚方案

### 7.1 Vercel 回滚

```bash
# 查看历史部署
vercel ls

# 回滚到上一个版本
vercel rollback <deployment-url>
```

### 7.2 GitHub 回滚

```bash
# 回滚 commit
git revert <commit-hash>
git push origin main
```

---

## 八、部署状态

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 代码优化 | ✅ | 已完成 |
| vercel.json | ✅ | 已更新 |
| GitHub Actions | ✅ | 已更新 |
| 本地测试 | ⏳ | 待测试 |
| Vercel 部署 | ⏳ | 待部署 |
| API 验证 | ⏳ | 待验证 |
| 前端测试 | ⏳ | 待测试 |

**整体状态**: 🟡 **准备部署**

---

**创建时间**: 2026-04-08 17:30  
**下次检查**: 部署完成后
