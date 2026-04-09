# Vercel 项目批量清理脚本

**用途**: 批量删除 Vercel 冗余项目

## 前置条件

1. **获取 Vercel Token**:
   - 访问：https://vercel.com/account/tokens
   - 点击 "Create Token"
   - 复制 Token

2. **安装依赖**:
```bash
pip install requests
```

## 使用方法

```bash
# 1. 设置 Token
export VERCEL_TOKEN="your_token_here"

# 2. 运行脚本
python vercel_cleanup.py

# 3. 确认删除
# 脚本会列出所有匹配的项目
# 输入 y 确认删除，n 跳过
```

## 脚本逻辑

1. 获取所有项目
2. 筛选 `priceaction-` 或 `price-action-` 开头的项目
3. 列出所有匹配项目
4. 询问是否删除
5. 批量删除

---

**或者手动删除**（更简单）：

1. 访问：https://vercel.com/dashboard
2. 找到所有 `priceaction-xxx` 项目
3. 每个项目：
   - 点击进入
   - Settings → General
   - 滚动到底部
   - 点击 "Delete Project"
   - 输入项目名确认
4. 保留一个或全部删除
5. 重新 Import 部署

---

**推荐**: 手动删除更快（5-10 分钟）
