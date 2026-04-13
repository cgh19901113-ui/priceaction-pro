#!/bin/bash
# PriceAction-SaaS 更新部署脚本
# 在现有项目上更新，不创建新项目

echo "=================================="
echo "PriceAction-SaaS 更新部署"
echo "=================================="

# 检查 Git 状态
echo ""
echo "[1/4] 检查 Git 状态..."
cd /mnt/d/Projects/price-action-saas
git status

# 提交修改
echo ""
echo "[2/4] 提交修改..."
git add .
git commit -m "fix: 移除UI标识 + 优化数据不足提示 + 代码优化"
git push

echo ""
echo "[3/4] 提交完成！"
echo "修改内容："
echo "  - 移除 frontend/index.html 中的 UI 标识"
echo "  - 优化 backend/main.py 中的数据不足提示"

echo ""
echo "[4/4] Vercel 自动部署中..."
echo "请访问 https://vercel.com/dashboard 查看部署状态"
echo ""
echo "=================================="
echo "部署完成！"
echo "=================================="
echo "网站地址: https://priceaction-pro.vercel.app"