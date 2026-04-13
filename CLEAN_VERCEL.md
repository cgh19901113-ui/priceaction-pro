# Vercel 项目清理指南

## 清理步骤

### 步骤 1: 登录 Vercel Dashboard
访问: https://vercel.com/dashboard

### 步骤 2: 查看所有项目
在 Dashboard 首页，你会看到所有项目列表

### 步骤 3: 删除不需要的项目
对于每个要删除的项目:

1. 点击项目名称进入
2. 点击顶部 "Settings" 标签
3. 左侧菜单选择 "General"
4. 滚动到页面最底部
5. 找到 "Delete Project" 区域
6. 点击红色 "Delete Project" 按钮
7. 输入项目名称确认删除

### 步骤 4: 清理完成
删除后，项目数量会减少，腾出空间

## 快速清理命令 (Vercel CLI)

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 列出所有项目
vercel projects list

# 删除项目 (替换为实际项目名)
vercel projects delete 项目名称
```

## 保留项目建议

| 项目 | 建议 |
|------|------|
| priceaction-pro | ✅ 保留（裸K分析） |
| 其他旧项目 | ❌ 删除 |

## 清理后操作

1. 确认只剩 priceaction-pro 或空间充足
2. 访问部署链接重新导入
3. 或直接在 priceaction-pro 上重新部署

---

**请登录 https://vercel.com/dashboard 开始清理！**