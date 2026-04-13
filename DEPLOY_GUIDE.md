# PriceAction-SaaS Vercel 部署指南

## 部署链接
https://vercel.com/new/import?framework=fastapi&hasTrialAvailable=1&id=1203449776&name=priceaction-pro&owner=cgh19901113-ui&project-name=priceaction-pro&provider=github&remainingProjects=1&s=https%3A%2F%2Fgithub.com%2Fcgh19901113-ui%2Fpriceaction-pro&teamSlug=roots-projects-3b52feb2&totalProjects=1

## 部署步骤

### 步骤 1: 打开链接
点击上述链接，进入 Vercel 导入页面

### 步骤 2: 配置项目
- **Framework**: FastAPI (已自动选择)
- **Project Name**: priceaction-pro
- **Root Directory**: ./

### 步骤 3: 环境变量
添加以下环境变量：
```
TUSHARE_TOKEN=你的Tushare Token
```

### 步骤 4: 点击 Deploy
等待部署完成

## 部署前检查

### 已修改文件 ✅
- `frontend/index.html` - 移除UI标识
- `backend/main.py` - 优化错误提示

### 需要提交到 Git
```bash
cd D:\Projects\price-action-saas
git add .
git commit -m "fix: 移除UI标识 + 优化数据不足提示"
git push
```

## 部署后验证

1. 访问部署后的 URL
2. 测试股票分析功能
3. 确认UI标识已移除
4. 确认错误提示已优化

## 备选方案

如果自动导入失败，可以：
1. 手动上传文件到 Vercel
2. 使用 Vercel CLI 部署
3. 重新创建项目

---

**请先执行 Git 提交，然后点击部署链接！**