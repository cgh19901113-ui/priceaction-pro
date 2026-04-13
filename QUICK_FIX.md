# PriceAction-SaaS 快速修复指南

## ✅ 已完成修改

### 1. 移除 UI 标识
**文件**: `frontend/index.html`  
**修改**: 删除 "秋生 Trader(@Hoyooyoo)" 文字

### 2. 优化数据不足提示
**文件**: `backend/main.py`  
**修改**: 错误提示改为：
```
数据不足：该股票历史数据少于60个交易日。
请尝试：1) 主板股票如600519(茅台)、000001(平安银行)
      2) 避免新股或近期复牌股票
```

---

## 🚀 部署方案

### 方案 A：Vercel Dashboard 手动部署（推荐）
1. 打开 https://vercel.com/dashboard
2. 找到 price-action-saas 项目
3. 点击 "Deploy" 或上传修改后的文件

### 方案 B：安装 Git 后提交
1. 下载 Git: https://git-scm.com/download/win
2. 安装时勾选 "Add to PATH"
3. 打开新 PowerShell：
```powershell
cd D:\Projects\price-action-saas
git add .
git commit -m "fix: 移除UI标识 + 优化数据不足提示"
git push
```

### 方案 C：使用 deploy.bat
1. 安装 Git
2. 双击运行 `deploy.bat`

---

## 📁 修改文件清单

| 文件 | 状态 |
|------|------|
| frontend/index.html | ✅ 已修改 |
| backend/main.py | ✅ 已修改 |
| deploy.bat | ✅ 已创建 |
| QUICK_FIX.md | ✅ 本文件 |

---

## ⚠️ 注意事项

- 修改已保存到本地文件
- 需要部署后才能生效
- 网站 URL: https://priceaction-pro.vercel.app

---

**修改时间**: 2026-04-12 20:10  
**修改者**: glm-5