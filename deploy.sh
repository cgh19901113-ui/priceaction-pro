#!/bin/bash
# PriceAction-SaaS 快速部署脚本
# 用途：一键部署到 Vercel

echo "======================================"
echo "PriceAction-SaaS 快速部署脚本"
echo "======================================"
echo ""

# 检查 Python
echo "🔍 检查 Python..."
python --version || {
    echo "❌ Python 未安装，请先安装 Python 3.12"
    exit 1
}
echo "✅ Python 检查通过"
echo ""

# 检查依赖
echo "📦 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi

pip install -r requirements.txt -q || {
    echo "❌ 依赖安装失败"
    exit 1
}
echo "✅ 依赖安装完成"
echo ""

# 测试后端
echo "🧪 测试后端..."
cd backend
python -c "import main; print('Backend OK')" || {
    echo "❌ 后端测试失败"
    cd ..
    exit 1
}
cd ..
echo "✅ 后端测试通过"
echo ""

# 检查 Vercel CLI
echo "🔍 检查 Vercel CLI..."
vercel --version || {
    echo "⚠️  Vercel CLI 未安装，正在安装..."
    npm i -g vercel
}
echo "✅ Vercel CLI 检查通过"
echo ""

# 登录 Vercel
echo "🔑 登录 Vercel..."
vercel whoami || {
    echo "⚠️  未登录 Vercel，正在登录..."
    vercel login
}
echo "✅ Vercel 登录完成"
echo ""

# 部署
echo "🚀 开始部署到 Vercel..."
vercel --prod || {
    echo "❌ 部署失败"
    exit 1
}
echo ""
echo "✅ 部署完成！"
echo ""
echo "======================================"
echo "部署成功！"
echo "======================================"
echo ""
echo "下一步:"
echo "1. 访问生产 URL"
echo "2. 测试 API: /api/analyze?symbol=600519"
echo "3. 检查 Vercel Dashboard"
echo ""
