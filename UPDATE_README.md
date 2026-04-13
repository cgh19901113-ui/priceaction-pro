# PriceAction-SaaS 更新部署说明

## 原则
✅ 在现有项目上更新，不创建新项目

## 更新步骤

### 方法 1: 运行批处理脚本（推荐）

1. 双击运行 `update_and_deploy.bat`
2. 自动完成 Git 提交和推送
3. Vercel 自动部署更新

### 方法 2: 手动执行

打开 PowerShell：
```powershell
cd D:\Projects\price-action-saas
git add .
git commit -m "fix: 移除UI标识 + 优化数据不足提示"
git push
```

### 方法 3: Vercel Dashboard 手动更新

1. 访问 https://vercel.com/dashboard
2. 点击 priceaction-pro 项目
3. 点击 "Deployments"
4. 点击 "Redeploy"

## 已完成的修改

| 文件 | 修改内容 |
|------|----------|
| frontend/index.html | 移除 "秋生 Trader(@Hoyooyoo)" 标识 |
| backend/main.py | 优化数据不足提示，增加建议 |

## 验证部署

部署完成后访问：
https://priceaction-pro.vercel.app

检查：
- [ ] 页面底部无 UI 标识
- [ ] 输入新股时显示优化后的错误提示

---

**请运行 update_and_deploy.bat 完成更新！**