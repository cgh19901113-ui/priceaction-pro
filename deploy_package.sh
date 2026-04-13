#!/bin/bash
# 部署包 - 在 Ubuntu 上执行

echo "=================================="
echo "PriceAction-SaaS 部署包"
echo "=================================="

# 创建部署目录
mkdir -p ~/deploy/priceaction-pro
cd ~/deploy/priceaction-pro

# 复制项目文件
cp -r /mnt/d/Projects/price-action-saas/* .

# 初始化 Git
git init
git add .
git commit -m "Initial commit: PriceAction-SaaS"

# 创建 Vercel 配置文件
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/index.html"
    }
  ]
}
EOF

# 创建 requirements.txt
cat > requirements.txt << 'EOF'
fastapi
uvicorn
pandas
numpy
akshare
tushare
EOF

echo ""
echo "=================================="
echo "部署包已创建: ~/deploy/priceaction-pro"
echo "=================================="
echo ""
echo "下一步:"
echo "1. 进入目录: cd ~/deploy/priceaction-pro"
echo "2. 安装 Vercel CLI: npm install -g vercel"
echo "3. 登录: vercel login"
echo "4. 部署: vercel --prod"
echo ""
echo "或使用 GitHub + Vercel 自动部署"